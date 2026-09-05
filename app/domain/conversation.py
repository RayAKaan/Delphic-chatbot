"""Conversation state and context for the Delphic chatbot."""

from enum import Enum

from pydantic import BaseModel, Field

from app.domain.intents import Entities, Intent
from app.domain.models import Application, Candidate, Job

PROVISIONAL = (
    "PROVISIONAL: conversation states are working definitions and may change as "
    "Delphic confirms its final candidate workflow."
)


class ConversationState(str, Enum):
    IDLE = "IDLE"
    WELCOME = "WELCOME"
    COLLECTING_PROFILE = "COLLECTING_PROFILE"
    SEARCHING_JOBS = "SEARCHING_JOBS"
    VIEWING_JOB = "VIEWING_JOB"
    APPLYING = "APPLYING"
    CHECKING_APPLICATION = "CHECKING_APPLICATION"
    WAITING_FOR_INPUT = "WAITING_FOR_INPUT"
    HUMAN_HANDOFF = "HUMAN_HANDOFF"
    COMPLETED = "COMPLETED"


class ConversationContext(BaseModel):
    """Minimal state carried across messages in a conversation.

    Deliberately small. No conversation history is stored in this phase and
    there is no persistent conversation storage.
    """

    whatsapp_number: str
    state: ConversationState = ConversationState.IDLE
    current_intent: Intent | None = None
    entities: Entities = Field(default_factory=Entities)
    candidate: Candidate | None = None
    selected_job: Job | None = None
    selected_application: Application | None = None

    @property
    def is_existing_candidate(self) -> bool:
        return self.candidate is not None
