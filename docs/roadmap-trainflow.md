# 🧠 TrainFlow AI Coach – Product Roadmap

TrainFlow is an AI coach assistant for endurance sports, built iteratively using a **walking skeleton first** and then expanding capabilities in small, end-to-end increments.

---

## 🧩 Guiding Principles

- **Walking skeleton**: from day one there is a deployable end-to-end system, however small.
- **Vertical slices**: every milestone adds user-visible features, not just plumbing.
- **Production mindset**: CI/CD, observability, and deployment pipelines exist from M0.
- **Agent-first design**: behaviour is modeled as explicit phases and tools, not ad-hoc prompts.

---

## 🚩 Milestones Overview

| Milestone | Name                                   | Core Theme                                |
|----------|----------------------------------------|-------------------------------------------|
| M0       | Walking Skeleton                       | Baseline chat UI + LLM + deployment       |
| M1       | File Tools                             | FIT/ZWO parsing & generation tools        |
| M2       | Advanced Agent Behaviour               | Structured coaching phases & workflows    |
| M3       | Athlete Data Integration               | Strava (and others) data ingestion        |
| M4       | Advanced Training Planning             | Methodology-driven, multi-sport planning  |

---

## M0 – Walking Skeleton 🦴

**Goal:** Have a minimal but real, deployed TrainFlow instance that:

- Exposes a **chat-style interface** (Chainlit).
- Uses **LangGraph** to orchestrate a basic “coach” graph.
- Calls the **OpenAI API** for responses.
- Runs on **Google Cloud Run**.
- Is built, tested, and deployed via **CI/CD**.

**Scope:**

- Basic chat loop.
- Cloud Run deployment.
- CI/CD for tests + deploy.

**Out of scope:**

- Tools, integrations, structured agent behaviour.

---

## M1 – File Tools: FIT & ZWO 📁

- Provide unified tool interface for sport file formats.
- Implement FIT + ZWO parse/generate classes.
- Integrate tools into LangGraph for R/W.

---

## M2 – Advanced Agent Behaviour 🎭

- Introduce phases: **setup**, **weekly follow-up**, **final wrap-up**.
- Persist minimal athlete state.
- Add UI entry points to start/continue plans.

---

## M3 – Athlete Data Integration 📡

- Strava OAuth.
- Fetch activities, summaries.
- Provide agent-accessible data tools.

---

## M4 – Advanced Training Planning 🏃‍♀️🚴‍♂️⛷️

- Encode training methodologies.
- Multi-sport tailored plan generation.
- Produce FIT/ZWO workouts where appropriate.

---
