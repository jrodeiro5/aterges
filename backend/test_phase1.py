"""
Test script for Aterges Phase 1 implementation
Tests AI Orchestrator and Google Analytics Agent
"""

import asyncio
import os
import sys
import logging

# Add the backend directory to Python path
sys.path.append(os.path.dirname(__file__))

from ai.orchestrator import AIOrchestrator
from agents.google_analytics_agent import GoogleAnalyticsAgent
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_configuration():
    """Check if all required configuration is present"""
    print("🔧 Checking Aterges Configuration...")
    
    config_ok = True
    
    # Google Cloud Project
    if settings.google_cloud_project:
        print(f"✅ Google Cloud Project: {settings.google_cloud_project}")
    else:
        print("❌ Google Cloud Project: Not configured")
        print("   Set GOOGLE_CLOUD_PROJECT in .env file")
        config_ok = False
    
    # Service Account Credentials
    if settings.google_application_credentials:
        if os.path.exists(settings.google_application_credentials):
            print(f"✅ Service Account: {settings.google_application_credentials}")
        else:
            print(f"❌ Service Account: File not found at {settings.google_application_credentials}")
            print("   Place your Aterges service account JSON file at this path")
            config_ok = False
    else:
        print("❌ Service Account: Not configured")
        print("   Set GOOGLE_APPLICATION_CREDENTIALS in .env file")
        config_ok = False
    
    # GA4 Property ID
    if settings.ga4_property_id:
        print(f"✅ GA4 Property: {settings.ga4_property_id}")
    else:
        print("❌ GA4 Property: Not configured")
        print("   Set GA4_PROPERTY_ID in .env file")
        config_ok = False
    
    if not config_ok:
        print("\n❌ Configuration incomplete!")
        print("📖 See ATERGES_INDEPENDENT_SETUP.md for detailed setup instructions")
        return False
    
    print("\n✅ Configuration looks good!")
    return True

async def test_google_analytics_agent():
    """Test the Google Analytics Agent"""
    print("\n🧪 Testing Google Analytics Agent...")
    
    try:
        agent = GoogleAnalyticsAgent()
        
        if agent.is_initialized:
            print("✅ Google Analytics Agent initialized successfully")
            
            # Test health check
            health = await agent.health_check()
            print(f"🏥 Health check result: {health}")
            
            if health.get('status') == 'healthy':
                print("✅ Google Analytics Agent is healthy and ready")
            else:
                print("⚠️ Google Analytics Agent has issues:")
                print(f"   {health.get('message', 'Unknown issue')}")
            
        else:
            print(f"❌ Google Analytics Agent failed to initialize: {agent.last_error}")
            
    except Exception as e:
        print(f"❌ Error testing Google Analytics Agent: {e}")

async def test_ai_orchestrator():
    """Test the AI Orchestrator"""
    print("\n🧪 Testing AI Orchestrator...")
    
    try:
        orchestrator = AIOrchestrator(
            project_id=settings.google_cloud_project,
            location=settings.google_cloud_location
        )
        
        print("✅ AI Orchestrator initialized successfully")
        
        # Get status
        status = orchestrator.get_agent_status()
        print(f"📊 Orchestrator status:")
        print(f"   Model: {status['orchestrator']['model']}")
        print(f"   Agents: {status['orchestrator']['agents_count']}")
        print(f"   Tools: {status['orchestrator']['tools_count']}")
        
        # List agents
        for agent_name, agent_status in status['agents'].items():
            agent_symbol = "✅" if agent_status['initialized'] else "❌"
            print(f"   {agent_symbol} {agent_name}: {agent_status['description']}")
        
        # Test a simple query (may fail without proper GA4 setup)
        print("\n🤖 Testing AI query...")
        try:
            response = await orchestrator.process_query(
                "What is Google Analytics and what data can you help me analyze?",
                {"email": "test@example.com"}
            )
            print(f"✅ AI Response preview: {response[:200]}...")
        except Exception as e:
            print(f"⚠️ AI query test failed: {e}")
            print("   This is expected if GA4 property has no data or needs additional setup")
            
    except Exception as e:
        print(f"❌ Error testing AI Orchestrator: {e}")

async def main():
    """Run all tests"""
    print("🚀 Starting Aterges Phase 1 Implementation Tests")
    print("=" * 60)
    
    # Check configuration first
    if not check_configuration():
        print("\n🛠️ To fix configuration issues:")
        print("1. Follow the setup guide: ATERGES_INDEPENDENT_SETUP.md")
        print("2. Create your own Google Cloud project")
        print("3. Set up service account and GA4 property")
        print("4. Update .env file with your values")
        return
    
    # Run tests
    await test_google_analytics_agent()
    await test_ai_orchestrator()
    
    print("\n" + "=" * 60)
    print("✅ Phase 1 implementation tests completed!")
    
    if settings.validate_google_cloud_config():
        print("🎉 Aterges is ready for AI-powered conversations!")
        print("🌐 Start the backend: python main.py")
        print("🌐 Visit frontend: https://aterges.vercel.app")
    else:
        print("🔧 Complete the configuration to enable AI features")

if __name__ == "__main__":
    asyncio.run(main())
