#!/bin/bash

# Aterges Backend Diagnostic Script
# This script helps diagnose the 503 Service Unavailable issue

echo "🔍 ATERGES BACKEND DIAGNOSTIC SCRIPT"
echo "=================================="
echo "Timestamp: $(date)"
echo ""

# Check current service status
echo "1. 🌐 Testing backend health endpoint..."
BACKEND_URL="https://aterges-backend-service-kqswfx4lva-ew.a.run.app"

echo "Testing: $BACKEND_URL/health"
curl -v -w "\n\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" \
     -H "Accept: application/json" \
     "$BACKEND_URL/health" || echo "❌ Health check failed"

echo ""
echo "2. 🔍 Testing root endpoint..."
echo "Testing: $BACKEND_URL/"
curl -v -w "\n\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" \
     -H "Accept: application/json" \
     "$BACKEND_URL/" || echo "❌ Root endpoint failed"

echo ""
echo "3. 🔍 Testing signup endpoint..."
echo "Testing: $BACKEND_URL/auth/signup"
curl -v -X POST \
     -H "Content-Type: application/json" \
     -H "Accept: application/json" \
     -d '{"email":"test@example.com","password":"testpassword123"}' \
     -w "\n\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" \
     "$BACKEND_URL/auth/signup" || echo "❌ Signup endpoint failed"

echo ""
echo "4. 📊 Cloud Run Service Information:"
echo "Service URL: $BACKEND_URL"
echo "Expected Response: JSON with service status"
echo ""
echo "If you see 503 errors, check:"
echo "- Google Cloud Run logs in Google Cloud Console"
echo "- Environment variable configuration"
echo "- Database connectivity"
echo "- Container startup logs"
echo ""
echo "Next steps:"
echo "1. Fix .env.production (DATABASE_URL format)"
echo "2. Update GitHub Secrets"
echo "3. Redeploy service"
echo "4. Monitor logs during startup"

# Test local configuration
echo ""
echo "5. 🔧 Local Configuration Check:"
if [ -f ".env.production" ]; then
    echo "✅ .env.production exists"
    grep -v "PASSWORD\|SECRET\|KEY" .env.production | head -5
else
    echo "❌ .env.production missing"
fi

echo ""
echo "🏁 Diagnostic complete. Check output above for issues."
