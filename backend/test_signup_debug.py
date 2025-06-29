"""
Debug script to test signup functionality directly
Run this to test the auth service without going through the API
"""

import asyncio
import sys
import os
import logging

# Add backend to path
sys.path.append(os.path.dirname(__file__))

from auth.auth_service_improved import AuthService
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_signup():
    """Test signup functionality directly"""
    
    print("🔧 Testing Signup Functionality Directly")
    print("=" * 50)
    
    # Check configuration
    print(f"Supabase URL: {settings.supabase_url}")
    print(f"Supabase Key: {settings.supabase_key[:20]}...")
    
    # Initialize auth service
    try:
        auth_service = AuthService(database=None)  # We don't need database for this test
        print("✅ Auth service initialized")
    except Exception as e:
        print(f"❌ Failed to initialize auth service: {e}")
        return
    
    # Test email and password
    test_email = "test-debug@example.com"
    test_password = "testpassword123"
    
    print(f"\n🧪 Testing signup with: {test_email}")
    
    try:
        result = await auth_service.signup(test_email, test_password)
        print("✅ Signup successful!")
        print(f"   Email confirmed: {result.get('email_confirmed', 'Unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        print(f"   User ID: {result.get('user', {}).get('id', 'No ID')}")
        print(f"   Next step: {result.get('next_step', 'No next step')}")
        
    except ValueError as e:
        print(f"❌ Signup failed with ValueError: {e}")
    except Exception as e:
        print(f"❌ Signup failed with unexpected error: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_signup())
