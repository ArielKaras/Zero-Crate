
import sys
import os

# Ensure the parent directory is in sys.path so we can import 'core'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.state import UserStateManager

def test_has_opened():
    print("Testing has_opened method...")
    try:
        manager = UserStateManager()
        # Ensure dummy data doesn't exist or is clean
        # We can't strictly clear DB without side effects, so we test 'not found' primarily
        # or separate DB path, but let's just checking the method exists and runs.
        
        result = manager.has_opened("test_user_999", "test_offer_999")
        print(f"Call successful. Result: {result}")
        assert isinstance(result, bool)
        print("✅ has_opened method exists and works.")
        
    except AttributeError:
        print("❌ FAILED: 'UserStateManager' has no attribute 'has_opened'")
        sys.exit(1)
    except Exception as e:
        print(f"❌ FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_has_opened()
