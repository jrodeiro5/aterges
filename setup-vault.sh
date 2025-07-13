#!/bin/bash

# Supabase Vault BYOK Setup Script
# This script helps set up the final environment variable needed for the vault integration

echo "🚀 Supabase Vault BYOK Setup"
echo "================================"
echo ""

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "❌ Error: .env.local file not found!"
    echo "Please make sure you're in the project root directory."
    exit 1
fi

# Check if service role key is already set
if grep -q "^SUPABASE_SERVICE_ROLE_KEY=" .env.local; then
    echo "✅ SUPABASE_SERVICE_ROLE_KEY is already configured!"
    echo ""
else
    echo "⚠️  SUPABASE_SERVICE_ROLE_KEY is not yet configured."
    echo ""
    echo "To complete the setup:"
    echo "1. Go to your Supabase Dashboard"
    echo "2. Navigate to Settings → API"
    echo "3. Copy the 'service_role' key"
    echo "4. Add it to your .env.local file:"
    echo ""
    echo "   SUPABASE_SERVICE_ROLE_KEY=\"your_service_role_key_here\""
    echo ""
    
    read -p "Do you want to add it now? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        read -p "Paste your service role key: " service_key
        
        if [ ! -z "$service_key" ]; then
            echo "" >> .env.local
            echo "# Supabase Service Role Key (for Vault API operations)" >> .env.local
            echo "SUPABASE_SERVICE_ROLE_KEY=\"$service_key\"" >> .env.local
            echo ""
            echo "✅ Service role key added successfully!"
        else
            echo "❌ No key provided. Please add it manually to .env.local"
        fi
    fi
fi

echo ""
echo "🧪 Testing Setup..."
echo "================================"

# Check if Node.js is available
if command -v node &> /dev/null; then
    echo "✅ Node.js found"
else
    echo "❌ Node.js not found. Please install Node.js to continue."
    exit 1
fi

# Check if dependencies are installed
if [ -d "node_modules" ]; then
    echo "✅ Dependencies installed"
else
    echo "⚠️  Dependencies not found. Installing..."
    npm install
fi

echo ""
echo "🚀 Setup Instructions:"
echo "================================"
echo "1. Start the development server:"
echo "   npm run dev"
echo ""
echo "2. Test the vault integration:"
echo "   Visit: http://localhost:3000/test-vault"
echo ""
echo "3. Use the integrations page:"
echo "   Visit: http://localhost:3000/app/integrations"
echo ""
echo "✅ Supabase Vault BYOK is ready!"
echo ""
echo "📚 Documentation:"
echo "   - docs/VAULT_IMPLEMENTATION_COMPLETE.md"
echo "   - docs/supabase-vault-byok-implementation.md"
echo ""
