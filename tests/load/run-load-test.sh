#!/bin/bash
# Run Load Tests with Locust (T130, T131)

set -e

echo "=== Todo App Load Testing ==="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
TARGET_HOST=${TARGET_HOST:-"http://localhost:8000"}
USERS=${USERS:-100}
SPAWN_RATE=${SPAWN_RATE:-10}
RUN_TIME=${RUN_TIME:-"5m"}

# Check if locust is installed
if ! command -v locust &> /dev/null; then
    echo -e "${RED}❌ Locust not found${NC}"
    echo "Install: pip install locust"
    exit 1
fi

echo -e "${BLUE}Load Test Configuration:${NC}"
echo "  Target Host: ${TARGET_HOST}"
echo "  Users: ${USERS}"
echo "  Spawn Rate: ${SPAWN_RATE} users/sec"
echo "  Run Time: ${RUN_TIME}"
echo ""

# Ask for confirmation
read -p "Start load test? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted"
    exit 0
fi

# Change to load test directory
cd "$(dirname "$0")"

# Run Locust in headless mode
echo -e "${BLUE}Starting load test...${NC}"
locust -f locustfile.py \
    --host=${TARGET_HOST} \
    --users=${USERS} \
    --spawn-rate=${SPAWN_RATE} \
    --run-time=${RUN_TIME} \
    --headless \
    --html=load-test-report.html \
    --csv=load-test-results

echo ""
echo -e "${GREEN}✅ Load test complete!${NC}"
echo ""

# Display results summary
if [ -f "load-test-results_stats.csv" ]; then
    echo "=== Results Summary ==="
    cat load-test-results_stats.csv | column -t -s,
    echo ""
fi

echo "Full report: load-test-report.html"
echo ""

# Check for failures
FAILURES=$(grep -o "\"Total\",\"[0-9]*\"" load-test-results_stats.csv | grep -o "[0-9]*" || echo "0")

if [ "$FAILURES" -gt 0 ]; then
    echo -e "${RED}⚠️  ${FAILURES} requests failed${NC}"
    exit 1
else
    echo -e "${GREEN}✅ All requests successful${NC}"
fi
