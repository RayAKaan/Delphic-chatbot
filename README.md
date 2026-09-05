# Delphic-Chatbot

Backend for the Delphic Jobs WhatsApp chatbot.

Delphic Jobs is a manpower/recruitment company. This chatbot is used only by
jobseekers to ask questions, discover jobs, register/update their candidate
information, get application-related information, and contact a human recruiter.

> **Current status (Phase 2):** The deterministic domain and conversation core
> is implemented and tested against mock data. It does **not** connect to
> WhatsApp, Google Sheets, any AI service, or any other external system yet.
> Those integrations will be added in later phases once requirements and
> credentials are available.

## Stack

- Python 3.11+
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/) / pydantic-settings
- [pytest](https://docs.pytest.org/)
- [ruff](https://docs.astral.sh/ruff/) for linting and formatting

## Getting started

### 1. Install

```bash
cd delphic-chatbot
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -e ".[dev]"
```

### 2. Configure

Copy `.env.example` to `.env` and adjust if needed:

```bash
cp .env.example .env
```

The only optional setting is `ENVIRONMENT` (`development` default).

### 3. Run

```bash
uvicorn app.main:app --reload
```

Open:

- API root: http://127.0.0.1:8000/
- Interactive docs (Swagger): http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

### 4. Test, lint, format

```bash
pytest
ruff check .
ruff format .
```

## Exercising the conversation engine

The conversation engine runs fully on mock data. Use the test endpoint
(**NOT the production WhatsApp webhook**):

```bash
curl -X POST http://127.0.0.1:8000/api/v1/conversations/test \
  -H "Content-Type: application/json" \
  -d '{"whatsapp_number":"+919000000001","intent":"FIND_JOB","entities":{"location":"Bangalore","experience":"FRESHER"}}'
```

The response includes `message`, `state`, `handoff_required`, and any structured
payloads (`jobs`, `job`, `application`). Supported `intent` values are the
`Intent` enum members (e.g. `GREETING`, `FIND_JOB`, `JOB_DETAILS`,
`APPLICATION_STATUS`, `GENERAL_FAQ`, `HUMAN_SUPPORT`, `GOODBYE`).

## Documentation

- [Architecture](docs/architecture.md)
- [Domain model & intents](docs/domain.md)
- [Conversation flows](docs/conversation-flow.md)

## CI

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs linting, formatting
checks, and tests on Python 3.11 and 3.12 for every push to `main` and every PR.

## License

[MIT](LICENSE)