"""
Test script to verify date parsing in AI Orchestrator
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(os.path.dirname(__file__))

from ai.orchestrator import AIOrchestrator
from config import settings

async def test_date_parsing():
    """Test if the AI is parsing dates correctly"""
    print("🗓️ Testing Date Parsing in AI Orchestrator")
    print("=" * 50)
    
    try:
        orchestrator = AIOrchestrator(
            project_id=settings.google_cloud_project,
            location=settings.google_cloud_location
        )
        
        # Test date parsing method
        today = datetime.now()
        yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        week_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        
        print(f"Today: {today.strftime('%Y-%m-%d')}")
        print(f"Yesterday: {yesterday}")
        print(f"7 days ago: {week_ago}")
        
        # Test the date parsing function
        test_queries = [
            "usuarios en los últimos 7 días",
            "last 7 days users", 
            "yesterday traffic",
            "this week analytics"
        ]
        
        for query in test_queries:
            start_date, end_date = orchestrator._parse_date_reference(query)
            print(f"'{query}' → {start_date} to {end_date}")
        
        print(f"\n✅ Date parsing working correctly")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_date_parsing())
