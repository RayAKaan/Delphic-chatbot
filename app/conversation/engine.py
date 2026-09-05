"""Deterministic conversation engine for Phase 2.

The engine interprets an already-structured IntentResult, applies mock
business logic, and returns a Response. It does NOT call any AI model,
Google Sheets, or WhatsApp in this phase.
"""

from app.conversation import messages
from app.data.stores import (
    ApplicationStore,
    CandidateStore,
    FAQStore,
    JobStore,
)
from app.domain.conversation import ConversationContext, ConversationState
from app.domain.intents import Intent, IntentResult
from app.domain.models import Application, Job
from app.domain.responses import Response
from app.services import applications, candidates, faqs, jobs


class ConversationEngine:
    def __init__(
        self,
        candidates: CandidateStore | None = None,
        jobs: JobStore | None = None,
        applications: ApplicationStore | None = None,
        faqs: FAQStore | None = None,
    ) -> None:
        self.candidate_store = candidates or CandidateStore()
        self.job_store = jobs or JobStore()
        self.application_store = applications or ApplicationStore()
        self.faq_store = faqs or FAQStore()
        self._handlers = {
            Intent.GREETING: self._handle_greeting,
            Intent.FIND_JOB: self._handle_find_job,
            Intent.JOB_DETAILS: self._handle_job_details,
            Intent.ELIGIBILITY: self._handle_job_attribute,
            Intent.COMPENSATION: self._handle_job_attribute,
            Intent.LOCATION: self._handle_job_attribute,
            Intent.HOW_TO_APPLY: self._handle_faq,
            Intent.APPLICATION_STATUS: self._handle_application_status,
            Intent.INTERVIEW: self._handle_interview,
            Intent.DOCUMENTS: self._handle_faq,
            Intent.PROFILE_UPDATE: self._handle_profile_update,
            Intent.GENERAL_FAQ: self._handle_faq,
            Intent.HUMAN_SUPPORT: self._handle_human_support,
            Intent.GOODBYE: self._handle_goodbye,
            Intent.UNKNOWN: self._handle_unknown,
        }

    def handle(self, context: ConversationContext, intent_result: IntentResult) -> Response:
        context.current_intent = intent_result.intent
        context.entities = intent_result.entities
        context.candidate = self.candidate_store.find_by_whatsapp(context.whatsapp_number)

        handler = self._handlers.get(intent_result.intent)
        if handler is None:
            return self._handle_unknown(context, intent_result)
        return handler(context, intent_result)

    # --- Intent handlers -------------------------------------------------

    def _handle_greeting(self, context: ConversationContext, _: IntentResult) -> Response:
        candidate, is_new = candidates.find_or_create(self.candidate_store, context.whatsapp_number)
        context.candidate = candidate
        return Response(
            message=messages.WELCOME,
            state=ConversationState.WELCOME,
            info={"is_new_candidate": is_new, "candidate_id": candidate.candidate_id},
        )

    def _handle_find_job(self, context: ConversationContext, intent: IntentResult) -> Response:
        matches = jobs.search_jobs(self.job_store, intent.entities)
        context.state = ConversationState.SEARCHING_JOBS
        if not matches:
            return Response(
                message=messages.NO_JOBS_FOUND,
                state=ConversationState.SEARCHING_JOBS,
            )
        return Response(
            message=self._format_job_list(matches),
            state=ConversationState.SEARCHING_JOBS,
            jobs=matches,
        )

    def _handle_job_details(self, context: ConversationContext, intent: IntentResult) -> Response:
        job = self._resolve_job(context, intent.entities.job_id)
        if job is None:
            return Response(
                message=(
                    "I couldn't find that job. Ask me to find jobs for a role "
                    "or location, and I'll share the matching openings."
                ),
                state=ConversationState.WAITING_FOR_INPUT,
            )
        context.selected_job = job
        context.state = ConversationState.VIEWING_JOB
        return Response(
            message=self._format_job_details(job),
            state=ConversationState.VIEWING_JOB,
            job=job,
        )

    def _handle_job_attribute(self, context: ConversationContext, intent: IntentResult) -> Response:
        """Shared handler for ELIGIBILITY / COMPENSATION / LOCATION."""
        job = self._resolve_job(context, intent.entities.job_id)
        if job is None:
            return Response(
                message=(
                    "Which job would you like to know about? Share its job ID "
                    "(e.g. J001) or ask me to find jobs for you."
                ),
                state=ConversationState.WAITING_FOR_INPUT,
            )
        context.selected_job = job
        context.state = ConversationState.VIEWING_JOB
        if intent.intent == Intent.ELIGIBILITY:
            text = (
                f"For {job.title} you need:\n"
                f"- Experience: {job.experience_required or 'Not specified'}\n"
                f"- Qualification: {job.qualification or 'Not specified'}"
            )
        elif intent.intent == Intent.COMPENSATION:
            text = f"The salary for {job.title} is: {job.salary or 'Not specified'}."
        else:  # LOCATION
            text = f"The work location for {job.title} is: {job.location}."
        return Response(message=text, state=ConversationState.VIEWING_JOB, job=job)

    def _handle_application_status(self, context: ConversationContext, _: IntentResult) -> Response:
        if context.candidate is None:
            return Response(
                message=(
                    "I can't find any application for this number yet. "
                    "You can ask me to find jobs, or talk to a recruiter for help."
                ),
                state=ConversationState.CHECKING_APPLICATION,
            )
        application = applications.lookup_application(
            self.application_store, context.candidate.candidate_id
        )
        context.state = ConversationState.CHECKING_APPLICATION
        if application is None:
            return Response(
                message=(
                    "You don't have any application with us right now. "
                    "Ask me to find jobs and we can get you started."
                ),
                state=ConversationState.CHECKING_APPLICATION,
            )
        context.selected_application = application
        job = self.job_store.find_open(application.job_id)
        return Response(
            message=self._format_application(application, job),
            state=ConversationState.CHECKING_APPLICATION,
            application=application,
        )

    def _handle_interview(self, context: ConversationContext, _: IntentResult) -> Response:
        if context.candidate is None:
            return Response(
                message="I can't find any interview scheduled for this number yet.",
                state=ConversationState.CHECKING_APPLICATION,
            )
        application = applications.lookup_application(
            self.application_store, context.candidate.candidate_id
        )
        if application is None or application.interview_date is None:
            return Response(
                message=(
                    "There's no interview scheduled for you right now. "
                    "If you think this is a mistake, ask to talk to a recruiter."
                ),
                state=ConversationState.CHECKING_APPLICATION,
            )
        job = self.job_store.find_open(application.job_id)
        return Response(
            message=(
                f"Your interview for {job.title if job else application.job_id} "
                f"is scheduled for {application.interview_date}."
            ),
            state=ConversationState.CHECKING_APPLICATION,
            application=application,
        )

    def _handle_faq(self, _: ConversationContext, intent: IntentResult) -> Response:
        category = intent.entities.faq_category
        answer = faqs.lookup_faq(self.faq_store, category) if category else None
        if category is None:
            return Response(
                message=(
                    "I can help with questions about fees, documents, how to "
                    "apply, timings and more. What would you like to know?"
                ),
                state=ConversationState.WAITING_FOR_INPUT,
            )
        if answer is None:
            return Response(
                message=messages.FAQ_NOT_FOUND,
                state=ConversationState.HUMAN_HANDOFF,
                handoff_required=True,
            )
        return Response(message=answer, state=ConversationState.WAITING_FOR_INPUT)

    def _handle_profile_update(
        self, context: ConversationContext, intent: IntentResult
    ) -> Response:
        if context.candidate is None:
            return Response(
                message=(
                    "I don't have a profile for this number yet. Ask to talk "
                    "to a recruiter and they will register you."
                ),
                state=ConversationState.HUMAN_HANDOFF,
                handoff_required=True,
            )
        e = intent.entities
        entity_to_field = {
            "role": "preferred_role",
            "location": "preferred_location",
            "experience": "experience",
            "qualification": "qualification",
        }
        updates = {
            field: getattr(e, entity)
            for entity, field in entity_to_field.items()
            if getattr(e, entity) is not None
        }
        if not updates:
            return Response(
                message=(
                    "Happy to update your profile. Tell me what to change, "
                    "for example your experience, qualification, preferred "
                    "role or preferred location."
                ),
                state=ConversationState.COLLECTING_PROFILE,
            )
        updated = candidates.update_from_entities(self.candidate_store, context.candidate, updates)
        context.candidate = updated
        changed = [field.replace("_", " ") for field in updates]
        return Response(
            message=f"Your profile has been updated: {', '.join(changed)}.",
            state=ConversationState.COLLECTING_PROFILE,
            info={"updated_fields": list(updates)},
        )

    def _handle_human_support(self, context: ConversationContext, _: IntentResult) -> Response:
        context.state = ConversationState.HUMAN_HANDOFF
        return Response(
            message=messages.HUMAN_HANDOFF,
            state=ConversationState.HUMAN_HANDOFF,
            handoff_required=True,
        )

    def _handle_goodbye(self, context: ConversationContext, _: IntentResult) -> Response:
        context.state = ConversationState.COMPLETED
        return Response(message=messages.THANK_YOU, state=ConversationState.COMPLETED)

    def _handle_unknown(self, context: ConversationContext, _: IntentResult) -> Response:
        context.state = ConversationState.HUMAN_HANDOFF
        return Response(
            message=f"{messages.FALLBACK}\n\n{messages.HUMAN_HANDOFF}",
            state=ConversationState.HUMAN_HANDOFF,
            handoff_required=True,
        )

    # --- Helpers ---------------------------------------------------------

    def _resolve_job(self, context: ConversationContext, job_id: str | None) -> Job | None:
        if job_id:
            return jobs.get_job_details(self.job_store, job_id)
        return context.selected_job

    @staticmethod
    def _format_job_list(job_list: list[Job]) -> str:
        lines = ["Here are the current openings that match your search:"]
        for index, job in enumerate(job_list, start=1):
            lines.append(
                f"{index}. {job.title} - {job.company} ({job.location})\n"
                f"   Salary: {job.salary or 'Not specified'} | "
                f"Experience: {job.experience_required or 'Not specified'}"
            )
        lines.append("Reply with a job ID (e.g. J001) to see full details.")
        return "\n".join(lines)

    @staticmethod
    def _format_job_details(job: Job) -> str:
        return (
            f"{job.title} at {job.company}\n"
            f"Location: {job.location}\n"
            f"Salary: {job.salary or 'Not specified'}\n"
            f"Experience required: {job.experience_required or 'Not specified'}\n"
            f"Qualification: {job.qualification or 'Not specified'}\n"
            f"Description: {job.description or 'Not specified'}"
        )

    @staticmethod
    def _format_application(application: Application, job: Job | None) -> str:
        job_line = f"{job.title} ({application.job_id})" if job else f"job {application.job_id}"
        interview = application.interview_date or "To be scheduled"
        return (
            f"Application for {job_line}\n"
            f"Status: {application.status}\n"
            f"Applied on: {application.application_date}\n"
            f"Interview: {interview}"
        )


_conversation_engine: ConversationEngine | None = None


def get_conversation_engine() -> ConversationEngine:
    global _conversation_engine
    if _conversation_engine is None:
        _conversation_engine = ConversationEngine()
    return _conversation_engine
