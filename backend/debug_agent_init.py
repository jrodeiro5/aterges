"""
Debug script to trace exactly what's happening in GoogleAnalyticsAgent initialization
"""

import os
import sys
import json
import asyncio
import logging

# Add the backend directory to Python path
sys.path.append(os.path.dirname(__file__))

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def debug_ga_agent_init():
    """Debug the exact GoogleAnalyticsAgent initialization process"""
    print("🔍 Debugging GoogleAnalyticsAgent Initialization")
    print("=" * 60)
    
    # Import after setting up logging
    from agents.google_analytics_agent import GoogleAnalyticsAgent
    from config import settings
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.oauth2 import service_account
    
    print("\n1. Manual step-by-step initialization:")
    
    # Step 1: Load settings
    print(f"   GA4 Property ID: {settings.ga4_property_id}")
    print(f"   Service Account File: {settings.google_application_credentials}")
    
    # Step 2: Check file exists
    file_exists = os.path.exists(settings.google_application_credentials)
    print(f"   File exists: {file_exists}")
    
    if not file_exists:
        print("   ❌ File doesn't exist!")
        return
    
    # Step 3: Load credentials manually
    try:
        credentials = service_account.Credentials.from_service_account_file(
            settings.google_application_credentials,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        print(f"   ✅ Credentials loaded: {credentials.service_account_email}")
    except Exception as e:
        print(f"   ❌ Credentials failed: {e}")
        return
    
    # Step 4: Create client manually
    try:
        client = BetaAnalyticsDataClient(credentials=credentials)
        print(f"   ✅ Client created: {type(client)}")
        print(f"   ✅ Client is not None: {client is not None}")
    except Exception as e:
        print(f"   ❌ Client creation failed: {e}")
        return
    
    print("\n2. Now testing GoogleAnalyticsAgent:")
    
    # Create agent with debug
    try:
        print("   Creating GoogleAnalyticsAgent...")
        agent = GoogleAnalyticsAgent()
        
        print(f"   Agent.is_initialized: {agent.is_initialized}")
        print(f"   Agent.ga_client: {agent.ga_client}")
        print(f"   Agent.ga_client is None: {agent.ga_client is None}")
        print(f"   Agent.default_property_id: {agent.default_property_id}")
        print(f"   Agent.last_error: {agent.last_error}")
        
        # Try to access the agent's _initialize method directly
        print("\n3. Testing manual re-initialization:")
        
        # Save original client
        original_client = agent.ga_client
        
        # Call _initialize again
        try:
            agent._initialize()
            print(f"   After re-init - ga_client: {agent.ga_client}")
            print(f"   After re-init - ga_client is None: {agent.ga_client is None}")
        except Exception as e:
            print(f"   ❌ Re-initialization failed: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"   ❌ Agent creation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ga_agent_init()
