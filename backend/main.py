from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse
import logging
from typing import List, Dict, Optional, Any, Tuple, List

# Core Imports
from core.ledger import LedgerManager
from core.inventory import InventoryManager
from core.progression import ProgressionManager
from core.ids import IDGenerator
from core.state import UserStateManager
from core.models import GameOffer
from miners.epic import EpicMiner
from miners.steam import SteamMiner
from miners.scout import Scout

from pathlib import Path

# ... (imports)

app = FastAPI(title="ZeroCrate Ops")

# Resolve Paths relative to THIS file (backend/main.py)
BASE_DIR = Path(__file__).resolve().parent

# Mounts
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# System State (Persistent Managers)
ledger = LedgerManager()
inventory = InventoryManager()
progression = ProgressionManager(ledger)
user_state = UserStateManager()
miners = [EpicMiner(), SteamMiner(), Scout()]

# Cache for fast lookups
# canonical_id -> GameOffer
loot_cache: Dict[str, GameOffer] = {}

# Current Rails Snapshot (for /api/state)
latest_rails = {
    "new_finds": [],     # Unopened
    "opened_history": [], # Opened
    "high_value": [],
    "ending_soon": [],
    "mystery": []
}

# --- Phase 12: Cinematic UI State Logic ---

def parse_end_time_hours(end_time_rel: object) -> float:
    """Parses a relative time string (or object) into hours."""
    # If it's already a float/int (timestamp), logic would be different, 
    # but currently models.py says Optional[object]. 
    # Miners populating strings like "Ends in X" or datetimes.
    # For fail-safety, we treat high for unknown.
    if not end_time_rel:
        return float('inf')
    
    s = str(end_time_rel).lower()
    if "permanent" in s:
        return float('inf')
    
    # Simple heuristic parser for strings like "Ends in 2d" or "18h"
    try:
        if "ends in" in s:
            parts = s.split("ends in")[-1].strip().split()
            val = float(parts[0].replace('d', '').replace('h', ''))
            unit = parts[0][-1] if parts[0][-1] in ['d', 'h'] else parts[1] if len(parts)>1 else 'h'
            
            if 'd' in unit: return val * 24
            if 'h' in unit: return val
    except:
        pass
    
    return float('inf')

def calculate_hero_state() -> Dict[str, Any]:
    """
    DERIVED TRUTH: Collection Value comes from the Inventory Ledger.
    We do NOT verify against live loot_cache because history persists.
    """
    total_val = inventory.get_total_value()
    # Get basic stats
    stats = progression.get_player_stats("default_user")
    
    # Calculated Fields
    level = stats["level"]
    # Simple Title Logic
    titles = {1: "Scavenger", 2: "Tracker", 3: "Hunter", 4: "Ranger", 5: "Legend"}
    title = titles.get(level, "Scavenger")
    
    return {
        "collection_value": round(total_val, 2),
        "level": level,
        "level_title": title, 
        "streak": stats['streak'].get('message', 'Inactive')
    }

def calculate_rails() -> List[Dict[str, Any]]:
    """
    Constructs the 5 Canonical Rails based on Phase 12 Rules.
    Sources:
    - Active Items: loot_cache (filtered by unopened)
    - History: inventory (persisted opens)
    """
    opened_ids = user_state.get_opened_set("default_user")
    
    # 1. Unopened Active Offers (The Hunt)
    unopened_active = [
        offer for cid, offer in loot_cache.items() 
        if cid not in opened_ids
    ]
    
    # Helper for serializing GameOffer to JSON-friendly dict
    def serialize(o: GameOffer):
        # Generate a stable hue for the fallback gradient based on title
        # This ensures every game has a unique "identity" even without art
        title_hash = sum(ord(c) for c in o.title)
        hue = title_hash % 360
        
        return {
            "id": str(o.platform_id or "unknown"), 
            "title": o.title,
            "platform": o.source,
            "cover_image_url": o.image_url, 
            "fallback_hue": hue, # New field for CSS
            "original_price": o.original_price,
            "is_free_now": o.is_free_now,
            "end_time_rel": str(o.end_time) if o.end_time else None,
            "rating": o.rarity.value if hasattr(o.rarity, 'value') else str(o.rarity),
            "offer_type": "Mystery" if "mystery" in o.title.lower() else "BaseGame", 
            "url": o.store_url,
            "opened": False
        }

    # Helpers for Phase 18 Sorting/Normalization
    def normalize_platform(o: GameOffer) -> Tuple[str, str]:
        # Priority: platform field -> source field -> ID prefixes
        raw = (o.source or "").lower()
        if "steam" in raw: return "steam", "On Steam"
        if "epic" in raw: return "epic", "Epic Games"
        if "gog" in raw: return "gog", "GOG"
        return "unknown", "Other Sources"

    def get_end_hours(o: GameOffer) -> float:
        if not o.end_time: return float('inf')
        return parse_end_time_hours(o.end_time)

    # Buckets
    hero_items = []
    steam_items = []
    epic_items = []
    gog_items = []
    mystery_items = []

    # Iterate & Classify
    for o in unopened_active:
        # Strict Mystery Check
        is_mystery = getattr(o, 'offer_type', 'BaseGame') == 'Mystery' or "mystery" in o.title.lower() # Fallback for now until model updated
        if is_mystery:
            mystery_items.append(o)
            continue # Mystery items don't go into platform/hero rails

        # Platform Bucket
        key, label = normalize_platform(o)
        if key == "steam": steam_items.append(o)
        elif key == "epic": epic_items.append(o)
        elif key == "gog": gog_items.append(o)
        
        # Hero Check (Free or Urgent)
        hours = get_end_hours(o)
        if o.is_free_now or hours <= 24:
            hero_items.append(o)

    # Sorting Helper (Canonical Sort)
    # Key: (not Free, EndHours IF Free ELSE Inf, -Value, Title)
    def sort_key(o):
        hours = get_end_hours(o)
        return (
            not o.is_free_now, 
            hours if o.is_free_now else float('inf'), 
            -o.original_price, 
            o.title
        )

    hero_items.sort(key=sort_key)
    steam_items.sort(key=sort_key)
    epic_items.sort(key=sort_key)
    gog_items.sort(key=sort_key)
    # Mystery sorted by ID/Arbitrary for now
    
    # History Rail
    history_loot = inventory.get_history()
    history_items_serialized = []
    for item in history_loot:
        s = serialize(item)
        s['opened'] = True
        history_items_serialized.append(s)
    history_items_serialized.reverse()

    # Empty State Logic
    scout_active = True # We assume active for now, or check generic state
    def get_empty_msg(title: str) -> str:
        if not scout_active: return "Scout is scanning..."
        return f"No offers on {title} right now."

    # Construct Rails
    rails_struct = [
        {"id": "hero_miss", "title": "You Don't Want to Miss", "cards": [serialize(o) for o in hero_items], "empty_message": "No urgent deals found."},
        {"id": "steam", "title": "On Steam", "cards": [serialize(o) for o in steam_items], "empty_message": get_empty_msg("Steam")},
        {"id": "epic", "title": "Epic Games", "cards": [serialize(o) for o in epic_items], "empty_message": get_empty_msg("Epic Games")},
        {"id": "gog", "title": "GOG", "cards": [serialize(o) for o in gog_items], "empty_message": get_empty_msg("GOG")},
        {"id": "mystery", "title": "Mystery Loot", "cards": [serialize(o) for o in mystery_items], "empty_message": "The vault is empty."},
        {"id": "history", "title": "History / Collected", "cards": history_items_serialized, "empty_message": "Your collection is empty."},
    ]
    
    return rails_struct

def get_full_state() -> Dict[str, Any]:
    """Constructs the Phase 12 Data Contract."""
    return {
        "scout": {
            "status": "watching", # Mock for now, could check thread
            "last_discovery_age": "Just now"
        },
        "hero": calculate_hero_state(),
        "rails": calculate_rails()
    }

# --- API Routes ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """SSR: Renders initial state via Jinja."""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "state": get_full_state()}
    )

@app.get("/api/state")
async def get_state_json():
    """Client-side sync."""
    return get_full_state()

@app.post("/api/open/{offer_id}")
async def open_offer(offer_id: str):
    """
    Idempotent Open Action.
    1. Guard: Check existence, URL, Mystery.
    2. Logic: Add to Inventory (Ledger).
    3. Return: Updated State.
    """
    # 1. Find Offer (Check loot_cache first)
    offer = loot_cache.get(offer_id)
    
    # If not in loot cache, check if already in inventory?
    # If in inventory, it's already opened.
    if user_state.has_opened("default_user", offer_id):
         return {
            "already_opened": True,
            "state": get_full_state()
        }

    if not offer:
        raise HTTPException(status_code=404, detail="Offer lost from cache")
        
    # 2. Guards
    if "mystery" in offer.title.lower():
        raise HTTPException(status_code=409, detail="Mystery signal locked")
    
    if not offer.store_url:
        raise HTTPException(status_code=422, detail="Signal has no coordinates (URL)")

    # 3. State Change (Ledger First)
    # Add to inventory (persists to disk)
    inventory.add_loot(offer)
    # Mark user state (persists to sqlite)
    user_state.mark_opened("default_user", offer_id)
    # Mint XP
    progression.add_xp("default_user", 100, f"Secured {offer.title}")

    # 4. Return Full State (Simplest Sync)
    return {
        "already_opened": False,
        "state": get_full_state()
    }

@app.get("/api/why/{offer_id}")
async def get_why(offer_id: str):
    if offer_id not in loot_cache:
        return {"reason": "Unknown Signal"}
    item = loot_cache[offer_id]
    return {
        "reason": f"Detected by {item.source}",
        "confidence": "High",
        "original_price": item.original_price
    }

def run_miners_task():
    """Background task to run miners and update state."""
    global loot_cache
    print("📡 SCANNING FREQUENCIES...")
    scanned_loot = []
    
    # 1. Mine
    for miner in miners:
        try:
            scanned_loot.extend(miner.fetch_games())
        except Exception as e:
            print(f"❌ Error mining {miner.name}: {e}")

    # 2. Process & Cache
    # We update the global cache and Canonical IDs
    for item in scanned_loot:
        if not item.platform_id:
            continue # Skip invalid items
            
        canonical_id = IDGenerator.claim(item.source, item.platform_id)
        loot_cache[canonical_id] = item
        
        # Also ensure it's in the persistent 'Inventory' (Legacy/Backup layer)
        # We assume Inventory checks dict keys, but here we just blindly 'claim' to save it.
        # Ideally inventory should accept the CANONICAL ID now. 
        # For now, we use the old method to persist the data to json.
        inventory.claim_loot([item]) 
        
    print(f"✅ SCAN COMPLETE. Cache Updated with {len(scanned_loot)} signals.")

@app.on_event("startup")
async def startup_event():
    """Ignition Sequence: Start mining immediately."""
    import threading
    # Run in a separate thread so we don't block startup
    t = threading.Thread(target=run_miners_task)
    t.daemon = True
    t.start()
    print("🚀 SYSTEM IGNITION: Miners deployed automatically.")

@app.post("/api/scan")
async def trigger_scan(background_tasks: BackgroundTasks):
    """Triggers a scan in the background."""
    background_tasks.add_task(run_miners_task)
    return {"status": "scanning", "message": "Miners deployed..."}
