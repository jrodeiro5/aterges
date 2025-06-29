import requests
import json
import time
from datetime import datetime

def test_backend_endpoints():
    """Test all backend endpoints to diagnose the 503 issue."""
    base_url = "https://aterges-backend-service-kqswfx4lva-ew.a.run.app"
    
    print("🔍 ATERGES BACKEND SERVICE DIAGNOSTIC")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}")
    print(f"Target URL: {base_url}")
    print()
    
    endpoints = [
        {"method": "GET", "path": "/", "name": "Root"},
        {"method": "GET", "path": "/health", "name": "Health Check"},
        {"method": "GET", "path": "/docs", "name": "API Documentation"},
        {"method": "GET", "path": "/api/ai/status", "name": "AI Status"},
        {"method": "POST", "path": "/auth/signup", "name": "Signup", 
         "data": {"email": "test@example.com", "password": "testpass123"}},
    ]
    
    results = []
    
    for endpoint in endpoints:
        print(f"Testing {endpoint['name']}: {endpoint['method']} {endpoint['path']}")
        
        try:
            url = f"{base_url}{endpoint['path']}"
            start_time = time.time()
            
            if endpoint['method'] == 'GET':
                response = requests.get(url, timeout=30)
            elif endpoint['method'] == 'POST':
                response = requests.post(
                    url, 
                    json=endpoint.get('data', {}),
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
            
            response_time = time.time() - start_time
            
            result = {
                'endpoint': endpoint['name'],
                'status_code': response.status_code,
                'response_time': round(response_time, 2),
                'success': response.status_code < 400
            }
            
            if response.status_code == 200:
                print(f"  ✅ Status: {response.status_code} ({response_time:.2f}s)")
                try:
                    json_data = response.json()
                    print(f"  📄 Response preview: {str(json_data)[:100]}...")
                except:
                    print(f"  📄 Response preview: {response.text[:100]}...")
            else:
                print(f"  ❌ Status: {response.status_code} ({response_time:.2f}s)")
                print(f"  📄 Error: {response.text[:200]}...")
                
            results.append(result)
            
        except requests.exceptions.Timeout:
            print(f"  ⏰ TIMEOUT - Request took longer than 30 seconds")
            results.append({
                'endpoint': endpoint['name'],
                'status_code': 'TIMEOUT',
                'response_time': 30,
                'success': False
            })
        except requests.exceptions.ConnectionError:
            print(f"  🔌 CONNECTION ERROR - Cannot reach the service")
            results.append({
                'endpoint': endpoint['name'],
                'status_code': 'CONNECTION_ERROR',
                'response_time': 0,
                'success': False
            })
        except Exception as e:
            print(f"  💥 ERROR - {str(e)}")
            results.append({
                'endpoint': endpoint['name'],
                'status_code': 'ERROR',
                'response_time': 0,
                'success': False,
                'error': str(e)
            })
        
        print()
        time.sleep(1)  # Brief pause between requests
    
    # Summary
    print("📊 SUMMARY")
    print("-" * 30)
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    print(f"Successful endpoints: {successful}/{total}")
    
    if successful == 0:
        print("\n🚨 CRITICAL: ALL ENDPOINTS FAILED")
        print("Possible causes:")
        print("- Container failed to start")
        print("- Environment variables missing/incorrect")
        print("- Database connection issues")
        print("- Service account authentication problems")
    elif successful < total:
        print(f"\n⚠️  PARTIAL FAILURE: {total - successful} endpoints failed")
        print("Service is partially working - specific endpoint issues")
    else:
        print("\n✅ ALL TESTS PASSED - Service appears healthy")
    
    print("\n🔧 NEXT STEPS:")
    if successful == 0:
        print("1. Check Google Cloud Run logs")
        print("2. Verify environment variables in GitHub Secrets")
        print("3. Test database connectivity")
        print("4. Redeploy with fixed configuration")
    else:
        print("1. Focus on failed endpoints")
        print("2. Check specific error messages above")
        print("3. Verify authentication setup for protected endpoints")

if __name__ == "__main__":
    test_backend_endpoints()
