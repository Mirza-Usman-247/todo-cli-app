# Deploy Phase 5 - Quick Start Guide

**Your existing app + Event-Driven features**

---

## ✅ Prerequisites (Already Done!)

- ✅ Minikube running
- ✅ Kafka cluster deployed
- ✅ Dapr control plane installed
- ✅ Redis deployed
- ✅ Dapr components configured

All infrastructure is ready! Just need to build and deploy your app.

---

## 🚀 Deploy in 3 Steps

### Step 1: Build Backend Docker Image

```bash
cd /mnt/c/code/hackathon\ II/todo-app

# Point Docker to Minikube's Docker daemon
eval $(minikube docker-env)

# Build backend with Phase 5 updates
docker build -t todo-backend:phase5 -f backend/Dockerfile backend/

# Verify image
docker images | grep todo-backend
```

### Step 2: Install Dependencies (If Needed)

```bash
cd backend
pip3 install dapr dapr-ext-fastapi
```

### Step 3: Deploy with Helm

```bash
# Deploy entire stack
helm install todo-app-phase5 ./helm/todo-app-phase5

# Watch pods start (should see 2 containers per pod: app + daprd)
kubectl get pods -w

# Check Dapr sidecar injection worked
kubectl get pods -o jsonpath='{.items[*].spec.containers[*].name}'
# Should see: backend daprd
```

---

## 🧪 Test Event-Driven Features

### 1. Access Your Application

```bash
# Get backend URL
kubectl port-forward svc/todo-app-phase5-backend 8000:8000

# In another terminal, get frontend URL (if deployed)
minikube service todo-app-phase5-frontend --url
```

### 2. Create a Todo (Existing Endpoint)

```bash
# Your existing API works exactly the same!
curl -X POST http://localhost:8000/api/v1/todos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Test Phase 5 Events",
    "description": "This will publish to Kafka!"
  }'
```

### 3. Verify Event Published to Kafka

```bash
# Check Kafka topic for your event
kubectl exec -n kafka my-cluster-dual-role-0 -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic todo-created \
  --from-beginning \
  --max-messages 1

# You should see a CloudEvents-formatted message!
```

### 4. Check Backend Logs

```bash
# See event publishing in action
kubectl logs -l app=backend --tail=50

# Look for these log messages:
# "Phase 2-4: Auth, Todos, Chat ✅"
# "Phase 5: Event-Driven (Dapr) ✅"
# "📤 Published todo-created event for todo {uuid}"
```

---

## 🎯 What Works Now

### ✅ All Your Existing Features
- Authentication & Signup
- Todo CRUD (database)
- AI Chatbot
- Everything from Phase 2-4

### 🆕 Plus Phase 5 Events
- Kafka event publishing
- CloudEvents format
- Event-driven architecture
- Audit trail in Kafka

**Your app is backward compatible!**
- Works WITH Dapr → Publishes events ✅
- Works WITHOUT Dapr → Still functions normally ✅

---

## 📊 Verify Components

```bash
# Check Dapr components are loaded
kubectl get components
# Should see: pubsub-kafka, statestore-redis, kubernetes-secrets

# Check Dapr subscriptions
kubectl get subscriptions
# Should see: backend-todo-created, backend-todo-updated, etc.

# Check backend pod has Dapr sidecar
kubectl describe pod -l app=backend | grep -A 5 "Containers:"
# Should list: backend AND daprd
```

---

## 🔍 Troubleshooting

### Backend Won't Start

```bash
# Check pod status
kubectl get pods -l app=backend

# Check logs
kubectl logs -l app=backend -c backend
kubectl logs -l app=backend -c daprd

# Common issues:
# 1. Image not found → Build again with eval $(minikube docker-env)
# 2. CrashLoopBackOff → Check DATABASE_URL in values.yaml
# 3. Dapr sidecar failing → Ensure Dapr control plane running
```

### Events Not Publishing

```bash
# Check Dapr sidecar logs
kubectl logs -l app=backend -c daprd

# Verify Kafka connection
kubectl get component pubsub-kafka -o yaml

# Test Kafka directly
kubectl exec -n kafka my-cluster-dual-role-0 -- \
  bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Database Connection Issues

```bash
# Check if PostgreSQL pod exists
kubectl get pods | grep postgres

# If not deployed, deploy it:
helm install postgres bitnami/postgresql \
  --set auth.database=todos \
  --set auth.username=postgres \
  --set auth.password=postgres
```

---

## 🎓 Understanding the Architecture

### Request Flow (Phase 5)

```
User → Frontend → Backend API (FastAPI)
                       ↓
                 Database SAVE (PostgreSQL) ✅
                       ↓
                 Event PUBLISH ──→ Dapr Sidecar
                                        ↓
                                   Kafka Topic
                                        ↓
                                (Future: Event Consumers)
```

### Key Points

1. **Database is still primary**: PostgreSQL saves todo
2. **Events are secondary**: Published AFTER database save
3. **Non-blocking**: Event failure doesn't break todo creation
4. **Backward compatible**: Works without Dapr/Kafka

---

## 📝 Next Steps

### Option 1: Test Thoroughly
- Create, update, delete todos
- Verify events in Kafka
- Check all existing features still work

### Option 2: Add Event Consumers
- Implement event subscribers (backend/src/events/subscribers.py)
- Process events from Kafka
- Add business logic triggered by events

### Option 3: Deploy to Cloud
- Continue with Phase 9-12 tasks
- Deploy to OKE (Oracle Kubernetes Engine)
- Add CI/CD pipeline

---

## 🎉 Summary

You now have:
- ✅ All Phase 2-4 features (auth, todos, chat)
- ✅ Phase 5 event-driven architecture
- ✅ Kafka event streaming
- ✅ Dapr service abstraction
- ✅ Backward compatible design

**Everything preserved. New capabilities added. Zero breaking changes.**

---

*Generated by Claude Code*
*Last Updated: 2026-01-28*
