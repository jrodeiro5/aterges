#!/bin/bash
set -e  # Exit on any error

# Get port from environment variable or default to 8000
PORT=${PORT:-8000}

echo "Starting Aterges Backend on port $PORT"
echo "Environment check:"
echo "  - Python version: $(python --version)"
echo "  - Working directory: $(pwd)"
echo "  - Port: $PORT"
echo "  - Environment variables:"
echo "    * DEBUG: ${DEBUG:-not_set}"
echo "    * SUPABASE_URL: ${SUPABASE_URL:+set} ${SUPABASE_URL:-not_set}"
echo "    * DATABASE_URL: ${DATABASE_URL:+set} ${DATABASE_URL:-not_set}"
echo "    * GOOGLE_CLOUD_PROJECT: ${GOOGLE_CLOUD_PROJECT:-not_set}"
echo "    * GA4_PROPERTY_ID: ${GA4_PROPERTY_ID:+set} ${GA4_PROPERTY_ID:-not_set}"

# Check if main_robust.py exists
if [ ! -f "main_robust.py" ]; then
    echo "ERROR: main_robust.py not found in $(pwd)"
    ls -la
    exit 1
fi

# Check if requirements are installed
echo "Checking installed packages:"
pip list | grep -E "(fastapi|uvicorn|supabase)" || echo "Some required packages may be missing"

# Test basic Python import
echo "Testing Python imports:"
python -c "import fastapi, uvicorn; print('FastAPI and Uvicorn imported successfully')" || {
    echo "ERROR: Failed to import required packages"
    exit 1
}

# Start the FastAPI application with better error output
echo "Executing: uvicorn main_robust:app --host 0.0.0.0 --port $PORT --log-level info"
exec uvicorn main_robust:app --host 0.0.0.0 --port $PORT --log-level info
