#!/usr/bin/env python3
"""
Quick configuration test for Aterges backend
"""

try:
    print("🔧 Testing Aterges backend configuration...")
    
    from config import settings
    
    print("✅ Configuration loaded successfully!")
    print(f"   App Name: {settings.app_name}")
    print(f"   Debug Mode: {settings.debug}")
    print(f"   Supabase URL: {settings.supabase_url[:50]}...")
    print(f"   Database URL: {settings.database_url[:50]}...")
    print(f"   CORS Origins: {settings.get_cors_origins_list()}")
    print(f"   Secret Key: {'***' if settings.secret_key else 'NOT SET'}")
    print(f"   Google Cloud Project: {settings.google_cloud_project or 'Not configured (Phase 1)'}")
    
    print("\n🎯 Configuration test passed! Ready to start server.")
    
except Exception as e:
    print(f"❌ Configuration error: {e}")
    print("\n🔧 Check your .env file and try again.")
    exit(1)
