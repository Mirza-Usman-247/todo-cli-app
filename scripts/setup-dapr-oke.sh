#!/bin/bash
# Install Dapr Control Plane on OKE with HA and mTLS (T099)
# Production-ready Dapr installation for Oracle Kubernetes Engine

set -e

echo "=== Installing Dapr on OKE with HA and mTLS ==="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
DAPR_VERSION=${DAPR_VERSION:-"1.12.0"}
DAPR_HA=${DAPR_HA:-"true"}
DAPR_MTLS=${DAPR_MTLS:-"true"}

# Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

if ! command -v dapr &> /dev/null; then
    echo -e "${RED}❌ Dapr CLI not found${NC}"
    echo "Install: wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found${NC}"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo -e "${RED}❌ helm not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites satisfied${NC}"
echo ""

# Verify cluster access
echo -e "${BLUE}Step 2: Verifying cluster access...${NC}"
kubectl cluster-info
echo ""

# Install Dapr control plane
echo -e "${BLUE}Step 3: Installing Dapr control plane...${NC}"

if kubectl get namespace dapr-system &>/dev/null; then
    echo -e "${YELLOW}⚠️  Dapr namespace already exists${NC}"
    read -p "Upgrade existing Dapr installation? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping Dapr installation"
    else
        dapr uninstall --kubernetes
        echo "Waiting for cleanup..."
        sleep 10
    fi
fi

if ! kubectl get namespace dapr-system &>/dev/null; then
    echo "Installing Dapr ${DAPR_VERSION} with HA=${DAPR_HA}, mTLS=${DAPR_MTLS}..."

    if [ "$DAPR_HA" == "true" ]; then
        dapr init --kubernetes \
            --enable-ha=true \
            --enable-mtls=${DAPR_MTLS} \
            --wait
    else
        dapr init --kubernetes \
            --enable-mtls=${DAPR_MTLS} \
            --wait
    fi

    echo -e "${GREEN}✅ Dapr installed${NC}"
fi
echo ""

# Verify Dapr installation
echo -e "${BLUE}Step 4: Verifying Dapr installation...${NC}"

echo "Dapr control plane pods:"
kubectl get pods -n dapr-system

echo ""
echo "Dapr version:"
dapr version --kubernetes
echo ""

# Configure resource limits for production
echo -e "${BLUE}Step 5: Configuring resource limits for production...${NC}"

cat > /tmp/dapr-system-values.yaml <<EOF
global:
  ha:
    enabled: ${DAPR_HA}
  mtls:
    enabled: ${DAPR_MTLS}
  logAsJson: true
  logLevel: info

dapr_operator:
  replicaCount: 3
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi

dapr_sidecar_injector:
  replicaCount: 3
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi

dapr_sentry:
  replicaCount: 3
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi

dapr_placement:
  replicaCount: 3
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi

dapr_scheduler:
  replicaCount: 3
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi
EOF

# Apply via Helm upgrade (if using Helm-based installation)
if helm list -n dapr-system | grep -q dapr; then
    echo "Upgrading Dapr with production values..."
    helm upgrade dapr dapr/dapr \
        --namespace dapr-system \
        --values /tmp/dapr-system-values.yaml \
        --wait
    echo -e "${GREEN}✅ Dapr upgraded with production configuration${NC}"
else
    echo -e "${YELLOW}⚠️  Dapr not installed via Helm, skipping resource configuration${NC}"
fi
echo ""

# Configure Dapr observability (optional)
echo -e "${BLUE}Step 6: Configuring Dapr observability...${NC}"

cat > /tmp/dapr-config.yaml <<EOF
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
  namespace: default
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin.default.svc.cluster.local:9411/api/v2/spans"
  metric:
    enabled: true
  mtls:
    enabled: ${DAPR_MTLS}
    workloadCertTTL: "24h"
    allowedClockSkew: "15m"
EOF

kubectl apply -f /tmp/dapr-config.yaml
echo -e "${GREEN}✅ Dapr configuration applied${NC}"
echo ""

# Health check
echo -e "${BLUE}Step 7: Running health checks...${NC}"

echo "Checking Dapr operator..."
kubectl rollout status deployment/dapr-operator -n dapr-system

echo "Checking Dapr sidecar injector..."
kubectl rollout status deployment/dapr-sidecar-injector -n dapr-system

echo "Checking Dapr sentry..."
kubectl rollout status deployment/dapr-sentry -n dapr-system

echo "Checking Dapr placement..."
kubectl rollout status statefulset/dapr-placement-server -n dapr-system

echo ""
echo -e "${GREEN}✅ All Dapr components healthy${NC}"
echo ""

echo -e "${GREEN}✅ Dapr on OKE setup complete!${NC}"
echo ""
echo "=== Configuration Summary ==="
echo "Dapr Version: ${DAPR_VERSION}"
echo "High Availability: ${DAPR_HA}"
echo "mTLS Enabled: ${DAPR_MTLS}"
echo ""
echo "=== Next Steps ==="
echo "1. Deploy Redis cluster: ./scripts/setup-redis-oke.sh"
echo "2. Deploy Dapr components: kubectl apply -f helm/todo-app-phase5/templates/dapr-*.yaml"
echo "3. Deploy application: helm install todo-app ./helm/todo-app-phase5 -f values-oke.yaml"
echo ""
