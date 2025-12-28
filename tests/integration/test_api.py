
from fastapi.testclient import TestClient
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.main import app

client = TestClient(app)

def test_home_page():
    """Verify the dashboard loads (SSR)."""
    response = client.get("/")
    assert response.status_code == 200
    assert "ZeroCrate" in response.text

def test_state_endpoint():
    """Verify the Unified State endpoint returns valid JSON structure."""
    response = client.get("/api/state")
    assert response.status_code == 200
    data = response.json()
    
    # Check Root Keys
    assert "hero" in data
    assert "scout" in data
    assert "rails" in data
    
    # Check Data Types
    assert isinstance(data['rails'], list)
    assert isinstance(data['hero']['collection_value'], (int, float))

def test_open_action_404():
    """Verify handling of invalid offer IDs."""
    response = client.post("/api/open/INVALID_ID")
    # Our logic usually returns 200 with result='error', or 404.
    # checking current implementation...
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == 'Offer lost from cache'
