#!/bin/bash
# Validate OKE Deployment (T128)
# Production readiness validation for Oracle Kubernetes Engine

set -e

echo "=== OKE Production Deployment Validation ==="
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

# Configuration
NAMESPACE=${NAMESPACE:-"default"}

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

# Cluster Connectivity
echo -e "${BLUE}=== Cluster Connectivity ===${NC}"

run_check "kubectl configured" "kubectl cluster-info | grep -q 'is running'"
run_check "OKE cluster accessible" "kubectl get nodes | grep -q 'Ready'"
run_check "At least 3 nodes" "[ $(kubectl get nodes --no-headers | wc -l) -ge 3 ]"

echo ""

# Dapr Control Plane (HA)
echo -e "${BLUE}=== Dapr Control Plane (HA Mode) ===${NC}"

run_check "Dapr operator (3 replicas)" "[ $(kubectl get deployment dapr-operator -n dapr-system -o jsonpath='{.status.availableReplicas}') -ge 3 ]"
run_check "Dapr sidecar injector (3 replicas)" "[ $(kubectl get deployment dapr-sidecar-injector -n dapr-system -o jsonpath='{.status.availableReplicas}') -ge 3 ]"
run_check "Dapr sentry (3 replicas)" "[ $(kubectl get deployment dapr-sentry -n dapr-system -o jsonpath='{.status.availableReplicas}') -ge 3 ]"
run_check "Dapr placement (3 replicas)" "[ $(kubectl get statefulset dapr-placement-server -n dapr-system -o jsonpath='{.status.readyReplicas}') -ge 3 ]"
run_check "Dapr mTLS enabled" "kubectl get configuration dapr-config -n ${NAMESPACE} -o jsonpath='{.spec.mtls.enabled}' | grep -q 'true'"

echo ""

# Application Deployment
echo -e "${BLUE}=== Application Deployment ===${NC}"

run_check "Backend deployment exists" "kubectl get deployment todo-app-backend -n ${NAMESPACE}"
run_check "Frontend deployment exists" "kubectl get deployment todo-app-frontend -n ${NAMESPACE}"
run_check "Backend min 3 replicas" "[ $(kubectl get deployment todo-app-backend -n ${NAMESPACE} -o jsonpath='{.status.availableReplicas}') -ge 3 ]"
run_check "Frontend min 2 replicas" "[ $(kubectl get deployment todo-app-frontend -n ${NAMESPACE} -o jsonpath='{.status.availableReplicas}') -ge 2 ]"

echo ""

# Autoscaling
echo -e "${BLUE}=== Autoscaling (HPA) ===${NC}"

run_check "Backend HPA configured" "kubectl get hpa todo-app-backend -n ${NAMESPACE}"
run_check "Frontend HPA configured" "kubectl get hpa todo-app-frontend -n ${NAMESPACE}"
run_check "Backend HPA metrics available" "kubectl get hpa todo-app-backend -n ${NAMESPACE} -o jsonpath='{.status.currentMetrics}' | grep -q 'cpu'"
run_check "Frontend HPA metrics available" "kubectl get hpa todo-app-frontend -n ${NAMESPACE} -o jsonpath='{.status.currentMetrics}' | grep -q 'cpu'"

echo ""

# Pod Disruption Budgets
echo -e "${BLUE}=== Pod Disruption Budgets ===${NC}"

run_check "Backend PDB exists" "kubectl get pdb todo-app-backend -n ${NAMESPACE}"
run_check "Frontend PDB exists" "kubectl get pdb todo-app-frontend -n ${NAMESPACE}"

echo ""

# Managed Kafka
echo -e "${BLUE}=== Managed Kafka ===${NC}"

run_check "Kafka credentials secret" "kubectl get secret kafka-credentials -n ${NAMESPACE}"
run_check "pubsub-kafka component" "kubectl get component pubsub-kafka -n ${NAMESPACE}"
run_check "Kafka uses SASL auth" "kubectl get component pubsub-kafka -n ${NAMESPACE} -o yaml | grep -q 'authType.*password'"
run_check "Kafka uses SSL" "kubectl get component pubsub-kafka -n ${NAMESPACE} -o yaml | grep -q 'SASL_SSL'"

echo ""

# Redis Cluster
echo -e "${BLUE}=== Redis Cluster ===${NC}"

run_check "Redis credentials secret" "kubectl get secret redis-credentials -n ${NAMESPACE}"
run_check "Redis master running" "kubectl get pods redis-master-0 -n ${NAMESPACE} --field-selector=status.phase=Running | grep -q 'Running'"
run_check "Redis replicas (min 3)" "[ $(kubectl get pods -l app.kubernetes.io/name=redis -n ${NAMESPACE} --field-selector=status.phase=Running --no-headers | wc -l) -ge 3 ]"
run_check "Redis persistence enabled" "kubectl get pvc -l app.kubernetes.io/name=redis -n ${NAMESPACE} | grep -q 'Bound'"

echo ""

# Dapr Components
echo -e "${BLUE}=== Dapr Components ===${NC}"

run_check "statestore-redis component" "kubectl get component statestore-redis -n ${NAMESPACE}"
run_check "kubernetes-secrets component" "kubectl get component kubernetes-secrets -n ${NAMESPACE}"
run_check "Subscriptions configured" "[ $(kubectl get subscriptions -n ${NAMESPACE} --no-headers | wc -l) -ge 4 ]"

echo ""

# Services
echo -e "${BLUE}=== Services ===${NC}"

run_check "Backend service (ClusterIP)" "kubectl get svc todo-app-backend -n ${NAMESPACE} -o jsonpath='{.spec.type}' | grep -q 'ClusterIP'"
run_check "Frontend service (LoadBalancer)" "kubectl get svc todo-app-frontend -n ${NAMESPACE} -o jsonpath='{.spec.type}' | grep -q 'LoadBalancer'"
run_check "Frontend external IP assigned" "kubectl get svc todo-app-frontend -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress}' | grep -q '.'"

echo ""

# Monitoring
echo -e "${BLUE}=== Monitoring Stack ===${NC}"

run_check "Monitoring namespace" "kubectl get namespace monitoring"
run_check "Prometheus deployed" "kubectl get deployment prometheus-server -n monitoring"
run_check "Grafana deployed" "kubectl get deployment grafana -n monitoring"
run_check "Fluent Bit deployed" "kubectl get daemonset fluent-bit -n monitoring"
run_check "Prometheus persistent volume" "kubectl get pvc -l app=prometheus -n monitoring | grep -q 'Bound'"
run_check "Grafana persistent volume" "kubectl get pvc -l app.kubernetes.io/name=grafana -n monitoring | grep -q 'Bound'"

echo ""

# Resource Limits
echo -e "${BLUE}=== Resource Limits ===${NC}"

BACKEND_POD=$(kubectl get pod -l app=backend -n ${NAMESPACE} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -n "$BACKEND_POD" ]; then
    run_check "Backend CPU limits set" "kubectl get pod $BACKEND_POD -n ${NAMESPACE} -o jsonpath='{.spec.containers[0].resources.limits.cpu}' | grep -q '.'"
    run_check "Backend memory limits set" "kubectl get pod $BACKEND_POD -n ${NAMESPACE} -o jsonpath='{.spec.containers[0].resources.limits.memory}' | grep -q '.'"
    run_check "Dapr sidecar CPU limits set" "kubectl get pod $BACKEND_POD -n ${NAMESPACE} -o jsonpath='{.spec.containers[1].resources.limits.cpu}' | grep -q '.'"
    run_check "Dapr sidecar memory limits set" "kubectl get pod $BACKEND_POD -n ${NAMESPACE} -o jsonpath='{.spec.containers[1].resources.limits.memory}' | grep -q '.'"
fi

echo ""

# Security
echo -e "${BLUE}=== Security Hardening ===${NC}"

if [ -n "$BACKEND_POD" ]; then
    run_check "Pod runs as non-root" "kubectl get pod $BACKEND_POD -n ${NAMESPACE} -o jsonpath='{.spec.securityContext.runAsNonRoot}' | grep -q 'true'"
    run_check "Container privilege escalation disabled" "kubectl get pod $BACKEND_POD -n ${NAMESPACE} -o jsonpath='{.spec.containers[0].securityContext.allowPrivilegeEscalation}' | grep -q 'false'"
fi

run_check "OCIR pull secret exists" "kubectl get secret ocir-secret -n ${NAMESPACE}"

echo ""

# Health Endpoints
echo -e "${BLUE}=== Health Endpoints ===${NC}"

if [ -n "$BACKEND_POD" ]; then
    run_check "Backend liveness probe" "kubectl get pod $BACKEND_POD -n ${NAMESPACE} -o jsonpath='{.spec.containers[0].livenessProbe}' | grep -q 'httpGet'"
    run_check "Backend readiness probe" "kubectl get pod $BACKEND_POD -n ${NAMESPACE} -o jsonpath='{.spec.containers[0].readinessProbe}' | grep -q 'httpGet'"
fi

FRONTEND_POD=$(kubectl get pod -l app=frontend -n ${NAMESPACE} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -n "$FRONTEND_POD" ]; then
    run_check "Frontend liveness probe" "kubectl get pod $FRONTEND_POD -n ${NAMESPACE} -o jsonpath='{.spec.containers[0].livenessProbe}' | grep -q 'httpGet'"
    run_check "Frontend readiness probe" "kubectl get pod $FRONTEND_POD -n ${NAMESPACE} -o jsonpath='{.spec.containers[0].readinessProbe}' | grep -q 'httpGet'"
fi

echo ""

# Functional Test
echo -e "${BLUE}=== Functional Test ===${NC}"

if [ -n "$BACKEND_POD" ]; then
    # Port-forward backend
    kubectl port-forward -n ${NAMESPACE} $BACKEND_POD 8000:8000 &>/dev/null &
    PF_PID=$!
    sleep 5

    # Health check
    if curl -sf http://localhost:8000/health &>/dev/null; then
        echo -e "Backend health endpoint... ${GREEN}✅ PASS${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "Backend health endpoint... ${RED}❌ FAIL${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    # Create task
    TEST_RESPONSE=$(curl -sf -X POST http://localhost:8000/api/v1/events/tasks \
        -H "Content-Type: application/json" \
        -d '{"userId":"oke-test","title":"OKE Validation Test","priority":"high"}' 2>/dev/null || echo "")

    if [ -n "$TEST_RESPONSE" ] && echo "$TEST_RESPONSE" | grep -q '"id"'; then
        echo -e "Create task API... ${GREEN}✅ PASS${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "Create task API... ${RED}❌ FAIL${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    # Cleanup
    kill $PF_PID 2>/dev/null || true
fi

echo ""

# Summary
echo "=== Validation Summary ==="
echo "Total Checks: ${TOTAL_CHECKS}"
echo -e "${GREEN}Passed: ${PASSED_CHECKS}${NC}"
echo -e "${RED}Failed: ${FAILED_CHECKS}${NC}"
echo ""

PASS_RATE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
echo "Pass Rate: ${PASS_RATE}%"
echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}✅ All production validation checks passed!${NC}"
    echo "OKE deployment is production-ready."
    exit 0
elif [ $PASS_RATE -ge 90 ]; then
    echo -e "${YELLOW}⚠️  ${FAILED_CHECKS} checks failed but pass rate is ${PASS_RATE}%${NC}"
    echo "Review failures and determine if they are acceptable for production."
    exit 0
else
    echo -e "${RED}❌ Too many validation checks failed (${PASS_RATE}% pass rate)${NC}"
    echo "OKE deployment is NOT production-ready."
    echo ""
    echo "Review failures and fix issues before deploying to production."
    exit 1
fi
