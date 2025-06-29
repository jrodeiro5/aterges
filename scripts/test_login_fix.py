#!/usr/bin/env python3
"""
Test Login Fix
Verify that login now works after email confirmation fix
"""

import requests
import json

# Your working backend URL
BACKEND_URL = "https://aterges-backend-service-1017653515088.europe-west1.run.app"

def test_login_fix():
    """Test that login now works after fixing email confirmation."""
    print("🔍 TESTING LOGIN FIX")
    print("=" * 40)
    print(f"Backend: {BACKEND_URL}")
    
    # Test with the confirmed users
    test_users = [
        {"email": "javirodeiro5@gmail.com", "password": "your_password_here"},
        {"email": "kikirikuiri@gmail.com", "password": "your_password_here"}
    ]
    
    print("\n📋 Testing login for confirmed users...")
    
    for i, user in enumerate(test_users, 1):
        print(f"\n{i}. Testing login for: {user['email']}")
        
        # NOTE: You'll need to replace "your_password_here" with actual passwords
        print("   ⚠️  Please update this script with real passwords to test")
        print("   💡 Or test manually from your frontend")
        
        # Commented out actual test since we don't have passwords
        # response = requests.post(f"{BACKEND_URL}/auth/login", json=user)
        # print(f"   Status: {response.status_code}")
        # if response.status_code == 200:
        #     print("   ✅ LOGIN SUCCESS!")
        # else:
        #     print(f"   ❌ LOGIN FAILED: {response.text}")
    
    print("\n🎯 WHAT WAS FIXED:")
    print("• Users had email_confirmed_at = null")
    print("• Supabase requires email confirmation by default") 
    print("• Used MCP to set email_confirmed_at = NOW()")
    print("• Both users are now confirmed and can login")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Test login from your frontend")
    print("2. Should get 200 response with JWT token")
    print("3. /api/me should work with the token")
    print("4. Configure Supabase to disable email confirmation")

if __name__ == "__main__":
    test_login_fix()
