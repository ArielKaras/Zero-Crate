import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.cli import LootConsole
from core.models import GameOffer, Rarity

def test_hud():
    ui = LootConsole()
    
    print("\n--- TEST: HUD RENDERING ---")
    mock_stats = {
        "level": 5,
        "balance": 1500,
        "streak": {
            "active": True,
            "message": "Streak Active",
            "age_text": "14h ago"
        }
    }
    total_saved = 124.99
    
    ui.display_hud(mock_stats, total_saved)
    print("---------------------------\n")

def test_loot_table():
    ui = LootConsole()
    print("\n--- TEST: NEW LOOT TABLE ---")
    
    mock_loot = [
        GameOffer(
            title="Cyberpunk 2077",
            original_price=59.99,
            discount_price=0.0, # Free
            description="RPG",
            image_url="",
            store_url="https://steam.com",
            source="Steam",
            rarity=Rarity.LEGENDARY
        ),
        GameOffer(
            title="Indie Gem",
            original_price=19.99,
            discount_price=9.99, # 50% off
            description="Indie",
            image_url="",
            store_url="https://epic.com",
            source="Epic",
            rarity=Rarity.RARE
        )
    ]
    
    ui.display_loot(mock_loot)
    print("----------------------------\n")

if __name__ == "__main__":
    test_hud()
    test_loot_table()
