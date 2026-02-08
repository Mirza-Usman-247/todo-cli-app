#!/bin/bash
# Provision Oracle Kubernetes Engine (OKE) Cluster (T094, T095)
# Creates OKE cluster with required configuration for Phase 5 deployment

set -e

echo "=== Provisioning OKE Cluster for Todo App Phase 5 ==="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
COMPARTMENT_ID=${OCI_COMPARTMENT_ID:-""}
CLUSTER_NAME=${OKE_CLUSTER_NAME:-"todo-app-phase5"}
KUBERNETES_VERSION=${OKE_K8S_VERSION:-"v1.28.2"}
NODE_POOL_NAME="${CLUSTER_NAME}-nodepool"
NODE_COUNT=${OKE_NODE_COUNT:-3}
NODE_SHAPE=${OKE_NODE_SHAPE:-"VM.Standard.E4.Flex"}
NODE_OCPUS=${OKE_NODE_OCPUS:-2}
NODE_MEMORY_GB=${OKE_NODE_MEMORY_GB:-16}
VCN_NAME="${CLUSTER_NAME}-vcn"
REGION=${OCI_REGION:-"us-ashburn-1"}

# Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

if ! command -v oci &> /dev/null; then
    echo -e "${RED}❌ OCI CLI not found${NC}"
    echo "Install: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found${NC}"
    exit 1
fi

if [ -z "$COMPARTMENT_ID" ]; then
    echo -e "${RED}❌ OCI_COMPARTMENT_ID environment variable not set${NC}"
    echo "Set it with: export OCI_COMPARTMENT_ID=<your-compartment-ocid>"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites satisfied${NC}"
echo ""

# Display configuration
echo -e "${BLUE}Cluster Configuration:${NC}"
echo "  Compartment ID: ${COMPARTMENT_ID}"
echo "  Cluster Name: ${CLUSTER_NAME}"
echo "  Kubernetes Version: ${KUBERNETES_VERSION}"
echo "  Region: ${REGION}"
echo "  Node Count: ${NODE_COUNT}"
echo "  Node Shape: ${NODE_SHAPE} (${NODE_OCPUS} OCPUs, ${NODE_MEMORY_GB}GB RAM)"
echo ""

read -p "Proceed with cluster creation? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted"
    exit 1
fi

# Step 2: Create VCN if not exists
echo -e "${BLUE}Step 2: Creating Virtual Cloud Network (VCN)...${NC}"

VCN_ID=$(oci network vcn list \
    --compartment-id "$COMPARTMENT_ID" \
    --display-name "$VCN_NAME" \
    --query 'data[0].id' \
    --raw-output 2>/dev/null || echo "")

if [ -z "$VCN_ID" ] || [ "$VCN_ID" == "null" ]; then
    echo "Creating new VCN..."
    VCN_ID=$(oci network vcn create \
        --compartment-id "$COMPARTMENT_ID" \
        --display-name "$VCN_NAME" \
        --cidr-block "10.0.0.0/16" \
        --dns-label "${CLUSTER_NAME//-/}" \
        --query 'data.id' \
        --raw-output)

    echo "Waiting for VCN to be available..."
    oci network vcn get --vcn-id "$VCN_ID" --wait-for-state AVAILABLE
    echo -e "${GREEN}✅ VCN created: ${VCN_ID}${NC}"
else
    echo -e "${GREEN}✅ Using existing VCN: ${VCN_ID}${NC}"
fi
echo ""

# Step 3: Create Internet Gateway
echo -e "${BLUE}Step 3: Creating Internet Gateway...${NC}"

IGW_ID=$(oci network internet-gateway list \
    --compartment-id "$COMPARTMENT_ID" \
    --vcn-id "$VCN_ID" \
    --query 'data[0].id' \
    --raw-output 2>/dev/null || echo "")

if [ -z "$IGW_ID" ] || [ "$IGW_ID" == "null" ]; then
    IGW_ID=$(oci network internet-gateway create \
        --compartment-id "$COMPARTMENT_ID" \
        --vcn-id "$VCN_ID" \
        --is-enabled true \
        --display-name "${CLUSTER_NAME}-igw" \
        --query 'data.id' \
        --raw-output)

    echo -e "${GREEN}✅ Internet Gateway created: ${IGW_ID}${NC}"
else
    echo -e "${GREEN}✅ Using existing Internet Gateway: ${IGW_ID}${NC}"
fi
echo ""

# Step 4: Create Route Table
echo -e "${BLUE}Step 4: Configuring Route Table...${NC}"

ROUTE_TABLE_ID=$(oci network route-table list \
    --compartment-id "$COMPARTMENT_ID" \
    --vcn-id "$VCN_ID" \
    --query 'data[0].id' \
    --raw-output 2>/dev/null || echo "")

if [ -n "$ROUTE_TABLE_ID" ] && [ "$ROUTE_TABLE_ID" != "null" ]; then
    oci network route-table update \
        --rt-id "$ROUTE_TABLE_ID" \
        --route-rules "[{\"destination\": \"0.0.0.0/0\", \"networkEntityId\": \"$IGW_ID\"}]" \
        --force

    echo -e "${GREEN}✅ Route table updated${NC}"
else
    echo -e "${YELLOW}⚠️  Could not find route table${NC}"
fi
echo ""

# Step 5: Create Subnets
echo -e "${BLUE}Step 5: Creating Subnets...${NC}"

# Kubernetes API subnet
K8S_API_SUBNET_ID=$(oci network subnet list \
    --compartment-id "$COMPARTMENT_ID" \
    --vcn-id "$VCN_ID" \
    --display-name "${CLUSTER_NAME}-k8s-api-subnet" \
    --query 'data[0].id' \
    --raw-output 2>/dev/null || echo "")

if [ -z "$K8S_API_SUBNET_ID" ] || [ "$K8S_API_SUBNET_ID" == "null" ]; then
    K8S_API_SUBNET_ID=$(oci network subnet create \
        --compartment-id "$COMPARTMENT_ID" \
        --vcn-id "$VCN_ID" \
        --display-name "${CLUSTER_NAME}-k8s-api-subnet" \
        --cidr-block "10.0.1.0/24" \
        --route-table-id "$ROUTE_TABLE_ID" \
        --query 'data.id' \
        --raw-output)

    echo -e "${GREEN}✅ K8s API subnet created${NC}"
else
    echo -e "${GREEN}✅ Using existing K8s API subnet${NC}"
fi

# Worker nodes subnet
WORKER_SUBNET_ID=$(oci network subnet list \
    --compartment-id "$COMPARTMENT_ID" \
    --vcn-id "$VCN_ID" \
    --display-name "${CLUSTER_NAME}-worker-subnet" \
    --query 'data[0].id' \
    --raw-output 2>/dev/null || echo "")

if [ -z "$WORKER_SUBNET_ID" ] || [ "$WORKER_SUBNET_ID" == "null" ]; then
    WORKER_SUBNET_ID=$(oci network subnet create \
        --compartment-id "$COMPARTMENT_ID" \
        --vcn-id "$VCN_ID" \
        --display-name "${CLUSTER_NAME}-worker-subnet" \
        --cidr-block "10.0.10.0/24" \
        --route-table-id "$ROUTE_TABLE_ID" \
        --query 'data.id' \
        --raw-output)

    echo -e "${GREEN}✅ Worker subnet created${NC}"
else
    echo -e "${GREEN}✅ Using existing worker subnet${NC}"
fi

# Load balancer subnet
LB_SUBNET_ID=$(oci network subnet list \
    --compartment-id "$COMPARTMENT_ID" \
    --vcn-id "$VCN_ID" \
    --display-name "${CLUSTER_NAME}-lb-subnet" \
    --query 'data[0].id' \
    --raw-output 2>/dev/null || echo "")

if [ -z "$LB_SUBNET_ID" ] || [ "$LB_SUBNET_ID" == "null" ]; then
    LB_SUBNET_ID=$(oci network subnet create \
        --compartment-id "$COMPARTMENT_ID" \
        --vcn-id "$VCN_ID" \
        --display-name "${CLUSTER_NAME}-lb-subnet" \
        --cidr-block "10.0.20.0/24" \
        --route-table-id "$ROUTE_TABLE_ID" \
        --query 'data.id' \
        --raw-output)

    echo -e "${GREEN}✅ Load balancer subnet created${NC}"
else
    echo -e "${GREEN}✅ Using existing load balancer subnet${NC}"
fi
echo ""

# Step 6: Create OKE Cluster
echo -e "${BLUE}Step 6: Creating OKE cluster...${NC}"

CLUSTER_ID=$(oci ce cluster list \
    --compartment-id "$COMPARTMENT_ID" \
    --name "$CLUSTER_NAME" \
    --query 'data[0].id' \
    --raw-output 2>/dev/null || echo "")

if [ -z "$CLUSTER_ID" ] || [ "$CLUSTER_ID" == "null" ]; then
    echo "Creating OKE cluster (this may take 5-10 minutes)..."

    CLUSTER_ID=$(oci ce cluster create \
        --compartment-id "$COMPARTMENT_ID" \
        --name "$CLUSTER_NAME" \
        --vcn-id "$VCN_ID" \
        --kubernetes-version "$KUBERNETES_VERSION" \
        --endpoint-subnet-id "$K8S_API_SUBNET_ID" \
        --service-lb-subnet-ids "[\"$LB_SUBNET_ID\"]" \
        --wait-for-state SUCCEEDED \
        --query 'data.resources[0].identifier' \
        --raw-output)

    echo -e "${GREEN}✅ OKE cluster created: ${CLUSTER_ID}${NC}"
else
    echo -e "${GREEN}✅ Using existing OKE cluster: ${CLUSTER_ID}${NC}"
fi
echo ""

# Step 7: Create Node Pool
echo -e "${BLUE}Step 7: Creating node pool...${NC}"

NODE_POOL_ID=$(oci ce node-pool list \
    --compartment-id "$COMPARTMENT_ID" \
    --cluster-id "$CLUSTER_ID" \
    --name "$NODE_POOL_NAME" \
    --query 'data[0].id' \
    --raw-output 2>/dev/null || echo "")

if [ -z "$NODE_POOL_ID" ] || [ "$NODE_POOL_ID" == "null" ]; then
    echo "Creating node pool (this may take 5-10 minutes)..."

    NODE_POOL_ID=$(oci ce node-pool create \
        --compartment-id "$COMPARTMENT_ID" \
        --cluster-id "$CLUSTER_ID" \
        --name "$NODE_POOL_NAME" \
        --kubernetes-version "$KUBERNETES_VERSION" \
        --node-shape "$NODE_SHAPE" \
        --node-shape-config "{\"ocpus\": ${NODE_OCPUS}, \"memoryInGBs\": ${NODE_MEMORY_GB}}" \
        --size "$NODE_COUNT" \
        --placement-configs "[{\"availabilityDomain\": \"$(oci iam availability-domain list --compartment-id $COMPARTMENT_ID --query 'data[0].name' --raw-output)\", \"subnetId\": \"$WORKER_SUBNET_ID\"}]" \
        --wait-for-state SUCCEEDED \
        --query 'data.resources[0].identifier' \
        --raw-output)

    echo -e "${GREEN}✅ Node pool created: ${NODE_POOL_ID}${NC}"
else
    echo -e "${GREEN}✅ Using existing node pool: ${NODE_POOL_ID}${NC}"
fi
echo ""

# Step 8: Configure kubectl
echo -e "${BLUE}Step 8: Configuring kubectl...${NC}"

mkdir -p ~/.kube

oci ce cluster create-kubeconfig \
    --cluster-id "$CLUSTER_ID" \
    --file ~/.kube/config-oke \
    --region "$REGION" \
    --token-version 2.0.0 \
    --kube-endpoint PUBLIC_ENDPOINT

# Merge with existing kubeconfig
if [ -f ~/.kube/config ]; then
    KUBECONFIG=~/.kube/config:~/.kube/config-oke kubectl config view --flatten > ~/.kube/config-merged
    mv ~/.kube/config-merged ~/.kube/config
else
    mv ~/.kube/config-oke ~/.kube/config
fi

kubectl config use-context $(kubectl config get-contexts -o name | grep $CLUSTER_NAME | head -1)

echo -e "${GREEN}✅ kubectl configured${NC}"
echo ""

# Verify cluster access
echo -e "${BLUE}Step 9: Verifying cluster access...${NC}"
kubectl cluster-info
kubectl get nodes
echo ""

echo -e "${GREEN}✅ OKE Cluster provisioned successfully!${NC}"
echo ""
echo "=== Cluster Information ==="
echo "Cluster ID: ${CLUSTER_ID}"
echo "Node Pool ID: ${NODE_POOL_ID}"
echo "VCN ID: ${VCN_ID}"
echo "Region: ${REGION}"
echo ""
echo "=== Next Steps ==="
echo "1. Install Dapr: dapr init --kubernetes --wait"
echo "2. Deploy managed Kafka: ./scripts/setup-managed-kafka.sh"
echo "3. Deploy application: helm install todo-app ./helm/todo-app-phase5 -f values-oke.yaml"
echo ""
