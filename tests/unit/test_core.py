
import pytest
import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from core.ledger import LedgerManager
from core.progression import ProgressionManager
from core.ids import IDGenerator

# Test Helpers
@pytest.fixture
def ledger():
    """Provides a fresh ledger for each test."""
    db_path = "data/test_unit_core.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    manager = LedgerManager(db_path=db_path)
    yield manager
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
def progression(ledger):
    return ProgressionManager(ledger)

def test_idempotency(ledger):
    """Ensure duplicate transactions are ignored."""
    user = "test_user_1"
    ref = "claim:unique_ref_123"
    
    # First Claim
    res1 = ledger.add_transaction(user, 100, "EARN", ref)
    assert res1['status'] == "success"
    assert ledger.get_balance(user) == 100
    
    # Duplicate Claim
    res2 = ledger.add_transaction(user, 100, "EARN", ref)
    assert res2['status'] == "skipped"
    assert ledger.get_balance(user) == 100 # Balance unchanged

def test_level_mechanic(ledger, progression):
    """Ensure level is calculated from LIFETIME earnings, not current balance."""
    user = "test_user_2"
    
    # Earn 900 XP (Level 3: sqrt(900/100))
    ledger.add_transaction(user, 900, "EARN", "bonus:setup")
    assert progression.get_level(user) == 3
    assert ledger.get_balance(user) == 900
    
    # Spend 500 XP
    ledger.add_transaction(user, -500, "REDEEM", "spend:shop")
    assert ledger.get_balance(user) == 400
    
    # Level should NOT drop
    assert progression.get_level(user) == 3

def test_streak_logic(ledger, progression):
    """Verify streak active/inactive states."""
    user = "streak_user"
    
    # Case 1: Active (Earned 40h ago)
    t_active = datetime.utcnow() - timedelta(hours=40)
    ledger.add_transaction(user, 10, "EARN", "streak:1", created_at=t_active)
    
    status = progression.get_streak_status(user)
    assert status['active'] is True
    
    # Case 2: Inactive (Earned 50h ago)
    user2 = "lazy_user"
    t_inactive = datetime.utcnow() - timedelta(hours=50)
    ledger.add_transaction(user2, 10, "EARN", "streak:2", created_at=t_inactive)
    
    status2 = progression.get_streak_status(user2)
    assert status2['active'] is False

def test_id_canonicalization():
    """Verify ID generator standardizes inputs."""
    id1 = IDGenerator.claim("Steam", "Game123")
    id2 = IDGenerator.claim("steam ", " game123 ")
    assert id1 == "claim:steam:game123"
    assert id1 == id2
