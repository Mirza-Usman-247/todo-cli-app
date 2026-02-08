#!/bin/bash
# Inspect Kafka Topics (T093)
# View messages in Kafka topics to verify event publishing

set -e

echo "=== Kafka Topics Inspection ==="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get Kafka pod
KAFKA_POD=$(kubectl get pod -n kafka -l app.kubernetes.io/name=kafka -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$KAFKA_POD" ]; then
    echo -e "${RED}❌ Kafka pod not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Kafka pod: ${KAFKA_POD}${NC}"
echo ""

# Function to inspect topic
inspect_topic() {
    local topic=$1
    local max_messages=${2:-10}

    echo -e "${BLUE}=== Topic: ${topic} ===${NC}"

    # Check if topic exists
    topic_exists=$(kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
        --bootstrap-server my-cluster-kafka-bootstrap:9092 \
        --list 2>/dev/null | grep -c "^${topic}$" || echo "0")

    if [ "$topic_exists" -eq 0 ]; then
        echo -e "${RED}❌ Topic does not exist${NC}"
        echo ""
        return
    fi

    # Describe topic
    echo "Topic description:"
    kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
        --bootstrap-server my-cluster-kafka-bootstrap:9092 \
        --describe --topic ${topic} 2>/dev/null

    echo ""
    echo "Recent messages (last ${max_messages}):"

    # Consume recent messages
    kubectl exec -n kafka $KAFKA_POD -- bin/kafka-console-consumer.sh \
        --bootstrap-server my-cluster-kafka-bootstrap:9092 \
        --topic ${topic} \
        --from-beginning \
        --max-messages ${max_messages} \
        --timeout-ms 5000 2>/dev/null || echo -e "${YELLOW}No messages or timeout${NC}"

    echo ""
    echo "---"
    echo ""
}

# List all topics
echo -e "${BLUE}All Kafka topics:${NC}"
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
    --bootstrap-server my-cluster-kafka-bootstrap:9092 \
    --list 2>/dev/null
echo ""
echo "---"
echo ""

# Inspect each todo topic
inspect_topic "todo-created" 5
inspect_topic "todo-updated" 5
inspect_topic "todo-deleted" 5
inspect_topic "todo-reminder" 5

# Get consumer groups
echo -e "${BLUE}=== Consumer Groups ===${NC}"
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-consumer-groups.sh \
    --bootstrap-server my-cluster-kafka-bootstrap:9092 \
    --list 2>/dev/null || echo -e "${YELLOW}No consumer groups${NC}"
echo ""

# Function to monitor topic in real-time
monitor_topic() {
    local topic=$1

    echo -e "${BLUE}=== Monitoring topic: ${topic} (Ctrl+C to stop) ===${NC}"
    echo ""

    kubectl exec -n kafka $KAFKA_POD -- bin/kafka-console-consumer.sh \
        --bootstrap-server my-cluster-kafka-bootstrap:9092 \
        --topic ${topic} \
        --from-beginning 2>/dev/null
}

# Interactive mode
if [ "$1" == "--monitor" ]; then
    topic=${2:-todo-created}
    monitor_topic $topic
elif [ "$1" == "--help" ]; then
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  (none)           Inspect all topics and show recent messages"
    echo "  --monitor TOPIC  Monitor a specific topic in real-time"
    echo "  --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                           # Inspect all topics"
    echo "  $0 --monitor todo-created    # Monitor todo-created topic"
    echo ""
else
    echo -e "${GREEN}✅ Inspection complete!${NC}"
    echo ""
    echo "To monitor a topic in real-time:"
    echo "  ./scripts/inspect-kafka-topics.sh --monitor todo-created"
    echo ""
fi
