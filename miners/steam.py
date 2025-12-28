import requests
import re
from typing import List
from bs4 import BeautifulSoup
from core.models import GameOffer, Rarity
from miners.base import BaseMiner

class SteamMiner(BaseMiner):
    def __init__(self):
        super().__init__("Steam Store")
        # Search URL: 
        # specials=1 (On Sale)
        # maxprice=free (Free)
        # category1=998 (Game) - This filters out DLCs/Soundtracks to reduce noise
        # supportedlang=english - Ensures we can parse review text
        self.search_url = "https://store.steampowered.com/search/results/?maxprice=free&specials=1&category1=998&supportedlang=english"

    def _clean_price(self, price_str: str) -> float:
        """Robustly extracts float value from any currency string (e.g., '₪59.90', '€19.99')."""
        if not price_str or "free" in price_str.lower():
            return 0.0
        try:
            # Regex to find standard price format (digits + optional dot/comma)
            # Matches: 19.99, 59,90, 1,200.00
            # We assume '.' is decimal separator for simplistic global support, 
            # or we normalize ',' to '.' if it looks like a decimal.
            
            # Simple approach: Remove everything except digits and dots/commas
            clean = re.sub(r'[^\d.,]', '', price_str)
            
            # If comma is used as decimal (e.g. 59,99), replace with dot
            if ',' in clean and '.' not in clean:
               clean = clean.replace(',', '.')
            
            return float(clean)
        except:
            return 0.0

    def _parse_review_score(self, review_html: str) -> bool:
        """Returns True if reviews are Very Positive or Overwhelmingly Positive."""
        if not review_html:
            return False
            
        # Steam stores review data in data-tooltip-html or class names
        # Example class: "search_review_summary positive"
        # But "positive" can mean "Mostly Positive". We want "Very" or "Overwhelmingly".
        # The tooltip usually contains "Very Positive" text.
        
        # We will check the data-tooltip-html attribute content for keywords
        lower_html = review_html.lower()
        if "overwhelmingly positive" in lower_html:
            return True
        if "very positive" in lower_html:
            return True
            
        return False

    def fetch_games(self) -> List[GameOffer]:
        self._rate_limit()
        print(f"⛏️  {self.name}: Scanning for Quality Deals...")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            response = requests.get(self.search_url, headers=headers)
            if response.status_code != 200:
                print(f"⚠️  Steam returned {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.select('a.search_result_row')
            
            loot_crate = []
            
            for row in rows:
                try:
                    title = row.select_one('.title').text.strip()
                    
                    # 1. Quality Check: Reviews
                    # We strictly require "Very Positive" or "Overwhelmingly Positive"
                    review_tag = row.select_one('.search_review_summary')
                    if not review_tag:
                         continue

                    # Parse data-tooltip-html="Very Positive<br>..."
                    review_html = review_tag.get('data-tooltip-html', '')
                    if not self._parse_review_score(review_html):
                        # print(f"🗑️  Skipping garbage: {title}")
                        continue
                        
                    # 2. 100% Discount Check
                    discount_div = row.select_one('.search_discount span')
                    if not discount_div or discount_div.text.strip() != '-100%':
                        continue
                    
                    # 3. Price Check (Get Original Price from <strike>)
                    # If it's a 100% deal, the original price is always struck through.
                    strike = row.select_one('strike')
                    if not strike: 
                        continue
                    
                    original_price = self._clean_price(strike.text.strip())
                    
                    if original_price <= 0:
                        continue

                    # Url
                    store_url = row['href']
                    
                    # Image (img src inside .search_capsule)
                    img_tag = row.select_one('.search_capsule img')
                    image_url = img_tag['src'] if img_tag else ""

                    # Rarity logic
                    rarity = Rarity.COMMON
                    if original_price > 40: rarity = Rarity.LEGENDARY
                    elif original_price > 15: rarity = Rarity.EPIC
                    elif original_price > 5: rarity = Rarity.RARE

                    # ID Extraction
                    platform_id = row.get('data-ds-appid')
                    if not platform_id:
                        # Fallback: try to regex from URL
                        match = re.search(r'/app/(\d+)', store_url)
                        if match:
                            platform_id = match.group(1)
                        else:
                            platform_id = f"steam_unknown_{hash(title)}" # Last resort

                    offer = GameOffer(
                        title=title,
                        original_price=original_price,
                        discount_price=0.0,
                        description="Steam Community Reviewed: Very Positive+",
                        image_url=image_url,
                        store_url=store_url,
                        source="Steam",
                        platform_id=platform_id,
                        rarity=rarity
                    )
                    loot_crate.append(offer)
                    
                except Exception as e:
                    continue
                    
            return loot_crate

        except Exception as e:
            print(f"❌ Error mining Steam: {e}")
            return []

if __name__ == "__main__":
    miner = SteamMiner()
    loot = miner.fetch_games()
    for item in loot:
        print(item)
