#!/bin/bash
# Verify Dapr Sidecar Injection (T086)
# Checks that Dapr sidecars are properly injected into application pods

set -e

echo "=== Dapr Sidecar Verification ==="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

TOTAL_CHECKS=0
PASSED_CHECKS=0

# Function to check pod containers
check_pod_containers() {
    local app_label=$1
    local expected_app_container=$2
    local pod_name=$(kubectl get pod -l app=${app_label} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -z "$pod_name" ]; then
        echo -e "${RED}❌ No pod found with label app=${app_label}${NC}"
        return 1
    fi

    echo -e "${BLUE}Checking pod: ${pod_name}${NC}"

    # Check if pod is running
    pod_status=$(kubectl get pod ${pod_name} -o jsonpath='{.status.phase}')
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [ "$pod_status" == "Running" ]; then
        echo -e "${GREEN}✅ Pod is running${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}❌ Pod status: ${pod_status}${NC}"
    fi

    # Check container count (should be 2: app + daprd)
    container_count=$(kubectl get pod ${pod_name} -o jsonpath='{.spec.containers[*].name}' | wc -w)
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [ "$container_count" -eq 2 ]; then
        echo -e "${GREEN}✅ Found 2 containers (app + daprd)${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}❌ Expected 2 containers, found ${container_count}${NC}"
    fi

    # Check for daprd container
    daprd_exists=$(kubectl get pod ${pod_name} -o jsonpath='{.spec.containers[*].name}' | grep -o "daprd" || echo "")
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [ -n "$daprd_exists" ]; then
        echo -e "${GREEN}✅ daprd sidecar container found${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}❌ daprd sidecar container not found${NC}"
    fi

    # Check for application container
    app_exists=$(kubectl get pod ${pod_name} -o jsonpath='{.spec.containers[*].name}' | grep -o "${expected_app_container}" || echo "")
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [ -n "$app_exists" ]; then
        echo -e "${GREEN}✅ Application container '${expected_app_container}' found${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}❌ Application container '${expected_app_container}' not found${NC}"
    fi

    # Check Dapr annotations
    echo ""
    echo "Dapr Annotations:"
    kubectl get pod ${pod_name} -o jsonpath='{.metadata.annotations}' | jq 'with_entries(select(.key | startswith("dapr.io/")))'

    # Check container readiness
    echo ""
    echo "Container Status:"
    kubectl get pod ${pod_name} -o jsonpath='{range .status.containerStatuses[*]}{.name}{"\t"}{.ready}{"\t"}{.state}{"\n"}{end}' | while IFS=$'\t' read -r name ready state; do
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        if [[ "$ready" == "true" ]]; then
            echo -e "${GREEN}✅ ${name}: ready${NC}"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            echo -e "${RED}❌ ${name}: not ready - ${state}${NC}"
        fi
    done

    echo ""
}

# Check backend pod
echo "=== Backend Pod ==="
check_pod_containers "backend" "backend"
echo ""

# Check frontend pod
echo "=== Frontend Pod ==="
check_pod_containers "frontend" "frontend"
echo ""

# Check Dapr components
echo "=== Dapr Components ==="
components=$(kubectl get components -o json | jq -r '.items[].metadata.name')

for comp in $components; do
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    echo -e "${GREEN}✅ Component: ${comp}${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
done
echo ""

# Check Dapr subscriptions
echo "=== Dapr Subscriptions ==="
subscriptions=$(kubectl get subscriptions -o json | jq -r '.items[].metadata.name')

for sub in $subscriptions; do
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    echo -e "${GREEN}✅ Subscription: ${sub}${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
done
echo ""

# Test Dapr sidecar health
echo "=== Dapr Sidecar Health Check ==="

for app_label in backend frontend; do
    pod_name=$(kubectl get pod -l app=${app_label} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -z "$pod_name" ]; then
        continue
    fi

    echo "Checking Dapr sidecar in ${pod_name}..."

    # Check Dapr health endpoint
    health_check=$(kubectl exec ${pod_name} -c daprd -- curl -s http://localhost:3500/v1.0/healthz/outbound || echo "FAIL")
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [[ "$health_check" == *"true"* ]]; then
        echo -e "${GREEN}✅ Dapr sidecar is healthy${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}❌ Dapr sidecar health check failed${NC}"
    fi

    echo ""
done

# Summary
echo "=== Verification Summary ==="
echo "Total checks: ${TOTAL_CHECKS}"
echo "Passed: ${PASSED_CHECKS}"
echo "Failed: $((TOTAL_CHECKS - PASSED_CHECKS))"
echo ""

if [ $PASSED_CHECKS -eq $TOTAL_CHECKS ]; then
    echo -e "${GREEN}✅ All Dapr sidecar checks passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some checks failed. See details above.${NC}"
    exit 1
fi
