# Delphic Chatbot — Architecture

## Overview

Delphic Jobs is a manpower/recruitment company. Delphic-Chatbot will be a WhatsApp
chatbot used exclusively by jobseekers to ask questions, discover jobs, register and
update their candidate information, get application information, and contact a human
recruiter.

## Principles

This project follows **production-quality engineering with the simplest architecture
that correctly solves the current requirements**. We build only what is required now,
avoid speculative features, and prefer simple, readable solutions.

## Planned System Components

The eventual product will integrate the following (none are connected yet):

- **Meta WhatsApp Cloud API** — messaging channel for jobseekers.
- **AI / LLM** — natural-language intent understanding and information extraction.
- **Google Sheets & Google Forms** — Delphic's existing business data source,
  to be integrated rather than replaced.
- **Backend application** — contains the actual business logic.

Pipeline: `WhatsApp → Backend → AI understanding → deterministic business logic
→ Google Sheets → WhatsApp`.

## Current Status

### Phase 1 — Development Foundation (complete)

Minimal FastAPI backend:

- Health check `GET /health`.
- Configuration via pydantic-settings.
- Logging, tests, ruff, GitHub Actions CI.
- No external services.

### Phase 2 — Domain & Conversation Core (complete)

Deterministic, local conversation core built on mock data:

- Domain models, intents, intent results, conversation states and context.
- In-memory mock data stores (`CandidateStore`, `JobStore`, `ApplicationStore`,
  `FAQStore`) and thin business services.
- Deterministic conversation engine.
- Test endpoint `POST /api/v1/conversations/test` for exercising the engine.
- No external services, no database, no AI.

## Phase 2 Structure

```
delphic-chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   └── conversations.py      # test endpoint (NOT the WhatsApp webhook)
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── conversation/
│   │   ├── __init__.py
│   │   ├── engine.py             # deterministic conversation engine
│   │   └── messages.py           # provisional message text
│   ├── data/
│   │   ├── __init__.py
│   │   ├── mock_data.py          # clearly fake candidate/job/application/FAQ data
│   │   └── stores.py             # in-memory data access layer
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── conversation.py       # states + context
│   │   ├── intents.py            # Intent enum + Entities + IntentResult
│   │   ├── models.py             # Candidate, Job, Application, FAQ
│   │   └── responses.py          # Response model
│   └── services/
│       ├── __init__.py
│       ├── applications.py
│       ├── candidates.py
│       ├── faqs.py
│       └── jobs.py
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_candidates.py
│   ├── test_conversation.py
│   ├── test_faqs_applications.py
│   ├── test_health.py
│   └── test_jobs.py
├── docs/
│   ├── architecture.md
│   ├── conversation-flow.md
│   └── domain.md
├── .github/workflows/ci.yml
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
└── LICENSE
```

## Design notes

- **Domain** (`app/domain/`) is the vocabulary: models, intents, states,
  context, response. See [domain.md](domain.md).
- **Data** (`app/data/`) keeps Google Sheets out of business logic. The four
  stores are thin wrappers over mock in-memory data. When Sheets credentials and
  structures arrive, only this layer is replaced/adapted.
- **Services** (`app/services/`) hold the small deterministic business rules
  (search, FAQ lookup, candidate updates, application lookup).
- **Conversation engine** (`app/conversation/engine.py`) maps `IntentResult`
  to a `Response` using the services. It is fully local and deterministic.
- **API** exposes the engine for local testing only. The production webhook will
  be added in a later phase.
- **No persistence**: every request builds a fresh context; the candidate is
  re-resolved from the store per message.

## Configuration

Settings are read from environment variables and an optional `.env` file (see
`.env.example`) using pydantic-settings. Settings are cached so they are loaded
once per process. The only setting in use is `ENVIRONMENT`.

## Future Phases

Later phases will add, as requirements and credentials are confirmed:

- WhatsApp webhook (Meta Cloud API).
- AI intent classification / entity extraction.
- Google Sheets / Forms integration.
- Multi-turn candidate registration and application workflows.
- Realization of Delphic's final business rules.

These will be introduced only when their requirements are confirmed.