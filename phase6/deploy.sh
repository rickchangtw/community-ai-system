#!/bin/bash
# ============================================================================
# Community Management System - Deployment Script
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Community Management System Deployment"
echo "=========================================="

# Check prerequisites
echo ""
echo "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose is not installed"
    exit 1
fi

# Check .env file
if [ ! -f .env ]; then
    echo "WARNING: .env file not found"
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo "Please edit .env and fill in the required values"
    echo ""
fi

# Check Line Bot configuration
if grep -q "LINE_WEBHOOK_SECRET" .env; then
    echo "Line Bot configuration found in .env"
else
    echo "WARNING: Line Bot configuration not found in .env"
    echo "LINE agents will not be able to send notifications"
fi

# Build and deploy
echo ""
echo "Building and deploying services..."
echo ""

docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to be healthy..."
echo ""

# Function to check health
check_health() {
    local service=$1
    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2

        # Check if service is running
        if docker-compose ps $service | grep -q "Running"; then
            echo " ✓ Service $service is running"
            return 0
        fi
    done

    echo " ✗ Service $service failed to start"
    return 1
}

# Check all services
check_health "postgres"
check_health "redis"
check_health "ceo-agent"
check_health "property-agent"
check_health "security-agent"
check_health "fire-agent"
check_health "energy-agent"
check_health "notice-agent"
check_health "line-bot"
check_health "meeting-transcription"
check_health "monitoring-agent"
check_health "health-check"

# Print summary
echo ""
echo "=========================================="
echo "Deployment Summary"
echo "=========================================="
echo ""
echo "Services deployed:"
docker-compose ps
echo ""
echo "Ports allocated:"
echo "  3000 - Health Check"
echo "  3001 - CEO Agent"
echo "  3002 - Property Agent"
echo "  3003 - Security Agent"
echo "  3004 - Fire Safety Agent"
echo "  3005 - Energy Agent"
echo "  3006 - Notice Center Agent"
echo "  3010 - Monitoring Agent"
echo "  3011 - Meeting Transcription"
echo "  3021 - Line Bot"
echo "  5432 - PostgreSQL"
echo "  6379 - Redis"
echo ""
echo "=========================================="
echo "Access URLs"
echo "=========================================="
echo ""
echo "Line Bot: http://localhost:3021/health"
echo "Health Check: http://localhost:3000"
echo "CEO Agent: http://localhost:3001"
echo "Property Agent: http://localhost:3002"
echo "Security Agent: http://localhost:3003"
echo "Fire Agent: http://localhost:3004"
echo "Energy Agent: http://localhost:3005"
echo "Notice Agent: http://localhost:3006"
echo "Monitoring: http://localhost:3010"
echo "Meeting Transcription: http://localhost:3011"
echo ""
echo "=========================================="
echo "Usage"
echo "=========================================="
echo ""
echo "Start all services:"
echo "  docker-compose up -d"
echo ""
echo "Stop all services:"
echo "  docker-compose down"
echo ""
echo "Rebuild services:"
echo "  docker-compose build"
echo ""
echo "View logs:"
echo "  docker-compose logs -f"
echo ""
echo "View specific service logs:"
echo "  docker-compose logs ceo-agent"
echo ""
echo "=========================================="
