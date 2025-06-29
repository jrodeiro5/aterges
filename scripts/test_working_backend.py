#!/usr/bin/env python3
"""
Quick Backend Test Script
Test your working backend endpoints
"""

import requests
import json
from datetime import datetime

# Your WORKING backend URL
BACKEND_URL = "https://aterges-backend-service-1017653515088.europe-west1.run.app"

def test_endpoint(method, path, data=None, description=""):
    """Test a backend endpoint"""
    url = f"{BACKEND_URL}{path}"
    print(f"\n🔍 Testing: {description}")
    print(f"   {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code < 400:
            print(f"   ✅ SUCCESS")
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    json_data = response.json()
                    print(f"   Response: {json.dumps(json_data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"   Response: {response.text[:100]}...")
        else:
            print(f"   ❌ FAILED")
            print(f"   Error: {response.text[:200]}...")
            
        return response.status_code < 400
        
    except Exception as e:
        print(f"   💥 ERROR: {str(e)}")
        return False

def main():
    print("🎯 ATERGES BACKEND VERIFICATION")
    print("=" * 50)
    print(f"Testing: {BACKEND_URL}")
    print(f"Time: {datetime.now()}")
    
    # Test all endpoints
    results = []
    
    # Root endpoint
    results.append(test_endpoint("GET", "/", description="Root API Info"))
    
    # Health check
    results.append(test_endpoint("GET", "/health", description="Health Check"))
    
    # AI Status
    results.append(test_endpoint("GET", "/api/ai/status", description="AI System Status"))
    
    # API Documentation
    results.append(test_endpoint("GET", "/docs", description="API Documentation"))
    
    # Signup endpoint (the one that was failing!)
    results.append(test_endpoint("POST", "/auth/signup", {
        "email": "test@example.com", 
        "password": "testpass123"
    }, description="User Signup (CRITICAL TEST)"))
    
    # Summary
    successful = sum(results)
    total = len(results)
    
    print(f"\n📊 SUMMARY")
    print("-" * 30)
    print(f"Successful: {successful}/{total}")
    
    if successful == total:
        print("🎉 ALL TESTS PASSED - YOUR BACKEND IS WORKING PERFECTLY!")
        print("\n✅ You can now:")
        print("   - Sign up users from your frontend")
        print("   - Test the full application flow")
        print("   - Deploy frontend updates to Vercel")
    elif successful > 0:
        print(f"⚠️ PARTIAL SUCCESS - {total - successful} endpoints need attention")
    else:
        print("🚨 ALL TESTS FAILED - Backend may still have issues")
    
    print(f"\n🔗 Your working backend: {BACKEND_URL}")

if __name__ == "__main__":
    main()
