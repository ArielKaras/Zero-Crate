from typing import Any

class IDGenerator:
    """
    Single Source of Truth for generating Canonical Reference IDs.
    Prevents format drift and ensures idempotency across the application.
    """

    @staticmethod
    def claim(source: str, unique_id: str) -> str:
        """
        Generate a canonical ID for a game claim.
        Format: claim:{source}:{unique_id}
        Example: claim:Steam:12345 or claim:Epic Games:borderlands-3
        """
        # Normalize inputs: lowercase, strip whitespace
        s = source.strip().lower()
        u = str(unique_id).strip().lower()
        return f"claim:{s}:{u}"

    @staticmethod
    def bonus(bonus_type: str, context: str) -> str:
        """
        Generate a canonical ID for a specific bonus.
        Format: bonus:{type}:{context}
        Example: bonus:streak:2025-12-25
        """
        t = bonus_type.strip().lower()
        c = str(context).strip().lower()
        return f"bonus:{t}:{c}"

    @staticmethod
    def transaction(tx_type: str, ref: str) -> str:
        """
        Generic generator if needed, but prefer specific methods.
        """
        return f"tx:{tx_type}:{ref}"
