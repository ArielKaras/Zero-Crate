from dataclasses import dataclass
from enum import Enum
from typing import Optional

class Rarity(Enum):
    COMMON = "COMMON"       # < $5
    RARE = "RARE"           # $5 - $15
    EPIC = "EPIC"           # $15 - $40
    LEGENDARY = "LEGENDARY" # > $40
    HOLOGRAPHIC = "HOLOGRAPHIC" # Metacritic > 85

@dataclass
class GameOffer:
    title: str
    original_price: float
    discount_price: float
    description: str
    image_url: str
    store_url: str
    source: str  # e.g., "Epic", "Steam"
    platform_id: Optional[str] = None # Canonical Platform ID (e.g. Steam App ID)
    end_time: Optional[object] = None # Datetime object or None
    rarity: Rarity = Rarity.COMMON
    
    @property
    def savings(self) -> float:
        return self.original_price - self.discount_price

    @property
    def is_free_now(self) -> bool:
        return self.discount_price == 0

    @property
    def discount(self) -> int:
        if self.original_price == 0:
            return 0
        return int(((self.original_price - self.discount_price) / self.original_price) * 100)

    def __str__(self):
        return f"[{self.rarity.value}] {self.title} (Saved ${self.original_price:.2f})"
