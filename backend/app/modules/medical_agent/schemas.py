"""
Backward-compatibility forwarder for schemas.
"""
from app.modules.medical_agent.context.schemas import (
    AgentChatRequest,
    AgentChatResponse,
    AgentStepSchema,
    OutputValidationSchema,
    SOAContentSchema,
    SOAPContentSchema,
    SOAChangeSchema,
    SOANoteSchema,
    SOAReviewRequest,
    SOAReviewResponse,
    SOAConfirmationRequest,
    SOARevisionConfirmationRequest
)

__all__ = [
    "AgentChatRequest",
    "AgentChatResponse",
    "AgentStepSchema",
    "OutputValidationSchema",
    "SOAContentSchema",
    "SOAPContentSchema",
    "SOAChangeSchema",
    "SOANoteSchema",
    "SOAReviewRequest",
    "SOAReviewResponse",
    "SOAConfirmationRequest",
    "SOARevisionConfirmationRequest"
]
