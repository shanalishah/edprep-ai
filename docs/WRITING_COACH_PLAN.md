# Writing Coach - Robust Multi-Agent Architecture

## Vision
Interactive writing assistant with three reliable roles: Questioner (Socratic), Explainer, Challenger. Built for live demos and production.

## Core Components
- Knowledge Base (indexed IELTS materials)
- Agents (role prompts + tools)
- Session State (versions, turns, progress)
- Scoring Integration (existing ML + AI feedback)
- Frontend Workspace (chat + editor + checkpoints)

## Data Model (high level)
- TeachingSession(id, user_id, role, goal, status, created_at)
- TeachingTurn(id, session_id, role, user_input, agent_output, created_at)
- DraftVersion(id, session_id, content, created_at, checkpoint_meta)

## Agent Behaviors
- Questioner: 1–2 focused questions per turn, keep student moving
- Explainer: short, example-driven explanations tied to band descriptors
- Challenger: small, concrete challenges; revision tasks

## Retrieval
- Index top IELTS PDFs; chunk by sections; embed; store in vector DB (initially local)
- Metadata tags: task_type, band_focus, skill_area, difficulty

## Endpoints (initial)
- POST /api/v1/learning/sessions/start → {role, task_type, goal} → {session, first_prompt}
- POST /api/v1/learning/sessions/{id}/step → {user_input, draft_delta?} → {turn, draft_version, next_action}
- GET /api/v1/learning/sessions/{id} → {session, turns, latest_draft, metrics}

## Frontend
- New page: /writing-coach
- Tabs: Questioner | Explainer | Challenger
- Left: chat; Right: editor + rubric + checkpoints

## QA & Risk
- Deterministic prompts, short outputs, guardrails
- Fallbacks if retrieval/scoring fails
- Logging and metrics per turn

## Milestones
- M1: API skeleton + placeholder UI + local retrieval stub
- M2: Role prompts + session persistence + scoring checkpoints
- M3: Index first 3 PDFs + production-ready flows + tests
