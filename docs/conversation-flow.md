# Delphic Chatbot — Conversation Flow

How the deterministic conversation engine (`app/conversation/engine.py`) works
in Phase 2.

## Pipeline

```
User input (WhatsApp message)
        ↓
AI intent understanding      ← NOT in Phase 2; produced by the test caller
        ↓
IntentResult (intent + entities)
        ↓
ConversationEngine.handle(context, intent_result)
        ↓
Business operation (mock stores/services)
        ↓
Response (message, state, handoff_required, payloads)
```

The engine performs **no external calls** — no AI, no Google Sheets, no
WhatsApp. All data comes from the in-memory mock stores in `app/data/`.

## Entry point

`ConversationEngine.handle(context, intent_result)`:

1. Sets the current intent and entities on the context.
2. Re-resolves the candidate for the WhatsApp number from the store.
3. Dispatches to the intent handler.
4. Returns a `Response`.

## Intent behaviour

| Intent | Behaviour | State(s) produced | Handoff? |
| ------ | --------- | ----------------- | -------- |
| `GREETING` | Find-or-create candidate; welcome message | `WELCOME` | — |
| `FIND_JOB` | Search OPEN jobs by role/location/experience/qualification; list results | `SEARCHING_JOBS` | — |
| `JOB_DETAILS` | Full details for `job_id` (OPEN only) | `VIEWING_JOB` / `WAITING_FOR_INPUT` | — |
| `ELIGIBILITY` | Experience/qualification of the resolved job | `VIEWING_JOB` | — |
| `COMPENSATION` | Salary of the resolved job | `VIEWING_JOB` | — |
| `LOCATION` | Location of the resolved job | `VIEWING_JOB` | — |
| `HOW_TO_APPLY` | Approved FAQ answer (category `HOW_TO_APPLY`) | `WAITING_FOR_INPUT` | if no answer |
| `APPLICATION_STATUS` | Candidate's application details | `CHECKING_APPLICATION` | — |
| `INTERVIEW` | Interview date from application | `CHECKING_APPLICATION` | — |
| `DOCUMENTS` | Approved FAQ answer (category `DOCUMENTS`) | `WAITING_FOR_INPUT` | if no answer |
| `PROFILE_UPDATE` | Apply provided role/location/experience/qualification to the profile | `COLLECTING_PROFILE` | if no candidate |
| `GENERAL_FAQ` | Answer for `faq_category`; prompts if none given | `WAITING_FOR_INPUT` / `HUMAN_HANDOFF` | if no answer |
| `HUMAN_SUPPORT` | Enter human handoff | `HUMAN_HANDOFF` | yes |
| `GOODBYE` | Completion message | `COMPLETED` | — |
| `UNKNOWN` | Safe fallback + handoff | `HUMAN_HANDOFF` | yes |

## Human handoff triggers

The conversation requires a human recruiter when:

- the user explicitly asks (`HUMAN_SUPPORT`),
- a request cannot be interpreted safely (`UNKNOWN`),
- a requested FAQ has no approved answer,
- a profile update arrives for an unknown number.

Handoff is a flag + state. No notification system is contacted in Phase 2.

## Example flows

### New candidate greets and searches

```
POST /api/v1/conversations/test
{ "whatsapp_number": "+919000000001", "intent": "GREETING" }
→ WELCOME, handoff_required=false

{ "whatsapp_number": "+919000000001",
  "intent": "FIND_JOB",
  "entities": { "location": "Bangalore", "experience": "FRESHER" } }
→ SEARCHING_JOBS, jobs=[J001, J004]

{ "whatsapp_number": "+919000000001",
  "intent": "JOB_DETAILS",
  "entities": { "job_id": "J001" } }
→ VIEWING_JOB, job=J001
```

### Existing candidate checks application status

```
{ "whatsapp_number": "+919000000002", "intent": "APPLICATION_STATUS" }
→ CHECKING_APPLICATION, application=A002 (APPLIED, no interview yet)
```

### User asks for a human

```
{ "whatsapp_number": "+919000000001", "intent": "HUMAN_SUPPORT" }
→ HUMAN_HANDOFF, handoff_required=true
```

### Unknown request

```
{ "whatsapp_number": "+919000000001", "intent": "UNKNOWN" }
→ HUMAN_HANDOFF, handoff_required=true, safe fallback message
```

## The test conversation endpoint

`POST /api/v1/conversations/test` (`app/api/conversations.py`)

- **NOT the production WhatsApp webhook.** It exists only to exercise the
  engine locally before WhatsApp / AI integration.
- Request body:
  ```json
  {
    "whatsapp_number": "+919000000001",
    "intent": "FIND_JOB",
    "entities": { "location": "Bangalore", "experience": "FRESHER" }
  }
  ```
  `intent` must be one of the `Intent` enum values; `entities` is optional.
- Response body is the `Response` model: `message`, `state`,
  `handoff_required`, plus `jobs`/`job`/`application`/`info` when present.
- Try it in the Swagger UI at `http://127.0.0.1:8000/docs` with the server
  running.

## Deliberately not implemented in Phase 2

- WhatsApp webhook and sending messages.
- AI intent classification (the caller supplies `intent`).
- Candidate registration via multi-turn profile collection.
- Job application submission.
- Google Sheets integration.
- Persistent conversation state.