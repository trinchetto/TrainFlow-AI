# M1 – PR Plan and Exit Checklist (File Tools)

Milestone focus: introduce FIT/ZWO parsing and generation tools, wire them into LangGraph, and keep the walking skeleton production-ready.

---

## Planned PRs to Hit M1

1) **Scaffolding + Fixtures**
   - Add FIT/ZWO sample files in `tests/fixtures`.
   - Define shared data model for workouts (internal representation used by both formats).
   - Document file formats and assumptions.
2) **FIT Parse/Generate**
   - Implement FIT parser → internal model; round-trip generator → FIT.
   - Unit tests for happy/error paths and round-trip.
3) **ZWO Parse/Generate**
   - Implement ZWO parser → internal model; round-trip generator → ZWO.
   - Unit tests parallel to FIT coverage.
4) **Tool Abstractions**
   - Expose unified tool interface (parse/generate) for FIT/ZWO.
   - Validation and error surfacing; structured logging.
5) **LangGraph Integration**
   - Add file tools as graph nodes/tools; adapter from coach prompts to tool calls.
   - Contract/integration test to ensure tool invocation flow works.
6) **Chainlit UX**
   - UI affordance to upload/receive workout files (or demo hook).
   - Display parsed summary and generated outputs.
7) **Docs + Ops**
   - Update README/docs for file tools usage, sample commands, env vars.
   - CI additions (lint/tests for tool modules); note rollout/rollback steps.

## Exit / Demo Checklist for M1

- [ ] FIT parser can read a sample workout file and surface structured data.
- [ ] FIT generator produces a valid file that can be reopened by the parser (round-trip smoke).
- [ ] ZWO parser/generator support is equivalent (round-trip smoke).
- [ ] Unified tool interface exists and is covered by tests (happy + failure cases).
- [ ] LangGraph exposes file tools through the coach flow with a demoable path.
- [ ] Chainlit UI can invoke a tool-backed action and show the result without manual tweaks.
- [ ] Observability: structured logs include correlation/session IDs; failures are traceable.
- [ ] CI pipeline runs lint + tests for tool modules; artifacts (if any) handled in CI.
- [ ] Docs updated: how to use file tools locally and via Chainlit, required env vars, samples.
- [ ] Rollback plan noted for deployment (toggle to fallback behavior if tools regress).
