"""Development/test endpoint for exercising the conversation engine.

NOT the production WhatsApp webhook. This endpoint exists only to run the
backend locally before WhatsApp is integrated. It expects a structured IntentResult;
in production the intent will be produced by an AI service.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.conversation import get_conversation_engine
from app.domain.conversation import ConversationContext
from app.domain.intents import Entities, Intent, IntentResult
from app.domain.responses import Response

router = APIRouter(prefix="/api/v1", tags=["conversation"])


class TestConversationRequest(BaseModel):
    whatsapp_number: str = Field(description="Jobseeker's WhatsApp number (mock).")
    intent: Intent
    entities: Entities = Field(default_factory=Entities)


@router.post("/conversations/test")
def test_conversation(payload: TestConversationRequest) -> Response:
    context = ConversationContext(whatsapp_number=payload.whatsapp_number)
    engine = get_conversation_engine()
    return engine.handle(context, IntentResult(intent=payload.intent, entities=payload.entities))
