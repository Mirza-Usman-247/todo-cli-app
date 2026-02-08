#!/bin/bash
# Setup Redis Cluster on OKE with Persistence (T100)
# Production-ready Redis deployment for State Store

set -e

echo "=== Setting up Redis Cluster on OKE ==="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
REDIS_NAMESPACE=${REDIS_NAMESPACE:-"default"}
REDIS_REPLICAS=${REDIS_REPLICAS:-3}
REDIS_PASSWORD=${REDIS_PASSWORD:-$(openssl rand -base64 32)}
REDIS_STORAGE_CLASS=${REDIS_STORAGE_CLASS:-"oci-bv"}  # OCI Block Volume
REDIS_STORAGE_SIZE=${REDIS_STORAGE_SIZE:-"10Gi"}

# Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

if ! command -v helm &> /dev/null; then
    echo -e "${RED}❌ helm not found${NC}"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites satisfied${NC}"
echo ""

# Display configuration
echo -e "${BLUE}Redis Configuration:${NC}"
echo "  Namespace: ${REDIS_NAMESPACE}"
echo "  Replicas: ${REDIS_REPLICAS}"
echo "  Storage Class: ${REDIS_STORAGE_CLASS}"
echo "  Storage Size: ${REDIS_STORAGE_SIZE}"
echo ""

# Add Bitnami Helm repo
echo -e "${BLUE}Step 2: Adding Bitnami Helm repository...${NC}"

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

echo -e "${GREEN}✅ Helm repository updated${NC}"
echo ""

# Create namespace if not exists
kubectl create namespace ${REDIS_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Install Redis cluster
echo -e "${BLUE}Step 3: Installing Redis cluster...${NC}"

if helm list -n ${REDIS_NAMESPACE} | grep -q "^redis"; then
    echo -e "${YELLOW}⚠️  Redis already installed${NC}"
    read -p "Upgrade existing installation? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping Redis installation"
        exit 0
    fi
    HELM_COMMAND="upgrade"
else
    HELM_COMMAND="install"
fi

helm ${HELM_COMMAND} redis bitnami/redis \
    --namespace ${REDIS_NAMESPACE} \
    --set auth.enabled=true \
    --set auth.password="${REDIS_PASSWORD}" \
    --set architecture=replication \
    --set master.persistence.enabled=true \
    --set master.persistence.storageClass="${REDIS_STORAGE_CLASS}" \
    --set master.persistence.size="${REDIS_STORAGE_SIZE}" \
    --set master.resources.requests.cpu=250m \
    --set master.resources.requests.memory=256Mi \
    --set master.resources.limits.cpu=1000m \
    --set master.resources.limits.memory=512Mi \
    --set replica.replicaCount=${REDIS_REPLICAS} \
    --set replica.persistence.enabled=true \
    --set replica.persistence.storageClass="${REDIS_STORAGE_CLASS}" \
    --set replica.persistence.size="${REDIS_STORAGE_SIZE}" \
    --set replica.resources.requests.cpu=250m \
    --set replica.resources.requests.memory=256Mi \
    --set replica.resources.limits.cpu=1000m \
    --set replica.resources.limits.memory=512Mi \
    --set metrics.enabled=true \
    --set sentinel.enabled=true \
    --wait

echo -e "${GREEN}✅ Redis cluster ${HELM_COMMAND}d${NC}"
echo ""

# Create Kubernetes Secret for Redis password
echo -e "${BLUE}Step 4: Creating Kubernetes Secret for Redis password...${NC}"

kubectl create secret generic redis-credentials \
    --from-literal=redis-password="${REDIS_PASSWORD}" \
    --namespace ${REDIS_NAMESPACE} \
    --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✅ Redis credentials secret created${NC}"
echo ""

# Wait for Redis to be ready
echo -e "${BLUE}Step 5: Waiting for Redis to be ready...${NC}"

kubectl wait pod -l app.kubernetes.io/name=redis \
    --for=condition=Ready \
    --timeout=300s \
    --namespace ${REDIS_NAMESPACE}

echo -e "${GREEN}✅ Redis is ready${NC}"
echo ""

# Verify installation
echo -e "${BLUE}Step 6: Verifying Redis installation...${NC}"

echo "Redis pods:"
kubectl get pods -l app.kubernetes.io/name=redis -n ${REDIS_NAMESPACE}

echo ""
echo "Redis services:"
kubectl get svc -l app.kubernetes.io/name=redis -n ${REDIS_NAMESPACE}

echo ""
echo "Persistent volumes:"
kubectl get pvc -l app.kubernetes.io/name=redis -n ${REDIS_NAMESPACE}

echo ""

# Test connection
echo -e "${BLUE}Step 7: Testing Redis connection...${NC}"

REDIS_MASTER_POD=$(kubectl get pod -l app.kubernetes.io/name=redis,app.kubernetes.io/component=master -n ${REDIS_NAMESPACE} -o jsonpath='{.items[0].metadata.name}')

kubectl exec -n ${REDIS_NAMESPACE} ${REDIS_MASTER_POD} -- redis-cli -a "${REDIS_PASSWORD}" ping

echo -e "${GREEN}✅ Redis connection verified${NC}"
echo ""

# Create Dapr State Store component
echo -e "${BLUE}Step 8: Creating Dapr State Store component...${NC}"

cat > /tmp/dapr-statestore-redis.yaml <<EOF
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-redis
  namespace: ${REDIS_NAMESPACE}
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: redis-master.${REDIS_NAMESPACE}.svc.cluster.local:6379
  - name: redisPassword
    secretKeyRef:
      name: redis-credentials
      key: redis-password
  - name: actorStateStore
    value: "true"
  - name: keyPrefix
    value: "name"
  - name: enableTLS
    value: "false"
EOF

kubectl apply -f /tmp/dapr-statestore-redis.yaml

echo -e "${GREEN}✅ Dapr State Store component created${NC}"
echo ""

echo -e "${GREEN}✅ Redis cluster setup complete!${NC}"
echo ""
echo "=== Connection Information ==="
echo "Master endpoint: redis-master.${REDIS_NAMESPACE}.svc.cluster.local:6379"
echo "Password: ${REDIS_PASSWORD}"
echo ""
echo "=== Save Credentials ==="
echo "Store this password securely! You'll need it for application configuration."
echo ""
echo "# Add to your environment or secrets manager:"
echo "export REDIS_PASSWORD='${REDIS_PASSWORD}'"
echo ""
echo "=== Next Steps ==="
echo "1. Verify Dapr component: kubectl get components -n ${REDIS_NAMESPACE}"
echo "2. Deploy application: helm install todo-app ./helm/todo-app-phase5 -f values-oke.yaml"
echo "3. Test State Store: kubectl exec <app-pod> -c daprd -- curl http://localhost:3500/v1.0/state/statestore-redis"
echo ""
