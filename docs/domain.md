# Delphic Chatbot — Domain

This document describes the current domain model, intents, and conversation
concepts of the Delphic-Chatbot.

## Status of the domain

Almost every business-specific detail in this document is a **PROVISIONAL
ASSUMPTION**, not a confirmed Delphic requirement. Delphic has not yet provided:

- the actual Google Sheet structures,
- the final FAQ list,
- the final candidate workflow,
- the final job data,
- the final business rules.

Everything below is our working model, deliberately small, and designed to be
reconciled with Delphic's real data when it arrives.

**CONFIRMED REQUIREMENTS** (from the client brief):

- The chatbot is used ONLY by jobseekers (not employers).
- The chatbot will integrate with Delphic's existing Google Sheets / Forms.
- Users may ask questions, find jobs, register/update candidate info, check
  application info, and reach a human recruiter.
- Integration happens over WhatsApp (Meta Cloud API) with AI intent
  understanding in front of deterministic business logic.

Everything else is provisional.

## Domain models

Defined in `app/domain/models.py`. All models are Pydantic v2 `BaseModel`s.

### Candidate

| Field                | Type             | Notes                                        |
| -------------------- | ---------------- | -------------------------------------------- |
| `candidate_id`       | `str`            | e.g. `C001`                                  |
| `whatsapp_number`    | `str`            | identifier used to find/create candidates    |
| `name`               | `str \| None`    | profile data collected in a later phase      |
| `location`           | `str \| None`    |                                              |
| `experience`         | `str \| None`    |                                        |
| `qualification`      | `str \| None`    |                                              |
| `skills`             | `list[str]`      |                                              |
| `preferred_role`     | `str \| None`    | used by PROFILE_UPDATE                       |
| `preferred_location` | `str \| None`    | used by PROFILE_UPDATE                       |
| `cv`                 | `str \| None`    | upload handling is not in scope yet          |
| `status`             | `CandidateStatus`| `ACTIVE` or `ARCHIVED`                       |

### Job

| Field                  | Type        | Notes                          |
| ---------------------- | ----------- | ------------------------------ |
| `job_id`               | `str`       | e.g. `J001`                    |
| `title`                | `str`       |                                |
| `company`              | `str`       |                                |
| `location`             | `str`       |                                |
| `salary`               | `str \| None`| displayed as-is                |
| `experience_required`  | `str \| None`| e.g. `FRESHER`, `1-3 years`    |
| `qualification`        | `str \| None`|                                |
| `description`          | `str \| None`|                                |
| `status`               | `JobStatus` | `OPEN` or `CLOSED` — only `OPEN` jobs are searchable |

### Application

| Field              | Type             | Notes                                    |
| ------------------ | ---------------- | ---------------------------------------- |
| `application_id`   | `str`            | e.g. `A001`                              |
| `candidate_id`     | `str`            | links to the candidate                   |
| `job_id`           | `str`            | links to the job                         |
| `status`           | `ApplicationStatus` | `APPLIED`, `INTERVIEW`, `OFFERED`, `REJECTED` |
| `application_date` | `str`            | ISO date (provisional format)            |
| `interview_date`   | `str \| None`    |                                          |

> PROVISIONAL: application statuses are a working set. Delphic's actual
> statuses will be confirmed with the Google Sheet data.

### FAQ

| Field      | Type     | Notes                                        |
| ---------- | -------- | -------------------------------------------- |
| `faq_id`   | `str`    | e.g. `F001`                                  |
| `category` | `str`    | uppercase category, e.g. `FEES`, `DOCUMENTS` |
| `answer`   | `str`    | approved answer text                         |
| `active`   | `bool`   | inactive FAQs are never returned             |

## Intents

Defined in `app/domain/intents.py` as an `enum.Enum` (`Intent`).

| Intent              | Meaning                                            |
| ------------------- | ------------------------------------------------- |
| `GREETING`          | start of conversation / hello                     |
| `FIND_JOB`          | search for matching jobs                          |
| `JOB_DETAILS`       | show full details of a specific job               |
| `ELIGIBILITY`       | eligibility / criteria for a job                  |
| `COMPENSATION`      | salary information                                |
| `LOCATION`          | work location information                         |
| `HOW_TO_APPLY`      | how to apply (answered from approved FAQ)         |
| `APPLICATION_STATUS`| status of the candidate's application             |
| `INTERVIEW`         | interview details                                 |
| `DOCUMENTS`         | required documents (answered from approved FAQ)   |
| `PROFILE_UPDATE`    | update candidate profile information              |
| `GENERAL_FAQ`       | general Q&A, expects an `faq_category` entity     |
| `HUMAN_SUPPORT`     | request to talk to a human recruiter              |
| `GOODBYE`           | end of conversation                               |
| `UNKNOWN`           | message that cannot be safely interpreted         |

> PROVISIONAL: the intent set may evolve with confirmed requirements. In the
> final product the intent is produced by an AI service; in Phase 2 it is
> supplied directly by the caller.

## IntentResult

`app/domain/intents.py` — a Pydantic model with `intent` and `entities`.

`Entities` is a small, fixed set of plain optional fields:

- `role`, `location`, `experience`, `qualification`
- `job_id`, `application_id`
- `faq_category`

Deliberately not a general-purpose entity framework.

## Conversation states

Defined in `app/domain/conversation.py` as `enum.Enum` (`ConversationState`):

`IDLE`, `WELCOME`, `COLLECTING_PROFILE`, `SEARCHING_JOBS`, `VIEWING_JOB`,
`APPLYING`, `CHECKING_APPLICATION`, `WAITING_FOR_INPUT`, `HUMAN_HANDOFF`,
`COMPLETED`.

States actively produced by the Phase 2 engine:

- `WELCOME` — after a greeting.
- `SEARCHING_JOBS` — after a job search result.
- `VIEWING_JOB` — while showing/asking about a specific job.
- `CHECKING_APPLICATION` — after application/interview lookups.
- `COLLECTING_PROFILE` — during profile updates.
- `WAITING_FOR_INPUT` — prompting for more information.
- `HUMAN_HANDOFF` — handoff to a recruiter.
- `COMPLETED` — after a goodbye.

> PROVISIONAL: `COLLECTING_PROFILE`, `APPLYING` and `IDLE` are declared because
> the final candidate workflow will use them, but no multi-turn collection or
> apply flow is implemented yet.

## ConversationContext

`app/domain/conversation.py` — a Pydantic model carrying only what Phase 2 needs:

- `whatsapp_number`
- `state`
- `current_intent`
- `entities`
- `candidate`
- `selected_job`
- `selected_application`

Deliberately **no message history and no persistence**. Each request is handled
statelessly; the candidate is re-resolved from the store on every message.

## Response

`app/domain/responses.py` — what the engine returns. Fields the messaging layer
needs:

- `message` — reply text
- `state` — resulting conversation state
- `handoff_required` — true when a human recruiter must take over
- `jobs` / `job` / `application` — structured payloads when relevant
- `info` — small key/value extras (e.g. `is_new_candidate`)

## What is firmly NOT in this phase

- No AI / LLM call for intent detection.
- No Google Sheets, Google Forms, WhatsApp, or any external service.
- No database, queue, cache, message broker, or ORM.
- No semantic FAQ search, embeddings, or vector store.
- No authentication, admin dashboard, or analytics.

## Required from Delphic (future phases)

- Real Google Sheet structures for candidates, jobs, applications, FAQs.
- Google API credentials.
- Approved FAQ content and answer wording.
- The final candidate registration questions / workflow.
- Final business rules for eligibility and statuses.