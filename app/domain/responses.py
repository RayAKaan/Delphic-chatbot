"""Conversation response model.

Caller (messaging layer) can determine the message text, the resulting
conversation state, whether human handoff is required, and any structured
business payload (e.g. list of jobs, selected job, application).
"""

from typing import Any

from pydantic import BaseModel, Field

from app.domain.conversation import ConversationState
from app.domain.models import Application, Job


class Response(BaseModel):
    message: str
    state: ConversationState
    handoff_required: bool = False
    jobs: list[Job] = Field(default_factory=list)
    job: Job | None = None
    application: Application | None = None
    info: dict[str, Any] = Field(default_factory=dict)
