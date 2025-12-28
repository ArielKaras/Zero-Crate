"""
tests/verify_phase8.py
Verification for Phase 8: Discovery Library Architecture
"""

import sys
import os
import shutil
from fastapi.testclient import TestClient

# Add root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ids import IDGenerator
from core.state import UserStateManager
from core.models import GameOffer, Rarity
from web.main import app, loot_cache

# Setup Clean Environment
TEST_STATE_DB = "data/user_state.db"
if os.path.exists(TEST_STATE_DB):
    os.remove(TEST_STATE_DB)

client = TestClient(app)

def test_canonical_ids():
    print("\n🔹 Testing Canonical IDs...")
    
    # 1. Steam
    steam_id = IDGenerator.claim("Steam", "12345")
    assert steam_id == "claim:steam:12345"
    print("✅ Steam ID Generation: OK")
    
    # 2. Scout
    scout_id = IDGenerator.claim("Steam (Scout)", "scout_steam_deadbeef")
    assert scout_id == "claim:steam (scout):scout_steam_deadbeef"
    print("✅ Scout ID Generation: OK")

def test_user_state_manager():
    print("\n🔹 Testing UserStateManager...")
    sm = UserStateManager()
    user = "test_user"
    offer = "claim:steam:999"
    
    # 1. First Open
    res = sm.mark_opened(user, offer)
    assert res['status'] == "success"
    print("✅ First Open: Success")
    
    # 2. Duplicate Open
    res = sm.mark_opened(user, offer)
    assert res['status'] == "already_opened"
    print("✅ Duplicate Open: Rejected (Idempotent)")
    
    # 3. Set Retrieval
    opened = sm.get_opened_set(user)
    assert offer in opened
    print("✅ Set Retrieval: OK")

def test_api_atomic_flow():
    print("\n🔹 Testing API Atomicity (POST /api/open)...")
    
    # Setup Mock Cache
    offer_id = "claim:epic:test_offer"
    loot_cache[offer_id] = GameOffer(
        title="Test Game",
        original_price=59.99,
        discount_price=0,
        description="Test description",
        image_url="",
        store_url="http://epic.com",
        source="Epic",
        platform_id="test_offer",
        rarity=Rarity.LEGENDARY
    )
    
    # 1. First Call (Should Mint)
    res = client.post(f"/api/open/{offer_id}")
    data = res.json()
    assert res.status_code == 200
    assert data['status'] == "success"
    print("✅ API First Call: Minted XP")
    
    # 2. Second Call (Should NOT Mint, but return success/already_opened)
    res = client.post(f"/api/open/{offer_id}")
    data = res.json()
    assert res.status_code == 200
    assert data['status'] == "already_opened"
    print("✅ API Second Call: Idempotent")

def main():
    print("🧪 Starting Phase 8 Verification...")
    try:
        test_canonical_ids()
        test_user_state_manager()
        test_api_atomic_flow()
        print("\n🏆 PHASE 8 VERIFICATION PASSED. SYSTEM STABLE.")
    except AssertionError as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ RUNTIME ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
