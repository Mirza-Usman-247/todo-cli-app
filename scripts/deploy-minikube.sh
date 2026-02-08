#!/bin/bash
# Deploy Todo App Phase 5 to Minikube (T085)
# Full deployment: Kafka, Dapr, Redis, Application

set -e

echo "=== Phase 5: Event-Driven Todo App - Minikube Deployment ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

command -v minikube >/dev/null 2>&1 || { echo -e "${RED}❌ minikube not found${NC}"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}❌ kubectl not found${NC}"; exit 1; }
command -v helm >/dev/null 2>&1 || { echo -e "${RED}❌ helm not found${NC}"; exit 1; }
command -v dapr >/dev/null 2>&1 || { echo -e "${RED}❌ dapr CLI not found${NC}"; exit 1; }

echo -e "${GREEN}✅ All prerequisites found${NC}"
echo ""

# Start Minikube if not running
echo -e "${BLUE}Step 2: Ensuring Minikube is running...${NC}"
if ! minikube status &>/dev/null; then
    echo "Starting Minikube..."
    minikube start --cpus=4 --memory=8192 --driver=docker
else
    echo -e "${GREEN}✅ Minikube already running${NC}"
fi

minikube status
echo ""

# Set Docker env to Minikube
echo -e "${BLUE}Step 3: Configuring Docker environment...${NC}"
eval $(minikube docker-env)
echo -e "${GREEN}✅ Docker environment set to Minikube${NC}"
echo ""

# Install Strimzi Kafka Operator
echo -e "${BLUE}Step 4: Installing Strimzi Kafka Operator...${NC}"
kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -

if ! kubectl get deployment strimzi-cluster-operator -n kafka &>/dev/null; then
    echo "Installing Strimzi operator..."
    kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

    echo "Waiting for operator to be ready..."
    kubectl wait deployment/strimzi-cluster-operator \
        --for=condition=Available --timeout=300s -n kafka
else
    echo -e "${GREEN}✅ Strimzi operator already installed${NC}"
fi
echo ""

# Deploy Kafka cluster
echo -e "${BLUE}Step 5: Deploying Kafka cluster...${NC}"

if [ ! -f "kafka/strimzi/kafka-cluster.yaml" ]; then
    echo -e "${YELLOW}Creating Kafka cluster configuration...${NC}"
    mkdir -p kafka/strimzi
    cat > kafka/strimzi/kafka-cluster.yaml <<EOF
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: my-cluster
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
      inter.broker.protocol.version: "3.6"
    storage:
      type: ephemeral
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
  entityOperator:
    topicOperator: {}
    userOperator: {}
EOF
fi

if ! kubectl get kafka my-cluster -n kafka &>/dev/null; then
    echo "Deploying Kafka cluster..."
    kubectl apply -f kafka/strimzi/kafka-cluster.yaml -n kafka

    echo "Waiting for Kafka cluster to be ready (this may take 5-10 minutes)..."
    kubectl wait kafka/my-cluster --for=condition=Ready --timeout=600s -n kafka
else
    echo -e "${GREEN}✅ Kafka cluster already deployed${NC}"
fi
echo ""

# Create Kafka topics
echo -e "${BLUE}Step 6: Creating Kafka topics...${NC}"

KAFKA_POD=$(kubectl get pod -n kafka -l app.kubernetes.io/name=kafka -o jsonpath='{.items[0].metadata.name}')

for topic in todo-created todo-updated todo-deleted todo-reminder; do
    if kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
        --bootstrap-server my-cluster-kafka-bootstrap:9092 \
        --list | grep -q "^${topic}$"; then
        echo -e "${GREEN}✅ Topic ${topic} already exists${NC}"
    else
        echo "Creating topic: ${topic}"
        kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
            --bootstrap-server my-cluster-kafka-bootstrap:9092 \
            --create --topic ${topic} --partitions 1 --replication-factor 1
    fi
done
echo ""

# Install Dapr control plane
echo -e "${BLUE}Step 7: Installing Dapr control plane...${NC}"

if ! kubectl get namespace dapr-system &>/dev/null; then
    echo "Initializing Dapr in Kubernetes..."
    dapr init --kubernetes --wait
else
    echo -e "${GREEN}✅ Dapr already installed${NC}"
fi

kubectl get pods -n dapr-system
echo ""

# Install Redis
echo -e "${BLUE}Step 8: Installing Redis state store...${NC}"

if ! helm list | grep -q "^redis"; then
    echo "Adding Bitnami Helm repo..."
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo update

    echo "Installing Redis..."
    helm install redis bitnami/redis \
        --set auth.enabled=false \
        --set master.persistence.enabled=false \
        --set replica.replicaCount=0

    echo "Waiting for Redis to be ready..."
    kubectl wait pod -l app.kubernetes.io/name=redis --for=condition=Ready --timeout=300s
else
    echo -e "${GREEN}✅ Redis already installed${NC}"
fi
echo ""

# Build Docker images
echo -e "${BLUE}Step 9: Building Docker images...${NC}"

echo "Building backend image..."
cd backend
docker build -t todo-backend:phase5 .
cd ..

echo "Building frontend image..."
cd frontend
docker build -t todo-frontend:phase5 -f ../docker/frontend/Dockerfile .
cd ..

echo -e "${GREEN}✅ Docker images built${NC}"
echo ""

# Deploy application with Helm
echo -e "${BLUE}Step 10: Deploying application with Helm...${NC}"

if helm list | grep -q "^todo-app"; then
    echo "Upgrading existing release..."
    helm upgrade todo-app ./helm/todo-app-phase5 \
        --namespace default \
        --wait
else
    echo "Installing new release..."
    helm install todo-app ./helm/todo-app-phase5 \
        --namespace default \
        --wait
fi

echo -e "${GREEN}✅ Application deployed${NC}"
echo ""

# Verify deployment
echo -e "${BLUE}Step 11: Verifying deployment...${NC}"

echo "Checking pods..."
kubectl get pods

echo ""
echo "Checking Dapr components..."
kubectl get components

echo ""
echo "Checking Dapr subscriptions..."
kubectl get subscriptions

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "=== Access Information ==="
echo ""
echo "Frontend URL:"
minikube service todo-app-frontend --url
echo ""
echo "Backend API (use port-forward):"
echo "  kubectl port-forward svc/todo-app-backend 8000:8000"
echo ""
echo "=== Next Steps ==="
echo "1. Run E2E tests: python backend/tests/e2e/test_event_flow_create.py"
echo "2. Inspect Kafka topics: ./scripts/inspect-kafka-topics.sh"
echo "3. View logs: kubectl logs -l app=backend -c backend --tail=50 -f"
echo ""
