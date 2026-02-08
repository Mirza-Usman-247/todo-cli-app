#!/bin/bash
# Run All E2E Tests
# Executes all Phase 8 E2E tests in sequence

set -e

echo "=== Running All E2E Tests ==="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
TOTAL=0

# Function to run test
run_test() {
    local test_file=$1
    local test_name=$(basename $test_file .py)

    echo -e "${BLUE}Running: ${test_name}${NC}"
    TOTAL=$((TOTAL + 1))

    if python3 $test_file; then
        echo -e "${GREEN}✅ PASSED: ${test_name}${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ FAILED: ${test_name}${NC}"
        FAILED=$((FAILED + 1))
    fi

    echo ""
    echo "---"
    echo ""
}

# Prerequisites check
echo "Checking prerequisites..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

# Check if backend is accessible
if ! curl -s http://localhost:8000/health &> /dev/null; then
    echo -e "${RED}❌ Backend not accessible at http://localhost:8000${NC}"
    echo "Make sure to port-forward: kubectl port-forward svc/todo-app-backend 8000:8000"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites satisfied${NC}"
echo ""
echo "---"
echo ""

# Change to test directory
cd "$(dirname "$0")"

# Run all tests
run_test "test_event_flow_create.py"
run_test "test_event_flow_update.py"
run_test "test_event_flow_delete.py"
run_test "test_event_flow_reminder.py"
run_test "test_idempotency.py"
run_test "test_concurrency.py"

# Summary
echo "=== Test Summary ==="
echo "Total tests: ${TOTAL}"
echo -e "${GREEN}Passed: ${PASSED}${NC}"
echo -e "${RED}Failed: ${FAILED}${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
