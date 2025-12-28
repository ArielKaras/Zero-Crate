import sqlite3
import uuid
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = "data/zerocrate.db"

class LedgerManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the ledger tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. Ledger Entries Table (The Source of Truth)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ledger_entries (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount INTEGER NOT NULL,
                transaction_type TEXT NOT NULL CHECK(transaction_type IN ('EARN','REDEEM','ADJUSTMENT','BONUS')),
                reference_id TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        
        # Index for faster balance calculation
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_ledger_user_created 
            ON ledger_entries(user_id, created_at)
        ''')

        # 2. Redemptions Table (State Machine for future store)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS redemptions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'FULFILLED', 'FAILED', 'CANCELED')),
                created_at TEXT NOT NULL,
                updated_at TEXT,
                idempotency_key TEXT UNIQUE,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_transaction(self, user_id: str, amount: int, transaction_type: str, reference_id: str, metadata: Dict[str, Any] = None, created_at: datetime = None) -> Dict[str, Any]:
        """
        Add a new transaction to the ledger.
        Enforces idempotency via reference_id.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        entry_id = str(uuid.uuid4())
        if created_at is None:
            created_at = datetime.utcnow()
        created_at_iso = created_at.isoformat()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        try:
            cursor.execute('''
                INSERT INTO ledger_entries (id, user_id, amount, transaction_type, reference_id, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (entry_id, user_id, amount, transaction_type, reference_id, created_at_iso, metadata_json))
            
            conn.commit()
            return {
                "id": entry_id,
                "status": "success",
                "message": "Transaction recorded."
            }
            
        except sqlite3.IntegrityError:
            # Idempotency Lock: Transaction with this reference_id already exists.
            # We fail silently or return the existing one.
            conn.rollback()
            return {
                "status": "skipped",
                "message": f"Idempotency check: Transaction {reference_id} already processed."
            }
        finally:
            conn.close()

    def get_balance(self, user_id: str) -> int:
        """Calculate current balance by summing all transactions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COALESCE(SUM(amount), 0) FROM ledger_entries WHERE user_id = ?', (user_id,))
        balance = cursor.fetchone()[0]
        conn.close()
        return balance

    def get_lifetime_earned(self, user_id: str) -> int:
        """Calculate total lifetime XP earned (ignoring redemption spend)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) 
            FROM ledger_entries 
            WHERE user_id = ? AND amount > 0 AND transaction_type IN ('EARN', 'BONUS', 'ADJUSTMENT')
        ''', (user_id,))
        lifetime = cursor.fetchone()[0]
        conn.close()
        return lifetime

    def get_last_earn_timestamp(self, user_id: str) -> Optional[datetime]:
        """Return the timestamp of the last earning activity."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT created_at 
            FROM ledger_entries 
            WHERE user_id = ? AND amount > 0 AND transaction_type IN ('EARN', 'BONUS')
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return datetime.fromisoformat(row[0])
        return None
