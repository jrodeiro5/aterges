"""
Direct GA4 test with correct metrics and current dates
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(os.path.dirname(__file__))

from agents.google_analytics_agent import GoogleAnalyticsAgent

async def test_real_ga4_with_correct_metrics():
    """Test GA4 with the correct metric names and recent dates"""
    print("🔍 Testing GA4 with Correct Metrics and Current Dates")
    print("=" * 60)
    
    try:
        agent = GoogleAnalyticsAgent()
        
        if not agent.ga_client:
            print("❌ GA4 client not initialized")
            return
            
        print("✅ GA4 client is working")
        print(f"Property ID: {agent.default_property_id}")
        
        # Test with current dates
        today = datetime.now()
        yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        last_week = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        
        print(f"Today: {today.strftime('%Y-%m-%d')}")
        print(f"Yesterday: {yesterday}")
        print(f"Last 7 days: {last_week} to {yesterday}")
        
        # Test 1: Yesterday's users with correct metrics
        print(f"\n🧪 Test 1: Yesterday's Users ({yesterday})")
        result = await agent.get_ga4_report(
            start_date=yesterday,
            end_date=yesterday,
            dimensions=['date'],
            metrics=['activeUsers']  # This is the correct metric name
        )
        
        if result.get('success'):
            data = result['data']['data']
            if data:
                users = data[0].get('activeUsers', 0)
                print(f"✅ Yesterday users: {users}")
            else:
                print("⚠️ No data for yesterday")
        else:
            print(f"❌ Error: {result.get('message', 'Unknown error')}")
        
        # Test 2: Last 7 days
        print(f"\n🧪 Test 2: Last 7 Days ({last_week} to {yesterday})")
        result = await agent.get_ga4_report(
            start_date=last_week,
            end_date=yesterday,
            dimensions=['date'],
            metrics=['activeUsers']
        )
        
        if result.get('success'):
            data = result['data']['data']
            total_users = result['data']['totals'].get('activeUsers', 0)
            print(f"✅ Total users (7 days): {total_users}")
            print(f"✅ Days with data: {len(data)}")
            
            if data:
                print("Daily breakdown:")
                for day in data[-3:]:  # Show last 3 days
                    date = day.get('date')
                    users = day.get('activeUsers', 0)
                    print(f"  {date}: {users} users")
        else:
            print(f"❌ Error: {result.get('message', 'Unknown error')}")
        
        # Test 3: Try different metrics
        print(f"\n🧪 Test 3: Different Metrics")
        metrics_to_test = ['activeUsers', 'totalUsers', 'newUsers', 'sessions']
        
        for metric in metrics_to_test:
            result = await agent.get_ga4_report(
                start_date=yesterday,
                end_date=yesterday,
                dimensions=['date'],
                metrics=[metric]
            )
            
            if result.get('success'):
                data = result['data']['data']
                if data:
                    value = data[0].get(metric, 0)
                    print(f"✅ {metric}: {value}")
                else:
                    print(f"⚠️ {metric}: No data")
            else:
                print(f"❌ {metric}: Error - {result.get('message', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_ga4_with_correct_metrics())
