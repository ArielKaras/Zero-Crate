import time
from abc import ABC, abstractmethod
from typing import List
from core.models import GameOffer

class BaseMiner(ABC):
    def __init__(self, name: str):
        self.name = name
        self.last_request_time = 0
        self.min_interval = 2.0  # Seconds between requests (Security/Politeness)

    def _rate_limit(self):
        """Ensures we don't spam the API and get banned."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

    @abstractmethod
    def fetch_games(self) -> List[GameOffer]:
        """Must return a list of GameOffer objects."""
        pass
