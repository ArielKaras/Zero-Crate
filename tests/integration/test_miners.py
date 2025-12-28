
import pytest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from miners.epic import EpicMiner
from miners.steam import SteamMiner
from miners.scout import Scout
from core.models import Rarity

# --- EPIC MINER TESTS ---
@patch('requests.get')
def test_epic_miner_parsing(mock_get):
    """Verify Epic Miner correctly parses compliant JSON response."""
    # Mock Response Data
    mock_data = {
        "data": {
            "Catalog": {
                "searchStore": {
                    "elements": [
                        {
                            "title": "Free Game A",
                            "price": {
                                "totalPrice": {
                                    "discountPrice": 0,
                                    "originalPrice": 1500 # 15.00
                                }
                            },
                            "keyImages": [{"url": "http://img.com/a.jpg"}],
                            "productSlug": "free-game-a"
                        }
                    ]
                }
            }
        }
    }
    
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_data
    
    miner = EpicMiner()
    loot = miner.fetch_games()
    
    assert len(loot) == 1
    item = loot[0]
    assert item.title == "Free Game A"
    assert item.original_price == 15.00

# --- STEAM MINER TESTS ---
@patch('requests.get')
def test_steam_miner_parsing(mock_get):
    """Verify Steam Miner parses HTML and filters garbage."""
    html_content = """
    <html>
        <a class="search_result_row" href="https://store.steampowered.com/app/101" data-ds-appid="101">
            <div class="title">Good Game</div>
            <div class="search_review_summary" data-tooltip-html="Overwhelmingly Positive<br>98% of checks..."></div>
            <div class="search_discount"><span>-100%</span></div>
            <div class="search_price discounted">
                <strike>$19.99</strike><br>Free
            </div>
            <div class="search_capsule"><img src="thumb.jpg"></div>
        </a>
    </html>
    """
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = html_content
    
    miner = SteamMiner()
    loot = miner.fetch_games()
    
    assert len(loot) == 1
    assert loot[0].title == "Good Game"

# --- SCOUT MINER TESTS ---
@patch('feedparser.parse')
def test_scout_filtering(mock_parse):
    """Verify Scout ignores DLC and non-games."""
    
    mock_feed = MagicMock()
    mock_feed.status = 200
    
    # helper to create entry objects with attributes
    def create_entry(title):
        e = MagicMock()
        e.title = title
        e.link = "http://reddit.com/r/1"
        # content structure for scout: entry.content[0].value
        content_mock = MagicMock()
        content_mock.value = '<a href="http://realStart.com/game">Link</a>'
        e.content = [content_mock]
        return e

    mock_feed.entries = [
        create_entry("[Steam] (Game) Cool RPG"),
        create_entry("[Steam] (DLC) Soundtrack Vol 1"), # BLOCKED
        create_entry("[Epic] (Beta) Test Server")       # BLOCKED
    ]
    
    mock_parse.return_value = mock_feed
    
    scout = Scout()
    # Mock specific helpers to avoid complex content regex matching in unit test
    scout._extract_real_url = MagicMock(return_value="http://real.url/game")
    scout._extract_thumbnail = MagicMock(return_value="http://thumb.jpg")
    
    loot = scout.fetch_games()
    
    assert len(loot) == 1
    assert loot[0].title == "Cool RPG"
