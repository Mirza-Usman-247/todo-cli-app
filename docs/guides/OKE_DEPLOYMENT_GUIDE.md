# OKE Deployment Guide (T125)

Production deployment guide for Oracle Kubernetes Engine (OKE).

## Prerequisites

Before deploying to OKE, ensure you have:

### Required Tools

- [OCI CLI](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm) v3.0+
- [kubectl](https://kubernetes.io/docs/tasks/tools/) v1.28+
- [Helm](https://helm.sh/docs/intro/install/) v3.12+
- [Dapr CLI](https://docs.dapr.io/getting-started/install-dapr-cli/) v1.12+

### OCI Resources

- Oracle Cloud account with active subscription
- Compartment with appropriate permissions
- VCN with public and private subnets
- Container Registry (OCIR) access
- (Optional) Managed database service

### Secrets and Credentials

- OCI API key pair
- OCIR auth token
- Database credentials
- Kafka credentials (Redpanda/Confluent)
- Redis password

## Deployment Steps

### Step 1: Provision OKE Cluster

Run the cluster provisioning script:

```bash
# Set environment variables
export OCI_COMPARTMENT_ID="ocid1.compartment.oc1..aaaa..."
export OCI_REGION="us-ashburn-1"
export OKE_CLUSTER_NAME="todo-app-phase5"
export OKE_NODE_COUNT=3

# Provision cluster
./scripts/provision-oke-cluster.sh
```

**What this does**:
- Creates VCN with subnets
- Provisions OKE cluster with specified Kubernetes version
- Creates node pool with 3 worker nodes (VM.Standard.E4.Flex)
- Configures kubectl context

**Estimated time**: 15-20 minutes

### Step 2: Set Up Managed Kafka

Configure managed Kafka (Redpanda Cloud or Confluent Cloud):

```bash
# Set Kafka credentials
export KAFKA_BOOTSTRAP_SERVERS="seed-xxxxx.us-east-1.aws.redpanda.com:9092"
export KAFKA_SASL_USERNAME="your-username"
export KAFKA_SASL_PASSWORD="your-password"

# Run setup script
./scripts/setup-managed-kafka.sh
```

**What this does**:
- Creates Kubernetes secret for Kafka credentials
- Creates 4 topics (todo-created, todo-updated, todo-deleted, todo-reminder)
- Configures Dapr Pub/Sub component

**Estimated time**: 5 minutes

### Step 3: Install Dapr Control Plane

Install Dapr with high availability and mTLS:

```bash
./scripts/setup-dapr-oke.sh
```

**What this does**:
- Installs Dapr v1.12+ in `dapr-system` namespace
- Enables HA mode (3 replicas for each component)
- Enables mTLS for secure communication
- Configures resource limits for production

**Estimated time**: 5 minutes

### Step 4: Deploy Redis Cluster

Deploy Redis with persistence:

```bash
./scripts/setup-redis-oke.sh
```

**What this does**:
- Deploys Redis cluster with 3 replicas
- Enables persistence using OCI Block Volumes
- Creates Kubernetes secret for Redis password
- Configures Dapr State Store component

**Estimated time**: 5 minutes

### Step 5: Build and Push Docker Images

Build and push images to OCIR:

```bash
# Set OCIR credentials
export OCIR_USERNAME="<tenancy-namespace>/<oci-username>"
export OCIR_AUTH_TOKEN="<auth-token>"
export OCI_REGION="us-ashburn-1"

# Login to OCIR
docker login ${OCI_REGION}.ocir.io -u ${OCIR_USERNAME} -p ${OCIR_AUTH_TOKEN}

# Build backend
cd backend
docker build -t ${OCI_REGION}.ocir.io/<tenancy-namespace>/todo-backend:phase5 .
docker push ${OCI_REGION}.ocir.io/<tenancy-namespace>/todo-backend:phase5
cd ..

# Build frontend
cd frontend
docker build -t ${OCI_REGION}.ocir.io/<tenancy-namespace>/todo-frontend:phase5 \
  -f ../docker/frontend/Dockerfile .
docker push ${OCI_REGION}.ocir.io/<tenancy-namespace>/todo-frontend:phase5
cd ..
```

**Estimated time**: 10-15 minutes

### Step 6: Create Kubernetes Secrets

Create secrets for database, API keys, etc.:

```bash
# Create OCIR pull secret
kubectl create secret docker-registry ocir-secret \
  --docker-server=${OCI_REGION}.ocir.io \
  --docker-username=${OCIR_USERNAME} \
  --docker-password=${OCIR_AUTH_TOKEN}

# Create database credentials secret
kubectl create secret generic database-credentials \
  --from-literal=connection-string="postgresql://user:pass@host:5432/db"

# Create OpenAI API key secret (optional)
kubectl create secret generic openai-secret \
  --from-literal=api-key="<your-api-key>"
```

### Step 7: Update Helm Values

Edit `helm/todo-app-phase5/values-oke.yaml`:

```yaml
backend:
  image:
    repository: us-ashburn-1.ocir.io/<tenancy-namespace>/todo-backend
    tag: phase5

frontend:
  image:
    repository: us-ashburn-1.ocir.io/<tenancy-namespace>/todo-frontend
    tag: phase5

imagePullSecrets:
  - name: ocir-secret
```

### Step 8: Deploy Application

Deploy using Helm:

```bash
helm install todo-app ./helm/todo-app-phase5 \
  --namespace default \
  --values ./helm/todo-app-phase5/values-oke.yaml \
  --wait \
  --timeout 10m
```

**What this deploys**:
- Backend (3 replicas with HPA)
- Frontend (2 replicas with HPA)
- Dapr components (Pub/Sub, State Store, Secrets)
- Services and ingress
- Pod disruption budgets

**Estimated time**: 5 minutes

### Step 9: Verify Deployment

Check deployment status:

```bash
# Check pods
kubectl get pods

# Expected output:
# NAME                              READY   STATUS    RESTARTS   AGE
# todo-app-backend-xxx              2/2     Running   0          2m
# todo-app-backend-yyy              2/2     Running   0          2m
# todo-app-backend-zzz              2/2     Running   0          2m
# todo-app-frontend-aaa             2/2     Running   0          2m
# todo-app-frontend-bbb             2/2     Running   0          2m

# Check services
kubectl get svc

# Check HPA
kubectl get hpa

# Check Dapr components
kubectl get components

# Check Dapr subscriptions
kubectl get subscriptions
```

### Step 10: Install Monitoring Stack

Deploy Prometheus, Grafana, and Fluent Bit:

```bash
./monitoring/install-monitoring.sh
```

**What this deploys**:
- Prometheus for metrics collection
- Grafana with Dapr dashboards
- Fluent Bit for log aggregation
- Alertmanager for notifications

**Estimated time**: 10 minutes

## Accessing the Application

### Get Frontend URL

If using LoadBalancer:

```bash
kubectl get svc todo-app-frontend

# EXTERNAL-IP column shows the public IP
# Access at: http://<EXTERNAL-IP>
```

### Port Forwarding (Alternative)

```bash
# Frontend
kubectl port-forward svc/todo-app-frontend 3000:80

# Backend API
kubectl port-forward svc/todo-app-backend 8000:8000

# Grafana
kubectl port-forward -n monitoring svc/grafana 3000:80
```

## Health Checks

### Application Health

```bash
# Backend health
kubectl exec -it <backend-pod> -c backend -- curl http://localhost:8000/health

# Frontend health
kubectl exec -it <frontend-pod> -c frontend -- curl http://localhost:3000/health
```

### Dapr Health

```bash
# Dapr sidecar health
kubectl exec -it <backend-pod> -c daprd -- curl http://localhost:3500/v1.0/healthz/outbound
```

### Component Health

```bash
# Check Kafka connectivity
kubectl logs <backend-pod> -c daprd | grep -i kafka

# Check Redis connectivity
kubectl logs <backend-pod> -c daprd | grep -i redis
```

## Scaling

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment todo-app-backend --replicas=5

# Scale frontend
kubectl scale deployment todo-app-frontend --replicas=3
```

### Auto-Scaling (HPA)

HPA is pre-configured in `values-oke.yaml`:

```yaml
backend:
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
```

Monitor HPA:

```bash
kubectl get hpa -w
```

## Monitoring

### Grafana Dashboards

Access Grafana:

```bash
kubectl port-forward -n monitoring svc/grafana 3000:80
# Open http://localhost:3000
# Username: admin
# Password: (retrieved from install-monitoring.sh output)
```

**Available Dashboards**:
1. Dapr System Services
2. Dapr Sidecars
3. Todo App - Events & Tasks

### Prometheus Alerts

View active alerts:

```bash
kubectl port-forward -n monitoring svc/prometheus-alertmanager 9093:80
# Open http://localhost:9093
```

### Application Logs

```bash
# Backend logs
kubectl logs -l app=backend -c backend --tail=100 -f

# Dapr sidecar logs
kubectl logs -l app=backend -c daprd --tail=100 -f

# All logs for a pod
kubectl logs <pod-name> --all-containers=true -f
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name>

# Check image pull
kubectl get events --sort-by=.metadata.creationTimestamp

# Common issues:
# - OCIR authentication failed → Recreate ocir-secret
# - Image not found → Verify image tag and push
# - Resource limits → Check node capacity
```

### Dapr Sidecar Issues

```bash
# Check Dapr injection
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].name}'
# Should show: backend daprd (or frontend daprd)

# Check Dapr logs
kubectl logs <pod-name> -c daprd --tail=100

# Restart pod to re-inject sidecar
kubectl delete pod <pod-name>
```

### Event Processing Issues

```bash
# Check Kafka connectivity
kubectl logs <backend-pod> -c daprd | grep -i kafka

# Inspect Kafka topics
./scripts/inspect-kafka-topics.sh

# Check consumer lag
kubectl exec -n kafka <kafka-pod> -- bin/kafka-consumer-groups.sh \
  --bootstrap-server <bootstrap-servers> \
  --describe --group backend-group-prod
```

### State Store Issues

```bash
# Check Redis connectivity
kubectl logs <backend-pod> -c daprd | grep -i redis

# Test Redis manually
kubectl exec -it redis-master-0 -- redis-cli -a <password> ping

# Check keys
kubectl exec -it redis-master-0 -- redis-cli -a <password> KEYS "task:*"
```

## Upgrading

### Application Upgrade

```bash
# Build and push new images with new tag
docker build -t ${OCI_REGION}.ocir.io/<tenancy>/todo-backend:v1.1.0 .
docker push ${OCI_REGION}.ocir.io/<tenancy>/todo-backend:v1.1.0

# Upgrade Helm release
helm upgrade todo-app ./helm/todo-app-phase5 \
  --namespace default \
  --values ./helm/todo-app-phase5/values-oke.yaml \
  --set backend.image.tag=v1.1.0 \
  --wait
```

### Rollback

```bash
# Rollback to previous version
helm rollback todo-app 0 -n default

# View rollout history
helm history todo-app -n default
```

## Backup & Disaster Recovery

### Redis Backup

```bash
# Trigger manual backup
kubectl exec -it redis-master-0 -- redis-cli -a <password> BGSAVE

# Copy backup file
kubectl cp redis-master-0:/data/dump.rdb ./redis-backup-$(date +%Y%m%d).rdb
```

### Disaster Recovery

1. **Regional Failover**:
   - Deploy to secondary OKE cluster in different region
   - Use OCI Traffic Management for DNS failover
   - Replicate Redis data across regions

2. **Backup Strategy**:
   - Automated Redis snapshots (daily)
   - Kafka topic replication (if multi-region)
   - Kubernetes resource backups (Velero)

## Cost Optimization

### Resource Tuning

```bash
# Monitor actual resource usage
kubectl top pods

# Adjust resource requests/limits in values-oke.yaml
backend:
  resources:
    requests:
      cpu: 250m  # Adjust based on actual usage
      memory: 512Mi
```

### Autoscaling

- Use HPA to scale down during low traffic
- Consider cluster autoscaler for node scaling
- Use burstable VM shapes for non-production

## Security Hardening

### Network Policies

```bash
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: redis
EOF
```

### Pod Security

- Run as non-root user
- Read-only root filesystem
- Drop all capabilities
- Enable AppArmor/SELinux

## Next Steps

1. Set up CI/CD pipeline (GitHub Actions)
2. Configure SSL/TLS certificates
3. Implement backup automation
4. Set up alerting notifications (Slack/PagerDuty)
5. Performance testing and optimization
6. Documentation updates

## References

- [OCI Documentation](https://docs.oracle.com/en-us/iaas/)
- [OKE Best Practices](https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengbestpractices.htm)
- [Dapr on Kubernetes](https://docs.dapr.io/operations/hosting/kubernetes/)
- [Helm Documentation](https://helm.sh/docs/)
