"""
core/state.py
User Interaction State Manager.
Strict Separation: This manages UX state (Opened/Seen), NOT economic value.
"""

import sqlite3
import os
from typing import Set, Dict, Any

STATE_DB_PATH = "data/user_state.db"

class UserStateManager:
    def __init__(self):
        self._ensure_db()

    def _ensure_db(self):
        os.makedirs(os.path.dirname(STATE_DB_PATH), exist_ok=True)
        with sqlite3.connect(STATE_DB_PATH) as conn:
            cursor = conn.cursor()
            # UX Table: Tracks which offers a user has intentionally opened
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS opened_offers (
                    user_id TEXT NOT NULL,
                    offer_id TEXT NOT NULL,
                    opened_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, offer_id)
                )
            """)
            conn.commit()

    def mark_opened(self, user_id: str, offer_id: str) -> Dict[str, Any]:
        """
        Records an 'Open' event.
        Atomic & Idempotent via PK Constraint.
        Returns: {'status': 'success' | 'already_opened'}
        """
        try:
            with sqlite3.connect(STATE_DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO opened_offers (user_id, offer_id) VALUES (?, ?)",
                    (user_id, offer_id)
                )
                conn.commit()
                return {"status": "success"}
        except sqlite3.IntegrityError:
            return {"status": "already_opened"}

    def get_opened_set(self, user_id: str) -> Set[str]:
        """Returns a set of all offer_ids opened by the user."""
        with sqlite3.connect(STATE_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT offer_id FROM opened_offers WHERE user_id = ?",
                (user_id,)
            )
            return {row[0] for row in cursor.fetchall()}

    def has_opened(self, user_id: str, offer_id: str) -> bool:
        """Checks if a specific offer has been opened by the user."""
        with sqlite3.connect(STATE_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM opened_offers WHERE user_id = ? AND offer_id = ?",
                (user_id, offer_id)
            )
            return cursor.fetchone() is not None
