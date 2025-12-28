from datetime import datetime, timedelta
import math
from typing import Dict, Any, Tuple
from core.ledger import LedgerManager

class ProgressionManager:
    def __init__(self, ledger: LedgerManager):
        self.ledger = ledger

    def get_level(self, user_id: str) -> int:
        """
        Calculate Level based on Lifetime Earned XP.
        Formula: Level = floor(sqrt(total_xp / 100))
        Result is always at least 1.
        """
        lifetime_xp = self.ledger.get_lifetime_earned(user_id)
        if lifetime_xp <= 0:
            return 1
        
        # Progression Curve: 100 XP = Lv 1, 400 XP = Lv 2, 900 XP = Lv 3
        level = math.floor(math.sqrt(lifetime_xp / 100))
        return max(1, level)

    def get_streak_status(self, user_id: str) -> Dict[str, Any]:
        """
        Determine if the user's streak is active.
        Window: 48 hours from last EARN activity.
        """
        last_earn = self.ledger.get_last_earn_timestamp(user_id)
        
        if not last_earn:
            return {
                "active": False,
                "age_text": "Never",
                "message": "Start your streak!"
            }

        now = datetime.utcnow()
        delta = now - last_earn
        hours = int(delta.total_seconds() / 3600)
        if hours < 1:
            age_text = "Just now"
        else:
            age_text = f"{hours}h ago"
        
        if delta <= timedelta(hours=48):
            return {
                "active": True,
                "last_activity": last_earn,
                "age_text": age_text,
                "message": "Streak Active"
            }
        else:
            return {
                "active": False,
                "last_activity": last_earn,
                "age_text": age_text,
                "message": "Streak Inactive"
            }

    def get_player_stats(self, user_id: str) -> Dict[str, Any]:
        """Aggregates all player metrics for the HUD."""
        return {
            "balance": self.ledger.get_balance(user_id),
            "level": self.get_level(user_id),
            "streak": self.get_streak_status(user_id)
        }
