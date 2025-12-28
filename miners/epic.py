import requests
from typing import List
from core.models import GameOffer, Rarity
from miners.base import BaseMiner

class EpicMiner(BaseMiner):
    def __init__(self):
        super().__init__("Epic Games Store")
        self.api_url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

    def _calculate_rarity(self, price: float) -> Rarity:
        # Simple Rarity Logic (We can expand this later)
        if price > 40: return Rarity.LEGENDARY
        if price > 15: return Rarity.EPIC
        if price > 5: return Rarity.RARE
        return Rarity.COMMON

    def fetch_games(self) -> List[GameOffer]:
        self._rate_limit()
        print(f"⛏️  {self.name}: Connecting to API...")
        
        try:
            response = requests.get(self.api_url, headers=self.get_headers())
            data = response.json()
            games = data['data']['Catalog']['searchStore']['elements']
            
            loot_crate = []
            
            for game in games:
                # SAFE & DUMB LOGIC: Check the bill, not the tag.
                # If Original Price > 0 and Final Price == 0, it is free.
                price = game.get('price', {}).get('totalPrice', {})
                discount_price = price.get('discountPrice', -1)
                original_price = price.get('originalPrice', -1)

                # Skip invalid data
                if discount_price == -1 or original_price == -1:
                    continue
                
                # Check for "Vaulted" status (Mystery Games often have 0 price but this tag)
                categories = [c.get('path') for c in game.get('categories', [])]
                is_vaulted = 'freegames/vaulted' in categories or 'freegames' in categories

                is_deal = False
                effective_rarity = None

                # Condition 1: Standard Deal (Price > 0, Discount = 0)
                if discount_price == 0 and original_price > 0:
                    is_deal = True
                    price_float = original_price / 100.0
                
                # Condition 2: Vault/Mystery Deal (Price = 0, but explicitly a Free Game)
                elif discount_price == 0 and original_price == 0 and is_vaulted:
                    is_deal = True
                    # We don't know the price, but Vault games are usually premium.
                    # Flag as LEGENDARY to ensure dopamine hit.
                    price_float = 29.99 # Assumed Value for Mystery Games
                    effective_rarity = Rarity.LEGENDARY

                if is_deal:
                    # Sanitize Slug (Mystery games have "[]")
                    slug = game.get('productSlug', '')
                    if slug == "[]" or not slug:
                        slug = "free-games" # Fallback to generic page

                    # Create the Object
                    offer_obj = GameOffer(
                        title=game['title'],
                        original_price=price_float,
                        discount_price=0.0,
                        description=game.get('description', ''),
                        image_url=game['keyImages'][0]['url'] if game.get('keyImages') else "",
                        store_url=f"https://store.epicgames.com/p/{slug}",
                        source="Epic Games",
                        rarity=effective_rarity if effective_rarity else self._calculate_rarity(price_float)
                    )
                    loot_crate.append(offer_obj)
            if not loot_crate:
                print(f"⚠️  No active 100% off deals found. Activating DEMO MODE for visualization.")
                return self._get_demo_loot()

            return loot_crate

        except Exception as e:
            print(f"❌ Error mining Epic: {e}")
            return []

    def _get_demo_loot(self) -> List[GameOffer]:
        """Returns fake data so the user can see the UI in action."""
        return [
            GameOffer(
                title="Melvor Idle (DEMO)",
                original_price=9.99,
                discount_price=0.0,
                description="Runescape-inspired idle game.",
                image_url="",
                store_url="https://store.epicgames.com/en-US/p/melvor-idle",
                source="Epic Games",
                rarity=Rarity.RARE
            ),
            GameOffer(
                title="Cyberpunk 2077: Ultimate (DEMO DROP)",
                original_price=59.99,
                discount_price=0.0,
                description="A story of action and adventure in Night City.",
                image_url="",
                store_url="https://store.epicgames.com/",
                source="Epic Games",
                rarity=Rarity.LEGENDARY
            )
        ]

# --- Verification Block (Run this file directly to test) ---
if __name__ == "__main__":
    miner = EpicMiner()
    loot = miner.fetch_games()
    print("\n--- MINING RESULTS ---")
    for item in loot:
        print(item)
