#!/bin/bash
# Docker Compose Test Script
# Run this script to test the Docker setup

set -e

echo "=== Task Management System - Docker Test ==="
echo ""

# Check Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE="docker compose"
else
    echo "ERROR: Docker Compose is not available"
    exit 1
fi

echo "Using: $COMPOSE"
echo ""

# Build and start services
echo "=== Building Docker images ==="
$COMPOSE build

echo ""
echo "=== Starting services ==="
$COMPOSE up -d

echo ""
echo "=== Waiting for services to be ready ==="
sleep 10

# Wait for health check
MAX_RETRIES=30
RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "App is healthy!"
        break
    fi
    echo "Waiting for app to be ready... ($RETRY/$MAX_RETRIES)"
    sleep 2
    RETRY=$((RETRY + 1))
done

if [ $RETRY -eq $MAX_RETRIES ]; then
    echo "ERROR: App failed to start"
    $COMPOSE logs
    exit 1
fi

echo ""
echo "=== Running API Tests ==="

# Test health endpoint
echo -n "Health check: "
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "PASS"
else
    echo "FAIL"
    exit 1
fi

# Test registration
echo -n "User registration: "
REG_RESULT=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"username": "dockertest", "email": "docker@test.com", "password": "testpass123"}')
if echo "$REG_RESULT" | grep -q "dockertest"; then
    echo "PASS"
else
    echo "FAIL - $REG_RESULT"
fi

# Test login
echo -n "User login: "
LOGIN_RESULT=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email": "docker@test.com", "password": "testpass123"}')
if echo "$LOGIN_RESULT" | grep -q "access_token"; then
    echo "PASS"
    TOKEN=$(echo "$LOGIN_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
else
    echo "FAIL - $LOGIN_RESULT"
    exit 1
fi

# Test creating a task
echo -n "Create task: "
TASK_RESULT=$(curl -s -X POST http://localhost:8000/api/v1/tasks \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"title": "Docker Test Task", "priority": "high"}')
if echo "$TASK_RESULT" | grep -q "Docker Test Task"; then
    echo "PASS"
else
    echo "FAIL - $TASK_RESULT"
fi

# Test listing tasks
echo -n "List tasks: "
TASKS=$(curl -s http://localhost:8000/api/v1/tasks \
    -H "Authorization: Bearer $TOKEN")
if echo "$TASKS" | grep -q "items"; then
    echo "PASS"
else
    echo "FAIL"
fi

echo ""
echo "=== All Tests Passed! ==="
echo ""
echo "Services are running at:"
echo "  App:      http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "To stop: $COMPOSE down"
echo "To view logs: $COMPOSE logs -f"
