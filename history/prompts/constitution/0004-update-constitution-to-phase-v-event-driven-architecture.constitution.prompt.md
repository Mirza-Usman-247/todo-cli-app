---
id: 0004
title: Update Constitution to Phase V Event-Driven Architecture
stage: constitution
date: 2026-01-27
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: todo-app
user: system
command: /sp.constitution
labels: ["constitution", "event-driven", "kafka", "dapr", "phase-v", "kubernetes", "production"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - None (constitution update, no code tests)
---

## Prompt

Role:
You are Claude Code acting as a Senior Cloud-Native Architect and Event-Driven Systems Engineer.

Phase Objective:
Design and deploy the Advanced Todo Chatbot with event-driven architecture using Kafka and Dapr, first on Minikube and then on a production-grade Kubernetes cluster (AKS / GKE / OKE).

Mandatory Rule (Critical):
Before ANY implementation:
- Use MCP Context 7 server
- Fetch and study the latest official documentation for:
  - Kubernetes (AKS / GKE / OKE)
  - Dapr (Pub/Sub, State, Jobs API, Secrets, Service Invocation)
  - Kafka (Strimzi / Redpanda Cloud / Confluent)
  - GitHub Actions (CI/CD)
- Do NOT rely on prior knowledge
- Do NOT write code until documentation is fully understood

Development Workflow (Non-Negotiable):
Write Spec → Generate Plan → Break into Tasks → Implement via Claude Code

Hard Constraints:
- No manual coding by the user
- No skipping phases
- No undocumented assumptions
- All infrastructure interaction must be declarative and reproducible

Architecture Principles:
- Event-driven (Kafka via Dapr Pub/Sub)
- Loose coupling via Dapr sidecars
- Stateless services
- Cloud-portable Kubernetes manifests
- Secure secrets handling

## Response snapshot

Constitution updated from Version 4.0.0 to Version 5.0.0 with comprehensive Phase V event-driven architecture principles.

Key changes implemented:

1. **Major Version Bump (4.0.0 → 5.0.0)**: Backward-incompatible evolution from local Kubernetes deployment to production-grade event-driven architecture.

2. **New Core Principles Added** (XIX-XXVI):
   - Event-Driven Architecture First
   - Dapr Sidecar Pattern Mandate
   - Kafka as Event Backbone
   - Loose Coupling via Service Invocation
   - Stateless Services with Dapr State API
   - Secrets Management via Dapr
   - Production-Grade Kubernetes Focus
   - MCP Context Mandate for Dapr & Kafka

3. **Modified Existing Principles**:
   - Phase-Scoped Development: Now targets event-driven refactoring with Kafka and Dapr
   - Storage Architecture: Replaced ephemeral storage with Dapr State Store API
   - MCP Context-First Development: Expanded to include Kafka, Dapr, and production Kubernetes
   - Container-First Design: Updated for Dapr sidecar pattern
   - Declarative Operations: Extended to include Dapr components and Kafka configurations
   - Cluster Focus: Shifted from local Minikube to production Kubernetes (AKS/GKE/OKE)

4. **Technical Constraints Updated**:
   - Event-Driven Architecture Stack defined (Kafka, Dapr, Redis, GitHub Actions)
   - Dapr component specifications (Pub/Sub, State Store, Secrets)
   - Kafka infrastructure options (Strimzi, Redpanda Cloud, Confluent)
   - Production Kubernetes providers (AKS, GKE, OKE)
   - Event schemas documented (todo-created, todo-updated, todo-deleted)
   - CI/CD pipeline requirements with GitHub Actions

5. **Development Workflow Enhanced**:
   - Phase 0: MCP Context 7 validation (BLOCKING gate)
   - Phase 1: Event architecture design
   - Phase 2: Dapr component configuration
   - Phase 3: Application refactoring
   - Phase 4: Local validation (Minikube)
   - Phase 5: Production deployment (AKS/GKE/OKE)

6. **Governance Strengthened**:
   - MCP Context 7 validation mandatory before ANY implementation
   - Event flow testing requirements
   - Dapr component validation with CLI
   - Production deployment compliance checks

## Outcome

- ✅ Impact: Constitution successfully upgraded to Phase V with comprehensive event-driven architecture guidance. All principles, constraints, and workflows aligned with Kafka, Dapr, and production Kubernetes requirements.
- 🧪 Tests: No code tests (constitution documentation update). Validation via Sync Impact Report embedded in constitution file.
- 📁 Files: Updated `.specify/memory/constitution.md` (4.0.0 → 5.0.0)
- 🔁 Next prompts:
  1. Validate MCP Context 7 server availability and test Dapr/Kafka documentation access
  2. Run `/sp.specify` for first event-driven feature (e.g., "Event-Driven Todo CRUD with Kafka and Dapr")
  3. Update CLAUDE.md to emphasize MCP Context 7 mandate and Dapr/Kafka focus
  4. Review and update template files (plan-template.md, spec-template.md, tasks-template.md) for event-driven patterns
- 🧠 Reflection: The constitution now provides clear, enforceable principles for building production-grade event-driven applications. The MCP Context 7 mandate ensures all Dapr and Kafka implementations use current best practices, not outdated training data. The phased workflow (Minikube validation → production deployment) reduces risk while maintaining development velocity.

## Evaluation notes (flywheel)

- Failure modes observed: None in constitution update. Potential future failure modes: (1) MCP Context 7 unavailable when needed, (2) Dapr components misconfigured without proper MCP validation, (3) Event schemas evolving without documentation updates.
- Graders run and results (PASS/FAIL): PASS - Constitution file successfully updated with all placeholders filled, version incremented, Sync Impact Report embedded.
- Prompt variant (if applicable): Standard /sp.constitution command with Phase V event-driven architecture requirements.
- Next experiment (smallest change to try): Test MCP Context 7 server connection and validate Dapr Pub/Sub API documentation retrieval before proceeding to `/sp.specify`.
