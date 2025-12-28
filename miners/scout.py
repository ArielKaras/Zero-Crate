"""
miners/scout.py
The Watcher: Monitors high-signal RSS feeds for 100% off deals.
Focus: r/FreeGameFindings (Strict moderation ensures high quality)
"""

import feedparser
import re
import html
from typing import List, Optional
from core.models import GameOffer, Rarity
from miners.base import BaseMiner

class Scout(BaseMiner):
    # RSS Feed for "New" posts to catch deals immediately
    RSS_URL = "https://www.reddit.com/r/FreeGameFindings/new/.rss"
    
    # Blocklist to enforce "Base Game Only" policy
    BLACKLIST_KEYWORDS = [
        "DLC", "Soundtrack", "Artbook", "Wallpaper", 
        "Demo", "Beta", "Alpha", "Restocked", "Massively Multiplayer"
    ]

    def __init__(self):
        super().__init__("Scout Signal")
        self.feed = None

    def _is_garbage(self, title: str) -> bool:
        """Filters out DLCs, trash, and non-game content."""
        title_upper = title.upper()
        
        # 1. Check for forbidden keywords
        for keyword in self.BLACKLIST_KEYWORDS:
            if keyword.upper() in title_upper:
                return True
        
        # 2. Check for "expired" flair (often in title for RSS)
        if "EXPIRED" in title_upper:
            return True

        return False

    def _normalize_platform(self, raw_platform: str) -> Optional[str]:
        """Maps subreddit tags to our internal Source strings."""
        raw = raw_platform.lower()
        if "steam" in raw:
            return "Steam"
        if "epic" in raw:
            return "Epic Games"
        if "gog" in raw:
            return "GOG"
        if "itch" in raw:
            return "Itch.io"
        return None  # We ignore unknown platforms for now

    def _estimate_value(self, platform: str) -> float:
        """
        Heuristic: RSS doesn't provide price.
        We estimate based on platform averages to ensure 'Value Saved' dopamine.
        """
        if platform == "Steam": return 14.99
        if platform == "Epic Games": return 19.99
        if platform == "GOG": return 9.99
        return 4.99




    def _extract_real_url(self, entry) -> str:
        """
        Reddit RSS 'link' is the thread URL.
        The real deal link is usually in the content HTML as <a href="...">[link]</a>.
        """
        try:
            content = entry.content[0].value
            # Regex to find the href associated with "[link]" text commonly used by Reddit
            # Or just the first external link that isn't reddit.com
            # r/FreeGameFindings usually has a standard format.
            matches = re.findall(r'href="([^"]+)"', content)
            for m in matches:
                if "reddit.com" not in m and "static.reddit" not in m:
                    return m
        except (AttributeError, IndexError):
            pass
        
        # Fallback to the thread link if we can't find it
        return entry.link

    def _extract_thumbnail(self, entry) -> str:
        """Attempts to find a thumbnail in the RSS entry."""
        # Reddit often uses 'media_thumbnail'
        if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
            return entry.media_thumbnail[0]['url']
        # Sometimes 'media_content'
        if hasattr(entry, 'media_content') and entry.media_content:
             return entry.media_content[0]['url']
        # Fallback: check content for img tag
        try:
            content = entry.content[0].value
            match = re.search(r'src="([^"]+jpg|[^"]+png)"', content)
            if match:
                return match.group(1)
        except:
            pass
        return ""

    def fetch_games(self) -> List[GameOffer]:
        """Fetches the feed and returns verified GameOffer objects."""
        print(f"🔭 Scout is scanning: {self.RSS_URL} ...")
        
        # Parse the RSS Feed
        try:
            feed = feedparser.parse(self.RSS_URL, request_headers=self.get_headers())
        except Exception as e:
            print(f"⚠️  Scout Link Error: {e}")
            return []

        if hasattr(feed, 'status') and feed.status != 200:
            print(f"⚠️  Scout failed to connect. Status: {feed.status}")
            return []

        loot_bag = []

        for entry in feed.entries:
            # RSS titles often look like: "[Steam] (Game) Pizza Possum - Free"
            title = entry.title
            
            # 1. Strict Filter Check
            if self._is_garbage(title):
                continue

            # 2. Parse Title Structure
            match = re.search(r"\[(.*?)\]", title)
            if not match:
                continue 
            
            raw_platform = match.group(1)
            platform = self._normalize_platform(raw_platform)

            if not platform:
                continue 

            # 3. Clean Game Title
            clean_title = title.replace(f"[{raw_platform}]", "").strip()
            clean_title = re.sub(r"\(.*?\)", "", clean_title) 
            clean_title = re.split(r"\-|–|100%|Free", clean_title)[0].strip()
            clean_title = html.unescape(clean_title)

            # 4. Extract Real URL & Image
            real_url = self._extract_real_url(entry)
            image_url = self._extract_thumbnail(entry)

            # 5. Construct the Offer
            estimated_price = self._estimate_value(platform)
            
            clean_url_key = real_url.split('?')[0].split('#')[0].rstrip('/')
            url_hash = hex(hash(clean_url_key) & 0xffffffff)[2:] 
            platform_id = f"scout_{platform.lower()}_{url_hash}"

            rarity = Rarity.COMMON
            if estimated_price > 15: rarity = Rarity.RARE
            
            offer = GameOffer(
                title=clean_title,
                original_price=estimated_price,
                discount_price=0.0, 
                description=f"Detected via Scout. Source: {platform}",
                image_url=image_url, 
                store_url=real_url,
                source=f"{platform}",
                platform_id=platform_id,
                rarity=rarity
            )
            
            loot_bag.append(offer)

        print(f"✅ Scout returned with {len(loot_bag)} potential assets.")
        return loot_bag

# Quick verification block
if __name__ == "__main__":
    scout = Scout()
    deals = scout.fetch_games()
    print("\n--- SCOUT REPORT ---")
    for deal in deals:
        print(f"FOUND: {deal.title} | {deal.source} | ID: {deal.platform_id}")
