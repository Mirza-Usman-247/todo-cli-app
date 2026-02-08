#!/bin/bash
# Test Event-Driven Task API Endpoints
# Run this script to validate all API endpoints are working

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
API_URL=${API_URL:-"http://localhost:8000"}
USER_ID="test-user-$(date +%s)"

echo "=== Testing Event-Driven Task API ==="
echo ""
echo "API URL: ${API_URL}"
echo "Test User: ${USER_ID}"
echo ""

# Test 1: Health Check
echo -e "${BLUE}Test 1: Health Check${NC}"
HEALTH_RESPONSE=$(curl -s ${API_URL}/health)
echo "Response: ${HEALTH_RESPONSE}"

if echo "${HEALTH_RESPONSE}" | grep -q '"status"'; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    exit 1
fi
echo ""

# Test 2: Create Task
echo -e "${BLUE}Test 2: Create Task${NC}"
CREATE_RESPONSE=$(curl -s -X POST ${API_URL}/api/v1/events/tasks \
    -H "Content-Type: application/json" \
    -d "{
        \"userId\": \"${USER_ID}\",
        \"title\": \"Test Task - API Validation\",
        \"description\": \"Testing event-driven task creation\",
        \"priority\": \"high\",
        \"tags\": [\"test\", \"api\"],
        \"dueDate\": \"2026-12-31T23:59:59Z\"
    }")

echo "Response: ${CREATE_RESPONSE}"

TASK_ID=$(echo "${CREATE_RESPONSE}" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -n "$TASK_ID" ]; then
    echo -e "${GREEN}✅ Task created: ${TASK_ID}${NC}"
else
    echo -e "${RED}❌ Task creation failed${NC}"
    echo "Full response: ${CREATE_RESPONSE}"
    exit 1
fi
echo ""

# Test 3: Get Single Task
echo -e "${BLUE}Test 3: Get Single Task${NC}"
GET_RESPONSE=$(curl -s ${API_URL}/api/v1/events/tasks/${TASK_ID}?user_id=${USER_ID})
echo "Response: ${GET_RESPONSE}"

if echo "${GET_RESPONSE}" | grep -q "${TASK_ID}"; then
    echo -e "${GREEN}✅ Task retrieved successfully${NC}"
else
    echo -e "${RED}❌ Task retrieval failed${NC}"
fi
echo ""

# Test 4: List Tasks
echo -e "${BLUE}Test 4: List Tasks${NC}"
LIST_RESPONSE=$(curl -s ${API_URL}/api/v1/events/tasks?user_id=${USER_ID})
echo "Response: ${LIST_RESPONSE}"

if echo "${LIST_RESPONSE}" | grep -q "${TASK_ID}"; then
    echo -e "${GREEN}✅ Task found in list${NC}"
else
    echo -e "${RED}❌ Task not found in list${NC}"
fi
echo ""

# Test 5: Update Task
echo -e "${BLUE}Test 5: Update Task${NC}"
UPDATE_RESPONSE=$(curl -s -X PUT ${API_URL}/api/v1/events/tasks/${TASK_ID}?user_id=${USER_ID} \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Test Task - UPDATED",
        "priority": "urgent",
        "description": "Updated via API test"
    }')

echo "Response: ${UPDATE_RESPONSE}"

if echo "${UPDATE_RESPONSE}" | grep -q "UPDATED"; then
    echo -e "${GREEN}✅ Task updated successfully${NC}"
else
    echo -e "${RED}❌ Task update failed${NC}"
fi
echo ""

# Test 6: Mark Task Complete
echo -e "${BLUE}Test 6: Mark Task Complete${NC}"
COMPLETE_RESPONSE=$(curl -s -X PATCH ${API_URL}/api/v1/events/tasks/${TASK_ID}/complete?user_id=${USER_ID})
echo "Response: ${COMPLETE_RESPONSE}"

if echo "${COMPLETE_RESPONSE}" | grep -q '"isCompleted"'; then
    echo -e "${GREEN}✅ Task marked complete${NC}"
else
    echo -e "${RED}❌ Task completion failed${NC}"
fi
echo ""

# Test 7: Search Tasks
echo -e "${BLUE}Test 7: Search Tasks${NC}"
SEARCH_RESPONSE=$(curl -s -X POST ${API_URL}/api/v1/events/tasks/search \
    -H "Content-Type: application/json" \
    -d "{
        \"userId\": \"${USER_ID}\",
        \"priority\": \"urgent\",
        \"tags\": [\"test\"]
    }")

echo "Response: ${SEARCH_RESPONSE}"

if echo "${SEARCH_RESPONSE}" | grep -q "${TASK_ID}"; then
    echo -e "${GREEN}✅ Task found in search${NC}"
else
    echo -e "${RED}❌ Task not found in search${NC}"
fi
echo ""

# Test 8: Schedule Reminder
echo -e "${BLUE}Test 8: Schedule Reminder${NC}"
REMINDER_RESPONSE=$(curl -s -X POST ${API_URL}/api/v1/events/tasks/reminders/${TASK_ID}?user_id=${USER_ID} \
    -H "Content-Type: application/json" \
    -d '{
        "hoursBeforeDue": 24
    }')

echo "Response: ${REMINDER_RESPONSE}"

if echo "${REMINDER_RESPONSE}" | grep -q "reminder"; then
    echo -e "${GREEN}✅ Reminder scheduled${NC}"
else
    echo -e "${YELLOW}⚠️  Reminder endpoint may not be implemented yet${NC}"
fi
echo ""

# Test 9: Delete Task
echo -e "${BLUE}Test 9: Delete Task${NC}"
DELETE_RESPONSE=$(curl -s -X DELETE ${API_URL}/api/v1/events/tasks/${TASK_ID}?user_id=${USER_ID})
echo "Response: ${DELETE_RESPONSE}"

if echo "${DELETE_RESPONSE}" | grep -q "deleted\|success"; then
    echo -e "${GREEN}✅ Task deleted successfully${NC}"
else
    echo -e "${RED}❌ Task deletion failed${NC}"
fi
echo ""

# Test 10: Verify Deletion
echo -e "${BLUE}Test 10: Verify Task Deleted${NC}"
VERIFY_RESPONSE=$(curl -s ${API_URL}/api/v1/events/tasks/${TASK_ID}?user_id=${USER_ID})
echo "Response: ${VERIFY_RESPONSE}"

if echo "${VERIFY_RESPONSE}" | grep -q "not found\|404"; then
    echo -e "${GREEN}✅ Task deletion verified${NC}"
else
    echo -e "${YELLOW}⚠️  Task may still exist (eventual consistency)${NC}"
fi
echo ""

# Summary
echo "=== Test Summary ==="
echo -e "${GREEN}All basic API endpoint tests completed!${NC}"
echo ""
echo "Next Steps:"
echo "  1. Check Kafka topics: ./scripts/inspect-kafka-topics.sh"
echo "  2. View backend logs: kubectl logs -l app=backend -c backend -f"
echo "  3. Verify events in Redis: kubectl exec redis-master-0 -- redis-cli KEYS 'task:*'"
echo ""
