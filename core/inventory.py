import json
import os
from typing import List, Dict
from datetime import datetime
from core.models import GameOffer

INVENTORY_FILE = "inventory.json"

class InventoryManager:
    def __init__(self):
        self.inventory = self._load_inventory()

    def _load_inventory(self) -> Dict[str, dict]:
        if not os.path.exists(INVENTORY_FILE):
            return {}
        try:
            with open(INVENTORY_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def _save_inventory(self):
        with open(INVENTORY_FILE, 'w') as f:
            json.dump(self.inventory, f, indent=4)

    def filter_new_loot(self, loot: List[GameOffer]) -> List[GameOffer]:
        """Returns only the items that haven't been claimed yet."""
        new_items = []
        for item in loot:
            # key by title for now; store_url or ID would be safer long term
            if item.title not in self.inventory:
                new_items.append(item)
        return new_items

    def claim_loot(self, loot: List[GameOffer]):
        """Adds new items to the inventory."""
        for item in loot:
            if item.title not in self.inventory:
                self.inventory[item.title] = {
                    "title": item.title,
                    "claimed_at": datetime.now().isoformat(),
                    "rarity": item.rarity.value if hasattr(item.rarity, 'value') else str(item.rarity),
                    "savings": item.original_price,
                    "source": item.source,
                    "store_url": item.store_url,
                    "cover_image_url": item.image_url,
                    "platform_id": item.platform_id
                }
        self._save_inventory()

    def add_loot(self, item: GameOffer):
        """Single item alias."""
        self.claim_loot([item])

    def get_history(self) -> List[GameOffer]:
        """Returns inventory as GameOffer objects."""
        offers = []
        from core.models import Rarity 
        
        for data in self.inventory.values():
            # Rehydrate (Best Effort)
            # Defaulting missing fields to None/Safe values
            o = GameOffer(
                title=data.get('title', 'Unknown'),
                original_price=data.get('savings', 0.0),
                discount_price=0.0, # Required field, default 0
                description="", # Required field
                source=data.get('source', 'System'),
                store_url=data.get('store_url', ''), # Required str
                image_url=data.get('cover_image_url', ''), # Required str
                platform_id=data.get('platform_id'),
                rarity=Rarity.COMMON # Default, fine for history
            )
            # We assume history items are 'opened' logic-side, 
            # but GameOffer doesn't track that.
            offers.append(o)
        return offers

    def get_all_loot(self) -> List[dict]:
        """Returns list of dicts for UI display."""
        return list(self.inventory.values())

    def get_total_value(self) -> float:
        """Calculates total market value saved."""
        total = 0.0
        for item in self.inventory.values():
            total += item.get('savings', 0)
        return total
