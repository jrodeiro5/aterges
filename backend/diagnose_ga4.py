"""
Detailed diagnostic script for GA4 connection issues
"""

import os
import sys
import json
import asyncio
import logging

# Add the backend directory to Python path
sys.path.append(os.path.dirname(__file__))

from agents.google_analytics_agent import GoogleAnalyticsAgent
from config import settings

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def detailed_ga4_test():
    """Perform detailed GA4 diagnostics"""
    print("🔍 Detailed GA4 Connection Diagnostics")
    print("=" * 50)
    
    # Step 1: Check configuration
    print("\n1. Configuration Check:")
    print(f"   GA4 Property ID: {settings.ga4_property_id}")
    print(f"   Service Account File: {settings.google_application_credentials}")
    print(f"   File exists: {os.path.exists(settings.google_application_credentials)}")
    
    # Step 2: Test service account JSON parsing
    print("\n2. Service Account File Check:")
    try:
        with open(settings.google_application_credentials, 'r') as f:
            creds_data = json.load(f)
        print(f"   ✅ JSON structure valid")
        print(f"   Project ID: {creds_data.get('project_id')}")
        print(f"   Client Email: {creds_data.get('client_email')}")
        print(f"   Type: {creds_data.get('type')}")
    except Exception as e:
        print(f"   ❌ Error parsing JSON: {e}")
        return
    
    # Step 3: Test Google Analytics API import
    print("\n3. Google Analytics API Import Check:")
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.oauth2 import service_account
        print("   ✅ Google Analytics API imports successful")
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   Run: pip install google-analytics-data google-auth")
        return
    
    # Step 4: Test credentials loading
    print("\n4. Credentials Loading Test:")
    try:
        credentials = service_account.Credentials.from_service_account_file(
            settings.google_application_credentials,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        print("   ✅ Credentials loaded successfully")
        print(f"   Service Account Email: {credentials.service_account_email}")
    except Exception as e:
        print(f"   ❌ Credentials loading failed: {e}")
        return
    
    # Step 5: Test client initialization
    print("\n5. GA4 Client Initialization Test:")
    try:
        client = BetaAnalyticsDataClient(credentials=credentials)
        print("   ✅ GA4 client created successfully")
    except Exception as e:
        print(f"   ❌ Client initialization failed: {e}")
        return
    
    # Step 6: Test actual API call
    print("\n6. GA4 API Call Test:")
    try:
        from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
        from datetime import datetime, timedelta
        
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        request = RunReportRequest(
            property=settings.ga4_property_id,
            dimensions=[Dimension(name="date")],
            metrics=[Metric(name="sessions")],
            date_ranges=[DateRange(start_date=yesterday, end_date=yesterday)],
            limit=1
        )
        
        print(f"   Testing API call with property: {settings.ga4_property_id}")
        response = client.run_report(request=request)
        print(f"   ✅ API call successful!")
        print(f"   Rows returned: {len(response.rows)}")
        
        if response.rows:
            print(f"   Sample data: {response.rows[0].dimension_values[0].value}")
        else:
            print("   ⚠️ No data returned (this might be normal for new properties)")
            
    except Exception as e:
        print(f"   ❌ API call failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Check for common permission errors
        if "permission" in str(e).lower() or "access" in str(e).lower():
            print("\n   🔧 LIKELY SOLUTION:")
            print("   The service account needs to be added to your GA4 property!")
            print("   Steps:")
            print("   1. Go to https://analytics.google.com/")
            print("   2. Admin → Property Access Management")
            print(f"   3. Add user: {creds_data.get('client_email')}")
            print("   4. Give 'Viewer' permissions")
        
        return
    
    # Step 7: Test the actual agent
    print("\n7. GoogleAnalyticsAgent Test:")
    try:
        agent = GoogleAnalyticsAgent()
        print(f"   Agent initialized: {agent.is_initialized}")
        print(f"   GA client exists: {agent.ga_client is not None}")
        
        if agent.ga_client:
            print("   ✅ Agent has working GA4 client")
            
            # Test health check
            health_result = await agent.health_check()
            print(f"   Health check result: {health_result}")
        else:
            print("   ❌ Agent GA4 client is None")
            print(f"   Last error: {agent.last_error}")
            
    except Exception as e:
        print(f"   ❌ Agent test failed: {e}")
    
    print("\n" + "=" * 50)
    print("Diagnostic complete!")

if __name__ == "__main__":
    asyncio.run(detailed_ga4_test())
