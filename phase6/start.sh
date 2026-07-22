#!/bin/bash
# ============================================================================
# Community Management System - Start Script
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting Community Management System..."

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Start all services
docker-compose up -d

# Wait for health check
echo "Waiting for services to start..."

# Simple health check
MAX_WAIT=60
WAIT=0
while [ $WAIT -lt $MAX_WAIT ]; do
    if docker-compose ps | grep -q "Running"; then
        echo "Services started successfully!"
        break
    fi
    sleep 2
    WAIT=$((WAIT + 2))
done

echo ""
echo "=========================================="
echo "Services Status"
echo "=========================================="
docker-compose ps
echo ""
echo "=========================================="
echo "Quick Start"
echo "=========================================="
echo ""
echo "1. Send message to Line Bot:"
echo "   Line Bot: http://localhost:3021"
echo ""
echo "2. Check health:"
echo "   curl http://localhost:3000"
echo ""
echo "3. View logs:"
echo "   docker-compose logs -f"
echo ""
echo "=========================================="
