"""
Real-time debug script to trace GA4 function calls with actual dates
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(os.path.dirname(__file__))

from ai.orchestrator import AIOrchestrator
from config import settings

async def test_real_query():
    """Test a real query and trace the exact function calls"""
    print("🔍 Testing Real AI Query with Date Tracing")
    print("=" * 60)
    
    try:
        orchestrator = AIOrchestrator(
            project_id=settings.google_cloud_project,
            location=settings.google_cloud_location
        )
        
        # Test the exact query from the chat
        user_query = "¿Cuántos usuarios activos tuve en los últimos 7 días?"
        user_context = {"email": "zariwille@cuvox.de", "user_id": "test"}
        
        print(f"Query: {user_query}")
        print(f"Current date: {datetime.now().strftime('%Y-%m-%d')}")
        
        # Test date parsing for this specific query
        start_date, end_date = orchestrator._parse_date_reference(user_query)
        print(f"Parsed dates: {start_date} to {end_date}")
        
        # Process the query and capture the response
        print("\n🤖 Processing query...")
        response = await orchestrator.process_query(user_query, user_context)
        
        print(f"\n📝 AI Response:")
        print(response)
        
        # Check if the response mentions wrong dates
        if "2024" in response:
            print("\n🚨 PROBLEM DETECTED: AI response mentions 2024 dates!")
        if "mayo" in response.lower():
            print("🚨 PROBLEM DETECTED: AI response mentions May (mayo)!")
            
        print(f"\n✅ Debug complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_query())
