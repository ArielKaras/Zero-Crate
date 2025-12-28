import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ledger import LedgerManager
from core.progression import ProgressionManager
from datetime import datetime, timedelta
import uuid

def run_checks():
    print("🏦 Starting Economic Integrity Checks...\n")
    
    # Use a temporary test database
    TEST_DB = "data/test_economy.db"
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
        
    ledger = LedgerManager(db_path=TEST_DB)
    progression = ProgressionManager(ledger)
    user_id = "test_user"

    # ==========================================
    # CHECK A: IDEMPOTENCY
    # ==========================================
    print("🔹 Check A: Idempotency under reruns")
    ref_id = "claim:steam:test_game_123"
    
    # 1st Run
    res1 = ledger.add_transaction(user_id, 100, "EARN", ref_id)
    print(f"  - Run 1: {res1['status']} (Expected: success)")
    
    # 2nd Run (Duplicate)
    res2 = ledger.add_transaction(user_id, 100, "EARN", ref_id)
    print(f"  - Run 2: {res2['status']} (Expected: skipped)")
    
    balance = ledger.get_balance(user_id)
    if balance == 100 and res2['status'] == "skipped":
        print("  ✅ PASS: Idempotency holds. Balance is 100.")
    else:
        print(f"  ❌ FAIL: Balance is {balance}")

    print("")

    # ==========================================
    # CHECK B: LEVEL INVARIANCE
    # ==========================================
    print("🔹 Check B: Level Invariance (Spending vs Lifetime)")
    # Current: 100 XP. Level = sqrt(100/100) = 1.
    # Add 800 XP -> Total 900. Level = sqrt(900/100) = 3.
    
    ledger.add_transaction(user_id, 800, "EARN", "bonus:level_jump")
    lv_before = progression.get_level(user_id)
    print(f"  - Level after earning: {lv_before} (Expected: 3)")
    
    # Spend 500 XP (Balance goes 900 -> 400)
    # Lifetime Earned should stay 900. Level should stay 3.
    ledger.add_transaction(user_id, -500, "REDEEM", "redeem:test_item")
    
    lv_after = progression.get_level(user_id)
    balance_after = ledger.get_balance(user_id)
    
    print(f"  - Balance after spend: {balance_after} (Expected: 400)")
    print(f"  - Level after spend: {lv_after} (Expected: 3)")
    
    if lv_after == 3 and balance_after == 400:
        print("  ✅ PASS: Level did not decrease.")
    else:
        print("  ❌ FAIL: Level dropped or math error.")

    print("")

    # ==========================================
    # CHECK C: STREAK LOGIC
    # ==========================================
    print("🔹 Check C: Streak Edge-Cases")
    
    # Reset User for clean streak test
    streak_user = "streak_tester"
    
    # Event 1: T (40 hours ago)
    t0 = datetime.utcnow() - timedelta(hours=40)
    ledger.add_transaction(streak_user, 100, "EARN", "streak:day1", created_at=t0)
    
    # Check Status (Should be Active)
    s1 = progression.get_streak_status(streak_user)
    print(f"  - T-40h Status: {s1['active']} (Expected: True)")
    
    if s1['active']:
        print("  ✅ PASS: Streak active within 48h.")
    else:
        print("  ❌ FAIL: Streak should be active.")

    # Event 2: T (50 hours ago) -> Should be inactive now if that was the last one
    reset_user = "reset_tester"
    t_minus_50 = datetime.utcnow() - timedelta(hours=50)
    ledger.add_transaction(reset_user, 100, "EARN", "streak:old", created_at=t_minus_50)
    
    s2 = progression.get_streak_status(reset_user)
    print(f"  - T-50h Status: {s2['active']} (Expected: False)")
    
    if not s2['active']:
        print("  ✅ PASS: Streak reset after 48h.")
    else:
        print("  ❌ FAIL: Streak should have verified.")
        
    # Clean up
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    # ==========================================
    # CHECK D: CANONICALIZATION
    # ==========================================
    print("🔹 Check D: Canonical ID Consistency")
    from core.ids import IDGenerator
    
    id1 = IDGenerator.claim("Steam", "Game123")
    id2 = IDGenerator.claim("steam ", "game123 ")
    
    print(f"  - ID1: {id1}")
    print(f"  - ID2: {id2}")
    
    if id1 == id2 == "claim:steam:game123":
        print("  ✅ PASS: IDs are normalized and consistent.")
    else:
        print("  ❌ FAIL: ID normalization failed.")

    print("")

    # ==========================================
    # CHECK E: CONCURRENCY (The Stress Test)
    # ==========================================
    print("🔹 Check E: Concurrency Stress Test")
    import threading
    
    # Re-init fresh DB for this test to be sure
    if os.path.exists("data/stress_test.db"):
        os.remove("data/stress_test.db")
        
    stress_ledger = LedgerManager("data/stress_test.db")
    stress_ref = "claim:stress:test"
    stress_user = "concurrent_user"
    
    def worker():
        stress_ledger.add_transaction(stress_user, 100, "EARN", stress_ref)
        
    threads = []
    print("  - Launching 5 concurrent threads trying to claim the same ID...")
    for _ in range(5):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    final_balance = stress_ledger.get_balance(stress_user)
    print(f"  - Final Balance: {final_balance} (Expected: 100)")
    
    if final_balance == 100:
        print("  ✅ PASS: Concurrency handled. Idempotency held under fire.")
    else:
        print(f"  ❌ FAIL: Race condition detected. Balance: {final_balance}")

    if os.path.exists("data/stress_test.db"):
        os.remove("data/stress_test.db")

if __name__ == "__main__":
    run_checks()
