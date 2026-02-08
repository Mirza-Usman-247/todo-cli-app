#!/bin/bash
# Setup Managed Kafka for OKE (T096, T097)
# Configures Redpanda Cloud or Confluent Cloud Kafka

set -e

echo "=== Managed Kafka Setup for OKE ==="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
KAFKA_PROVIDER=${KAFKA_PROVIDER:-"redpanda"}  # or "confluent"
KAFKA_BOOTSTRAP_SERVERS=${KAFKA_BOOTSTRAP_SERVERS:-""}
KAFKA_SASL_USERNAME=${KAFKA_SASL_USERNAME:-""}
KAFKA_SASL_PASSWORD=${KAFKA_SASL_PASSWORD:-""}
KAFKA_SECURITY_PROTOCOL=${KAFKA_SECURITY_PROTOCOL:-"SASL_SSL"}
KAFKA_SASL_MECHANISM=${KAFKA_SASL_MECHANISM:-"SCRAM-SHA-256"}

echo -e "${BLUE}Managed Kafka Provider: ${KAFKA_PROVIDER}${NC}"
echo ""

# Validate configuration
if [ -z "$KAFKA_BOOTSTRAP_SERVERS" ]; then
    echo -e "${RED}❌ KAFKA_BOOTSTRAP_SERVERS environment variable not set${NC}"
    echo ""
    echo "Set it with your managed Kafka endpoint:"
    echo "  export KAFKA_BOOTSTRAP_SERVERS=<your-kafka-bootstrap-servers>"
    echo ""
    echo "Example for Redpanda Cloud:"
    echo "  export KAFKA_BOOTSTRAP_SERVERS=seed-12345.us-east-1.aws.redpanda.com:9092"
    echo ""
    echo "Example for Confluent Cloud:"
    echo "  export KAFKA_BOOTSTRAP_SERVERS=pkc-xxxxx.us-east-1.aws.confluent.cloud:9092"
    echo ""
    exit 1
fi

if [ -z "$KAFKA_SASL_USERNAME" ] || [ -z "$KAFKA_SASL_PASSWORD" ]; then
    echo -e "${RED}❌ KAFKA_SASL_USERNAME and KAFKA_SASL_PASSWORD must be set${NC}"
    echo ""
    echo "Set them with your managed Kafka credentials:"
    echo "  export KAFKA_SASL_USERNAME=<your-username>"
    echo "  export KAFKA_SASL_PASSWORD=<your-password>"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Configuration validated${NC}"
echo ""

# Step 1: Create Kubernetes Secret for Kafka credentials (T098)
echo -e "${BLUE}Step 1: Creating Kubernetes Secret for Kafka credentials...${NC}"

kubectl create secret generic kafka-credentials \
    --from-literal=bootstrap-servers="$KAFKA_BOOTSTRAP_SERVERS" \
    --from-literal=sasl-username="$KAFKA_SASL_USERNAME" \
    --from-literal=sasl-password="$KAFKA_SASL_PASSWORD" \
    --from-literal=security-protocol="$KAFKA_SECURITY_PROTOCOL" \
    --from-literal=sasl-mechanism="$KAFKA_SASL_MECHANISM" \
    --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✅ Kubernetes Secret created${NC}"
echo ""

# Step 2: Create topics via kafka-topics CLI (if available)
echo -e "${BLUE}Step 2: Creating Kafka topics...${NC}"

if command -v kafka-topics &> /dev/null; then
    # Create temporary properties file
    PROPS_FILE=$(mktemp)
    cat > $PROPS_FILE <<EOF
bootstrap.servers=${KAFKA_BOOTSTRAP_SERVERS}
security.protocol=${KAFKA_SECURITY_PROTOCOL}
sasl.mechanism=${KAFKA_SASL_MECHANISM}
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username="${KAFKA_SASL_USERNAME}" password="${KAFKA_SASL_PASSWORD}";
EOF

    for topic in todo-created todo-updated todo-deleted todo-reminder; do
        echo "Creating topic: ${topic}"

        kafka-topics --create \
            --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
            --command-config "$PROPS_FILE" \
            --topic "$topic" \
            --partitions 3 \
            --replication-factor 3 \
            --if-not-exists || echo "Topic may already exist"
    done

    rm -f "$PROPS_FILE"
    echo -e "${GREEN}✅ Topics created${NC}"
else
    echo -e "${YELLOW}⚠️  kafka-topics CLI not found${NC}"
    echo "Please create topics manually via your Kafka provider console:"
    echo "  - todo-created"
    echo "  - todo-updated"
    echo "  - todo-deleted"
    echo "  - todo-reminder"
    echo ""
    echo "Recommended settings:"
    echo "  - Partitions: 3"
    echo "  - Replication Factor: 3"
    echo "  - Retention: 7 days"
fi
echo ""

# Step 3: Create Dapr Pub/Sub component for managed Kafka
echo -e "${BLUE}Step 3: Creating Dapr Pub/Sub component...${NC}"

cat > /tmp/dapr-pubsub-kafka.yaml <<EOF
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "${KAFKA_BOOTSTRAP_SERVERS}"
  - name: authType
    value: "password"
  - name: saslUsername
    secretKeyRef:
      name: kafka-credentials
      key: sasl-username
  - name: saslPassword
    secretKeyRef:
      name: kafka-credentials
      key: sasl-password
  - name: saslMechanism
    value: "${KAFKA_SASL_MECHANISM}"
  - name: securityProtocol
    value: "${KAFKA_SECURITY_PROTOCOL}"
  - name: maxMessageBytes
    value: "1024000"
  - name: consumeRetryInterval
    value: "200ms"
  - name: version
    value: "2.8.0"
EOF

kubectl apply -f /tmp/dapr-pubsub-kafka.yaml

echo -e "${GREEN}✅ Dapr Pub/Sub component created${NC}"
echo ""

# Step 4: Verify connection
echo -e "${BLUE}Step 4: Verifying Kafka connection...${NC}"

if command -v kafka-topics &> /dev/null; then
    PROPS_FILE=$(mktemp)
    cat > $PROPS_FILE <<EOF
bootstrap.servers=${KAFKA_BOOTSTRAP_SERVERS}
security.protocol=${KAFKA_SECURITY_PROTOCOL}
sasl.mechanism=${KAFKA_SASL_MECHANISM}
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username="${KAFKA_SASL_USERNAME}" password="${KAFKA_SASL_PASSWORD}";
EOF

    echo "Listing topics..."
    kafka-topics --list \
        --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
        --command-config "$PROPS_FILE"

    rm -f "$PROPS_FILE"
    echo -e "${GREEN}✅ Connection verified${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping connection verification (kafka-topics CLI not available)${NC}"
fi
echo ""

echo -e "${GREEN}✅ Managed Kafka setup complete!${NC}"
echo ""
echo "=== Configuration Summary ==="
echo "Provider: ${KAFKA_PROVIDER}"
echo "Bootstrap Servers: ${KAFKA_BOOTSTRAP_SERVERS}"
echo "Security Protocol: ${KAFKA_SECURITY_PROTOCOL}"
echo "SASL Mechanism: ${KAFKA_SASL_MECHANISM}"
echo ""
echo "=== Next Steps ==="
echo "1. Verify Dapr component: kubectl get components"
echo "2. Deploy application: helm install todo-app ./helm/todo-app-phase5 -f values-oke.yaml"
echo "3. Monitor logs: kubectl logs -l app=backend -c daprd --tail=50 -f"
echo ""
