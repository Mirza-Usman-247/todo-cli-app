#!/bin/bash
# Validate Minikube Deployment (T127)
# Comprehensive validation of all Phase 5 components

set -e

echo "=== Minikube Deployment Validation ==="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Function to run check
run_check() {
    local check_name=$1
    local check_command=$2

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    echo -n "Checking ${check_name}... "

    if eval "$check_command" &>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

# Infrastructure Checks
echo -e "${BLUE}=== Infrastructure Checks ===${NC}"

run_check "Minikube running" "minikube status | grep -q 'Running'"
run_check "kubectl configured" "kubectl cluster-info | grep -q 'is running'"
run_check "Dapr installed" "kubectl get namespace dapr-system"
run_check "Kafka namespace" "kubectl get namespace kafka"

echo ""

# Dapr Control Plane
echo -e "${BLUE}=== Dapr Control Plane ===${NC}"

run_check "dapr-operator" "kubectl get deployment dapr-operator -n dapr-system -o jsonpath='{.status.availableReplicas}' | grep -q '1'"
run_check "dapr-sidecar-injector" "kubectl get deployment dapr-sidecar-injector -n dapr-system -o jsonpath='{.status.availableReplicas}' | grep -q '1'"
run_check "dapr-sentry" "kubectl get deployment dapr-sentry -n dapr-system -o jsonpath='{.status.availableReplicas}' | grep -q '1'"
run_check "dapr-placement" "kubectl get statefulset dapr-placement-server -n dapr-system -o jsonpath='{.status.readyReplicas}' | grep -q '1'"

echo ""

# Kafka Cluster
echo -e "${BLUE}=== Kafka Cluster ===${NC}"

run_check "Kafka cluster ready" "kubectl get kafka my-cluster -n kafka -o jsonpath='{.status.conditions[?(@.type==\"Ready\")].status}' | grep -q 'True'"
run_check "Kafka pods running" "kubectl get pods -n kafka -l app.kubernetes.io/name=kafka --field-selector=status.phase=Running | grep -q 'Running'"
run_check "ZooKeeper running" "kubectl get pods -n kafka -l app.kubernetes.io/name=zookeeper --field-selector=status.phase=Running | grep -q 'Running'"

echo ""

# Kafka Topics
echo -e "${BLUE}=== Kafka Topics ===${NC}"

KAFKA_POD=$(kubectl get pod -n kafka -l app.kubernetes.io/name=kafka -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -n "$KAFKA_POD" ]; then
    run_check "todo-created topic" "kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh --bootstrap-server my-cluster-kafka-bootstrap:9092 --list | grep -q 'todo-created'"
    run_check "todo-updated topic" "kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh --bootstrap-server my-cluster-kafka-bootstrap:9092 --list | grep -q 'todo-updated'"
    run_check "todo-deleted topic" "kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh --bootstrap-server my-cluster-kafka-bootstrap:9092 --list | grep -q 'todo-deleted'"
    run_check "todo-reminder topic" "kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh --bootstrap-server my-cluster-kafka-bootstrap:9092 --list | grep -q 'todo-reminder'"
else
    echo -e "${YELLOW}⚠️  Kafka pod not found, skipping topic checks${NC}"
fi

echo ""

# Redis
echo -e "${BLUE}=== Redis State Store ===${NC}"

run_check "Redis master running" "kubectl get pods redis-master-0 --field-selector=status.phase=Running | grep -q 'Running'"
run_check "Redis service" "kubectl get svc redis-master | grep -q 'redis-master'"
run_check "Redis connectivity" "kubectl exec redis-master-0 -- redis-cli ping | grep -q 'PONG'"

echo ""

# Application Pods
echo -e "${BLUE}=== Application Pods ===${NC}"

run_check "Backend pod running" "kubectl get pods -l app=backend --field-selector=status.phase=Running | grep -q 'Running'"
run_check "Frontend pod running" "kubectl get pods -l app=frontend --field-selector=status.phase=Running | grep -q 'Running'"

# Check for Dapr sidecars
BACKEND_POD=$(kubectl get pod -l app=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
FRONTEND_POD=$(kubectl get pod -l app=frontend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -n "$BACKEND_POD" ]; then
    run_check "Backend Dapr sidecar" "kubectl get pod $BACKEND_POD -o jsonpath='{.spec.containers[*].name}' | grep -q 'daprd'"
    run_check "Backend container count" "kubectl get pod $BACKEND_POD -o jsonpath='{.spec.containers[*].name}' | wc -w | grep -q '2'"
fi

if [ -n "$FRONTEND_POD" ]; then
    run_check "Frontend Dapr sidecar" "kubectl get pod $FRONTEND_POD -o jsonpath='{.spec.containers[*].name}' | grep -q 'daprd'"
    run_check "Frontend container count" "kubectl get pod $FRONTEND_POD -o jsonpath='{.spec.containers[*].name}' | wc -w | grep -q '2'"
fi

echo ""

# Dapr Components
echo -e "${BLUE}=== Dapr Components ===${NC}"

run_check "pubsub-kafka component" "kubectl get component pubsub-kafka | grep -q 'pubsub-kafka'"
run_check "statestore-redis component" "kubectl get component statestore-redis | grep -q 'statestore-redis'"
run_check "kubernetes-secrets component" "kubectl get component kubernetes-secrets | grep -q 'kubernetes-secrets'"

echo ""

# Dapr Subscriptions
echo -e "${BLUE}=== Dapr Subscriptions ===${NC}"

run_check "todo-created subscription" "kubectl get subscription backend-todo-created | grep -q 'backend-todo-created'"
run_check "todo-updated subscription" "kubectl get subscription backend-todo-updated | grep -q 'backend-todo-updated'"
run_check "todo-deleted subscription" "kubectl get subscription backend-todo-deleted | grep -q 'backend-todo-deleted'"
run_check "todo-reminder subscription" "kubectl get subscription backend-todo-reminder | grep -q 'backend-todo-reminder'"

echo ""

# Services
echo -e "${BLUE}=== Services ===${NC}"

run_check "Backend service" "kubectl get svc todo-app-backend | grep -q 'ClusterIP'"
run_check "Frontend service" "kubectl get svc todo-app-frontend | grep -q 'NodePort'"

echo ""

# Health Checks
echo -e "${BLUE}=== Health Checks ===${NC}"

if [ -n "$BACKEND_POD" ]; then
    run_check "Backend health endpoint" "kubectl exec $BACKEND_POD -c backend -- curl -sf http://localhost:8000/health | grep -q '\"status\"'"
    run_check "Backend Dapr health" "kubectl exec $BACKEND_POD -c daprd -- curl -sf http://localhost:3500/v1.0/healthz/outbound"
fi

echo ""

# Functional Test
echo -e "${BLUE}=== Functional Test ===${NC}"

if [ -n "$BACKEND_POD" ]; then
    # Port-forward backend
    kubectl port-forward $BACKEND_POD 8000:8000 &>/dev/null &
    PF_PID=$!
    sleep 3

    # Create a test task
    TEST_RESPONSE=$(curl -sf -X POST http://localhost:8000/api/v1/events/tasks \
        -H "Content-Type: application/json" \
        -d '{"userId":"test-user","title":"Validation Test","priority":"high"}' 2>/dev/null || echo "")

    if [ -n "$TEST_RESPONSE" ] && echo "$TEST_RESPONSE" | grep -q '"id"'; then
        echo -e "Create task API... ${GREEN}✅ PASS${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "Create task API... ${RED}❌ FAIL${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    # Cleanup port-forward
    kill $PF_PID 2>/dev/null || true
fi

echo ""

# Summary
echo "=== Validation Summary ==="
echo "Total Checks: ${TOTAL_CHECKS}"
echo -e "${GREEN}Passed: ${PASSED_CHECKS}${NC}"
echo -e "${RED}Failed: ${FAILED_CHECKS}${NC}"
echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}✅ All validation checks passed!${NC}"
    echo "Minikube deployment is healthy and ready."
    exit 0
else
    echo -e "${RED}❌ Some validation checks failed${NC}"
    echo "Review the failures above and check logs:"
    echo "  kubectl logs -l app=backend -c backend --tail=50"
    echo "  kubectl logs -l app=backend -c daprd --tail=50"
    exit 1
fi
