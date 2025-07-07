"""
Debug AI Orchestrator function calls to see what parameters it's actually sending
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(os.path.dirname(__file__))

from ai.orchestrator import AIOrchestrator
from config import settings

async def debug_ai_function_calls():
    """Debug what the AI is actually sending to GA4"""
    print("🔍 Debugging AI Orchestrator Function Calls")
    print("=" * 60)
    
    try:
        orchestrator = AIOrchestrator(
            project_id=settings.google_cloud_project,
            location=settings.google_cloud_location
        )
        
        print("✅ AI Orchestrator initialized")
        
        # Test Spanish query like the user asked
        user_query = "¿Cuántos usuarios activos tuve ayer?"
        user_context = {"email": "zariwille@cuvox.de", "user_id": "test"}
        
        print(f"User Query: {user_query}")
        
        # Test date parsing first
        start_date, end_date = orchestrator._parse_date_reference(user_query)
        print(f"Parsed dates: {start_date} to {end_date}")
        
        # Override the _execute_function_call method to see what parameters are sent
        original_execute = orchestrator._execute_function_call
        
        async def debug_execute_function_call(function_call):
            print(f"\n🔍 FUNCTION CALL DEBUG:")
            print(f"  Function name: {function_call.name}")
            print(f"  Function args: {dict(function_call.args)}")
            
            # Call the original function
            result = await original_execute(function_call)
            print(f"  Function result success: {result.get('success', False)}")
            if result.get('success'):
                data = result.get('data', {})
                if isinstance(data, dict) and 'totals' in data:
                    print(f"  Total activeUsers: {data['totals'].get('activeUsers', 'N/A')}")
                    print(f"  Data points: {len(data.get('data', []))}")
            else:
                print(f"  Error: {result.get('message', 'Unknown error')}")
            
            return result
        
        # Replace the method temporarily
        orchestrator._execute_function_call = debug_execute_function_call
        
        # Process the query
        print(f"\n🤖 Processing AI query...")
        response = await orchestrator.process_query(user_query, user_context)
        
        print(f"\n📝 Final AI Response:")
        print(response[:500] + "..." if len(response) > 500 else response)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_ai_function_calls())
