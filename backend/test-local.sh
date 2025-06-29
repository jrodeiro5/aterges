# Test script to verify container startup locally
# Run this before deploying to check for issues

echo "Building Docker image..."
docker build -t aterges-backend-test ./backend

echo "Testing container startup on port 8080..."
docker run --rm -e PORT=8080 -e DEBUG=true -p 8080:8080 aterges-backend-test &

# Wait for container to start
sleep 10

echo "Testing health endpoint..."
curl -f http://localhost:8080/health || echo "Health check failed"

echo "Stopping test container..."
docker stop $(docker ps -q --filter ancestor=aterges-backend-test) 2>/dev/null || true
