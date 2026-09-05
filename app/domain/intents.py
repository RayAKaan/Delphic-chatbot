"""Intent definitions for the Delphic chatbot.

In the final product the intent will be produced by an AI service. In this
phase, intent results are provided directly by mocks and tests.
"""

from enum import Enum

from pydantic import BaseModel, Field


class Intent(str, Enum):
    """The interpreted meaning of a jobseeker's message.

    PROVISIONAL: the exact set may evolve as Delphic confirms requirements.
    """

    GREETING = "GREETING"
    FIND_JOB = "FIND_JOB"
    JOB_DETAILS = "JOB_DETAILS"
    ELIGIBILITY = "ELIGIBILITY"
    COMPENSATION = "COMPENSATION"
    LOCATION = "LOCATION"
    HOW_TO_APPLY = "HOW_TO_APPLY"
    APPLICATION_STATUS = "APPLICATION_STATUS"
    INTERVIEW = "INTERVIEW"
    DOCUMENTS = "DOCUMENTS"
    PROFILE_UPDATE = "PROFILE_UPDATE"
    GENERAL_FAQ = "GENERAL_FAQ"
    HUMAN_SUPPORT = "HUMAN_SUPPORT"
    GOODBYE = "GOODBYE"
    UNKNOWN = "UNKNOWN"


class Entities(BaseModel):
    """Note: PROVISIONAL. Not a complex entity framework.

    `faq_category` is a plain string slot used by GENERAL_FAQ lookups.
    """

    role: str | None = None
    location: str | None = None
    experience: str | None = None
    qualification: str | None = None
    job_id: str | None = None
    application_id: str | None = None
    faq_category: str | None = None


class IntentResult(BaseModel):
    """A structured interpretation of a jobseeker request."""

    intent: Intent
    entities: Entities = Field(default_factory=Entities)
