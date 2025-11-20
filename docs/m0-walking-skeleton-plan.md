# 🦴 Milestone M0 – Walking Skeleton Implementation Plan

**Objective:** Deliver a minimal but functional end-to-end TrainFlow skeleton:

- Chainlit chat UI → LangGraph → OpenAI → Response
- Cloud Run deployment
- CI/CD pipeline

---

## 🧱 Architecture Snapshot

**Frontend:** Chainlit chat app  
**Backend:** LangGraph with a single LLM node  
**Infra:** Docker → Cloud Run  
**CI/CD:** GitHub Actions for test + deploy

---

## 🗂 Repository Layout (Initial)

```
trainflow/
  docs/
  src/trainflow/
    config.py
    graph/coach_graph.py
    ui/chainlit_app.py
    server/main.py
  .chainlit/
  .github/workflows/
  Dockerfile
  pyproject.toml
```

---

## 🧪 Definition of Done

- Local development works.
- Cloud Run deployment works.
- CI ensures lint + tests.
- CD deploys on merge to main.

---

## 🔧 Proposed PR Breakdown

### PR #1 – Repo Bootstrap
- Project structure
- Lint/format tools
- Dummy test

### PR #2 – Minimal LangGraph Coach
- Simple LLM node
- `run_coach_graph()` function
- Tests with OpenAI mocks

### PR #3 – Chainlit UI Integration
- Chat bubble handler
- Route messages to graph

### PR #4 – Docker & Cloud Run
- Dockerfile
- Basic deployment script

### PR #5 – CI Setup
- Lint + tests on PRs

### PR #6 – CD Deployment
- Auto-deploy on merge to main

### PR #7 – Logging & Error Handling
- Structured logs
- Simple error fallback

---

## 🧭 Optional Stretch Goals

- Dev/prod config profiles
- Smoke tests against live Cloud Run
