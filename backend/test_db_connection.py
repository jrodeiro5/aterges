#!/usr/bin/env python3
"""
Aterges Database Connection Test
Using VERIFIED Supabase configuration from MCP access
"""

import os
import asyncio
import asyncpg
from databases import Database
from supabase import create_client

# Verified configuration from Supabase MCP
SUPABASE_URL = "https://zsmnqwjeeknohsumhmlx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpzbW5xd2plZWtub2hzdW1obWx4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEwNjI4MTgsImV4cCI6MjA2NjYzODgxOH0.4Fy5oNDvPOLSBqBcF6x-rAkAhL82Z4tUPwY5ixxhA6Q"

# OLD FORMAT (causing 503)
DATABASE_URL_OLD = "postgres://postgres.zsmnqwjeeknohsumhmlx:8QO4fGFwWkXxiexy@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require&supa=base-pooler.x"

# NEW FORMAT (fixed)
DATABASE_URL_NEW = "postgresql://postgres.zsmnqwjeeknohsumhmlx:8QO4fGFwWkXxiexy@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require&supa=base-pooler.x"

async def test_database_connection(url, description):
    """Test database connection with given URL."""
    print(f"\n🔍 Testing {description}")
    print(f"URL format: {url[:50]}...")
    
    try:
        database = Database(url)
        await database.connect()
        
        # Test simple query
        result = await database.fetch_one("SELECT 1 as test")
        print(f"✅ SUCCESS: {description}")
        print(f"   Query result: {result}")
        
        # Test auth.users table
        users_count = await database.fetch_one("SELECT COUNT(*) as count FROM auth.users")
        print(f"   Users in auth.users: {users_count['count']}")
        
        # Test profiles table
        profiles_count = await database.fetch_one("SELECT COUNT(*) as count FROM profiles")
        print(f"   Profiles in public.profiles: {profiles_count['count']}")
        
        await database.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {description}")
        print(f"   Error: {str(e)}")
        return False

def test_supabase_client():
    """Test Supabase client connection."""
    print(f"\n🔍 Testing Supabase Client Connection")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test a simple query
        response = supabase.table('profiles').select('*').limit(1).execute()
        print(f"✅ SUCCESS: Supabase Client")
        print(f"   Profiles query successful: {len(response.data)} rows")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Supabase Client")
        print(f"   Error: {str(e)}")
        return False

async def main():
    """Main test function."""
    print("🎯 ATERGES DATABASE CONNECTION DIAGNOSTIC")
    print("=" * 50)
    print("Using VERIFIED configuration from Supabase MCP access")
    
    # Test Supabase client first
    supabase_ok = test_supabase_client()
    
    # Test old format (should fail)
    old_ok = await test_database_connection(DATABASE_URL_OLD, "OLD FORMAT (postgres://)")
    
    # Test new format (should work)
    new_ok = await test_database_connection(DATABASE_URL_NEW, "NEW FORMAT (postgresql://)")
    
    print(f"\n📊 SUMMARY")
    print("-" * 30)
    print(f"Supabase Client: {'✅ OK' if supabase_ok else '❌ FAIL'}")
    print(f"Old URL Format:  {'✅ OK' if old_ok else '❌ FAIL'}")
    print(f"New URL Format:  {'✅ OK' if new_ok else '❌ FAIL'}")
    
    if not old_ok and new_ok:
        print(f"\n🎉 DIAGNOSIS CONFIRMED!")
        print(f"   The issue is the URL format: 'postgres://' vs 'postgresql://'")
        print(f"   Update your GitHub secrets with the NEW format.")
    elif old_ok and new_ok:
        print(f"\n🤔 UNEXPECTED: Both formats work")
        print(f"   The issue might be elsewhere in your deployment.")
    elif not old_ok and not new_ok:
        print(f"\n🚨 PROBLEM: Neither format works")
        print(f"   There might be a network or credentials issue.")
    else:
        print(f"\n🎯 MIXED RESULTS: Check individual errors above")

if __name__ == "__main__":
    asyncio.run(main())
