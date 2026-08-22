"""
Medical Agent Module - Modular Subpackage Architecture:
- agent: LangGraph StateGraph, Planner Node, Synthesis, Validator
- context: State schemas, Request/Response DTOs, Clinical Prompts
- memory: SQLite Checkpointer, Conversation Memory
- skills: Anamnesis, Diagnostics, Pharmacology, Red Flags, Disease Explanation, Audio SOAP, Output Schemas
- tools: Clinical Calculations, SIMRS MCP Tools, Qdrant Vector RAG
"""

from app.modules.medical_agent.agent.graph import medical_agent_graph, build_medical_agent_graph
from app.modules.medical_agent.context.state import MedicalAgentState, AgentStepInfo
from app.modules.medical_agent.context.schemas import (
    AgentChatRequest,
    AgentChatResponse,
    AgentStepSchema,
    OutputValidationSchema,
    SOAContentSchema,
    SOAPContentSchema,
    SOAChangeSchema,
    SOANoteSchema,
    SOARevisionConfirmationRequest
)
from app.modules.medical_agent.memory.checkpointer import sqlite_checkpointer, get_sqlite_checkpointer
from app.modules.medical_agent.skills.output_schemas import OutputValidator, OutputValidationReport

__all__ = [
    "medical_agent_graph",
    "build_medical_agent_graph",
    "MedicalAgentState",
    "AgentStepInfo",
    "AgentChatRequest",
    "AgentChatResponse",
    "AgentStepSchema",
    "OutputValidationSchema",
    "SOAContentSchema",
    "SOAPContentSchema",
    "SOAChangeSchema",
    "SOANoteSchema",
    "SOARevisionConfirmationRequest",
    "sqlite_checkpointer",
    "get_sqlite_checkpointer",
    "OutputValidator",
    "OutputValidationReport"
]
