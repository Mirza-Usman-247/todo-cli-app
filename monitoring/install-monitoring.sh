#!/bin/bash
# Install Complete Monitoring Stack on OKE (T114-T121)
# Prometheus + Grafana + Fluent Bit for observability

set -e

echo "=== Installing Monitoring Stack on OKE ==="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
NAMESPACE=${MONITORING_NAMESPACE:-"monitoring"}

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

# Create monitoring namespace
echo -e "${BLUE}Step 2: Creating monitoring namespace...${NC}"
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✅ Namespace created${NC}"
echo ""

# Add Helm repositories
echo -e "${BLUE}Step 3: Adding Helm repositories...${NC}"

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add fluent https://fluent.github.io/helm-charts
helm repo update

echo -e "${GREEN}✅ Helm repositories added${NC}"
echo ""

# Install Prometheus
echo -e "${BLUE}Step 4: Installing Prometheus...${NC}"

if helm list -n ${NAMESPACE} | grep -q "^prometheus"; then
    echo "Upgrading existing Prometheus installation..."
    helm upgrade prometheus prometheus-community/prometheus \
        --namespace ${NAMESPACE} \
        --values monitoring/prometheus/prometheus-values.yaml \
        --wait
else
    echo "Installing Prometheus..."
    helm install prometheus prometheus-community/prometheus \
        --namespace ${NAMESPACE} \
        --values monitoring/prometheus/prometheus-values.yaml \
        --wait
fi

echo -e "${GREEN}✅ Prometheus installed${NC}"
echo ""

# Install Grafana
echo -e "${BLUE}Step 5: Installing Grafana...${NC}"

if helm list -n ${NAMESPACE} | grep -q "^grafana"; then
    echo "Upgrading existing Grafana installation..."
    helm upgrade grafana grafana/grafana \
        --namespace ${NAMESPACE} \
        --values monitoring/grafana/grafana-values.yaml \
        --wait
else
    echo "Installing Grafana..."
    helm install grafana grafana/grafana \
        --namespace ${NAMESPACE} \
        --values monitoring/grafana/grafana-values.yaml \
        --wait
fi

echo -e "${GREEN}✅ Grafana installed${NC}"
echo ""

# Install Fluent Bit
echo -e "${BLUE}Step 6: Installing Fluent Bit...${NC}"

if helm list -n ${NAMESPACE} | grep -q "^fluent-bit"; then
    echo "Upgrading existing Fluent Bit installation..."
    helm upgrade fluent-bit fluent/fluent-bit \
        --namespace ${NAMESPACE} \
        --values monitoring/fluent-bit/fluent-bit-values.yaml \
        --wait
else
    echo "Installing Fluent Bit..."
    helm install fluent-bit fluent/fluent-bit \
        --namespace ${NAMESPACE} \
        --values monitoring/fluent-bit/fluent-bit-values.yaml \
        --wait
fi

echo -e "${GREEN}✅ Fluent Bit installed${NC}"
echo ""

# Optional: Install Loki for log aggregation
echo -e "${BLUE}Step 7: Installing Loki (optional)...${NC}"

read -p "Install Loki for log aggregation? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if helm list -n ${NAMESPACE} | grep -q "^loki"; then
        echo "Upgrading existing Loki installation..."
        helm upgrade loki grafana/loki \
            --namespace ${NAMESPACE} \
            --set persistence.enabled=true \
            --set persistence.storageClassName=oci-bv \
            --set persistence.size=20Gi \
            --wait
    else
        echo "Installing Loki..."
        helm install loki grafana/loki \
            --namespace ${NAMESPACE} \
            --set persistence.enabled=true \
            --set persistence.storageClassName=oci-bv \
            --set persistence.size=20Gi \
            --wait
    fi
    echo -e "${GREEN}✅ Loki installed${NC}"
else
    echo "Skipping Loki installation"
fi
echo ""

# Verify installation
echo -e "${BLUE}Step 8: Verifying installation...${NC}"

echo "Checking pods..."
kubectl get pods -n ${NAMESPACE}

echo ""
echo "Checking services..."
kubectl get svc -n ${NAMESPACE}

echo ""

# Get Grafana admin password
echo -e "${BLUE}Step 9: Retrieving Grafana credentials...${NC}"

GRAFANA_PASSWORD=$(kubectl get secret -n ${NAMESPACE} grafana -o jsonpath="{.data.admin-password}" | base64 --decode)

echo -e "${GREEN}✅ Monitoring stack installed successfully!${NC}"
echo ""

# Access information
echo "=== Access Information ==="
echo ""
echo "Prometheus:"
echo "  kubectl port-forward -n ${NAMESPACE} svc/prometheus-server 9090:80"
echo "  Open: http://localhost:9090"
echo ""
echo "Grafana:"
echo "  kubectl port-forward -n ${NAMESPACE} svc/grafana 3000:80"
echo "  Open: http://localhost:3000"
echo "  Username: admin"
echo "  Password: ${GRAFANA_PASSWORD}"
echo ""
echo "Alertmanager:"
echo "  kubectl port-forward -n ${NAMESPACE} svc/prometheus-alertmanager 9093:80"
echo "  Open: http://localhost:9093"
echo ""

# Dashboard URLs
echo "=== Grafana Dashboards ==="
echo "1. Dapr System Services"
echo "2. Dapr Actors"
echo "3. Dapr Sidecars"
echo "4. Todo App - Events & Tasks (custom)"
echo ""

# Next steps
echo "=== Next Steps ==="
echo "1. Configure alert notifications in Prometheus Alertmanager"
echo "2. Import additional custom dashboards in Grafana"
echo "3. Configure OCI Logging integration for long-term log retention"
echo "4. Set up uptime monitoring and synthetic tests"
echo ""
