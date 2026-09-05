import pytest

from app.conversation import ConversationEngine
from app.domain.conversation import ConversationContext, ConversationState
from app.domain.intents import Entities, Intent, IntentResult

NEW_NUMBER = "+919000000001"
UNKNOWN_NUMBER = "+919999999999"


@pytest.fixture
def engine() -> ConversationEngine:
    return ConversationEngine()


def handle(engine, whatsapp_number: str, intent: Intent, entities: Entities | None = None):
    context = ConversationContext(whatsapp_number=whatsapp_number)
    result = engine.handle(
        context,
        IntentResult(intent=intent, entities=entities or Entities()),
    )
    return result, context


def test_greeting_new_candidate(engine) -> None:
    result, context = handle(engine, UNKNOWN_NUMBER, Intent.GREETING)
    assert result.state == ConversationState.WELCOME
    assert result.info["is_new_candidate"] is True
    assert context.candidate is not None


def test_greeting_existing_candidate(engine) -> None:
    result, context = handle(engine, NEW_NUMBER, Intent.GREETING)
    assert result.state == ConversationState.WELCOME
    assert result.info["is_new_candidate"] is False
    assert context.candidate.candidate_id == "C001"


def test_find_job_returns_matching_jobs(engine) -> None:
    result, _ = handle(
        engine,
        NEW_NUMBER,
        Intent.FIND_JOB,
        Entities(location="Bangalore", experience="FRESHER"),
    )
    assert result.state == ConversationState.SEARCHING_JOBS
    assert [j.job_id for j in result.jobs] == ["J001", "J004"]


def test_find_job_no_matches(engine) -> None:
    result, _ = handle(engine, NEW_NUMBER, Intent.FIND_JOB, Entities(role="pilot"))
    assert result.state == ConversationState.SEARCHING_JOBS
    assert result.jobs == []
    assert "don't have any matching openings" in result.message.lower()


def test_job_details_by_id(engine) -> None:
    result, context = handle(engine, NEW_NUMBER, Intent.JOB_DETAILS, Entities(job_id="J001"))
    assert result.state == ConversationState.VIEWING_JOB
    assert result.job is not None and result.job.job_id == "J001"
    assert context.selected_job is not None


def test_job_details_missing(engine) -> None:
    result, _ = handle(engine, NEW_NUMBER, Intent.JOB_DETAILS, Entities(job_id="J999"))
    assert result.state == ConversationState.WAITING_FOR_INPUT
    assert result.job is None


def test_job_details_closed_job_rejected(engine) -> None:
    result, _ = handle(engine, NEW_NUMBER, Intent.JOB_DETAILS, Entities(job_id="J007"))
    assert result.job is None
    assert result.state == ConversationState.WAITING_FOR_INPUT


def test_eligibility_with_job_id(engine) -> None:
    result, _ = handle(engine, NEW_NUMBER, Intent.ELIGIBILITY, Entities(job_id="J001"))
    assert result.state == ConversationState.VIEWING_JOB
    assert "FRESHER" in result.message


def test_compensation_with_job_id(engine) -> None:
    result, _ = handle(engine, NEW_NUMBER, Intent.COMPENSATION, Entities(job_id="J001"))
    assert "₹18,000" in result.message


def test_location_with_job_id(engine) -> None:
    result, _ = handle(engine, NEW_NUMBER, Intent.LOCATION, Entities(job_id="J001"))
    assert "Bangalore" in result.message


def test_compensation_without_job_prompts(engine) -> None:
    result, _ = handle(engine, NEW_NUMBER, Intent.COMPENSATION)
    assert result.state == ConversationState.WAITING_FOR_INPUT


def test_how_to_apply_uses_approved_faq(engine) -> None:
    result, _ = handle(engine, NEW_NUMBER, Intent.HOW_TO_APPLY)
    assert result.state == ConversationState.WAITING_FOR_INPUT
    assert "apply" in result.message.lower()


def test_general_faq_specific_category(engine) -> None:
    result, _ = handle(engine, NEW_NUMBER, Intent.GENERAL_FAQ, Entities(faq_category="DOCUMENTS"))
    assert "certificates" in result.message.lower()


def test_general_faq_missing_category_prompts(engine) -> None:
    result, _ = handle(engine, NEW_NUMBER, Intent.GENERAL_FAQ)
    assert result.state == ConversationState.WAITING_FOR_INPUT


def test_general_faq_unknown_category_handoff(engine) -> None:
    result, _ = handle(engine, NEW_NUMBER, Intent.GENERAL_FAQ, Entities(faq_category="NONEXISTENT"))
    assert result.handoff_required is True
    assert result.state == ConversationState.HUMAN_HANDOFF


def test_application_status_existing_candidate(engine) -> None:
    result, _ = handle(engine, NEW_NUMBER, Intent.APPLICATION_STATUS)
    assert result.state == ConversationState.CHECKING_APPLICATION
    assert result.application is not None
    assert result.application.status == "INTERVIEW"
    assert "2026-09-10" in result.message


def test_application_status_no_application(engine) -> None:
    result, _ = handle(engine, "+919000000003", Intent.APPLICATION_STATUS)
    assert result.state == ConversationState.CHECKING_APPLICATION
    assert result.application is None
    assert "don't have any application" in result.message.lower()


def test_interview_scheduled(engine) -> None:
    result, _ = handle(engine, NEW_NUMBER, Intent.INTERVIEW)
    assert "2026-09-10" in result.message


def test_interview_not_scheduled(engine) -> None:
    result, _ = handle(engine, "+919000000003", Intent.INTERVIEW)
    assert "no interview" in result.message.lower()


def test_profile_update_applies_field(engine) -> None:
    result, _ = handle(engine, NEW_NUMBER, Intent.PROFILE_UPDATE, Entities(role="data entry"))
    assert "updated" in result.message.lower()
    assert result.state == ConversationState.COLLECTING_PROFILE


def test_profile_update_without_data_prompts(engine) -> None:
    result, _ = handle(engine, NEW_NUMBER, Intent.PROFILE_UPDATE)
    assert result.state == ConversationState.COLLECTING_PROFILE
    assert "what to change" in result.message.lower()


def test_profile_update_unknown_number_handoff(engine) -> None:
    result, _ = handle(engine, UNKNOWN_NUMBER, Intent.PROFILE_UPDATE)
    assert result.handoff_required is True


def test_human_support_triggers_handoff(engine) -> None:
    result, _ = handle(engine, NEW_NUMBER, Intent.HUMAN_SUPPORT)
    assert result.handoff_required is True
    assert result.state == ConversationState.HUMAN_HANDOFF


def test_goodbye_completes_conversation(engine) -> None:
    result, context = handle(engine, NEW_NUMBER, Intent.GOODBYE)
    assert result.state == ConversationState.COMPLETED
    assert "thank you" in result.message.lower()
    assert context.state == ConversationState.COMPLETED


def test_unknown_intent_uses_safe_fallback_and_handoff(engine) -> None:
    result, _ = handle(engine, NEW_NUMBER, Intent.UNKNOWN)
    assert result.handoff_required is True
    assert result.state == ConversationState.HUMAN_HANDOFF


def test_new_candidate_gets_created_then_found(engine) -> None:
    first, first_context = handle(engine, UNKNOWN_NUMBER, Intent.GREETING)
    assert first.info["is_new_candidate"] is True
    assert first_context.candidate is not None
    second, second_context = handle(engine, UNKNOWN_NUMBER, Intent.GREETING)
    assert second.info["is_new_candidate"] is False
    assert second_context.candidate.candidate_id == first_context.candidate.candidate_id


def test_conversation_flow_greeting_then_jobs(engine) -> None:
    greeting, _ = handle(engine, UNKNOWN_NUMBER, Intent.GREETING)
    assert greeting.info["is_new_candidate"] is True
    search, _ = handle(
        engine,
        UNKNOWN_NUMBER,
        Intent.FIND_JOB,
        Entities(role="customer support", location="Bangalore", experience="FRESHER"),
    )
    assert [j.job_id for j in search.jobs] == ["J001"]
    details, _ = handle(engine, UNKNOWN_NUMBER, Intent.JOB_DETAILS, Entities(job_id="J001"))
    assert details.job.title == "Customer Support Executive"
    goodbye, _ = handle(engine, UNKNOWN_NUMBER, Intent.GOODBYE)
    assert goodbye.state == ConversationState.COMPLETED
