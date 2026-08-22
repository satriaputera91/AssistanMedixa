"""
Medical Agent Module - Modular Architecture:
- agent: LangGraph StateGraph, Planner, Synthesis, Output Validator, Logging Utils
- context: State definitions, Pydantic Request/Response Schemas, Clinical Prompts
- memory: SQLite Session Checkpointer
- skills: Anamnesis, Diagnostics, Pharmacology, Red Flags, Disease Explanation, Audio STT/SOAP, Output Schemas
- tools: SIMRS MCP Tools, Clinical Calculations, Vector RAG Search & Literature Guidelines
"""

# Agent Core & Graph
from app.modules.medical_agent.agent.graph import (
    medical_agent_graph,
    build_medical_agent_graph,
    node_execute_tools,
    _route_entry_point,
    _route_planner
)
from app.modules.medical_agent.agent.planner import (
    node_planner,
    _debug_node_start,
    _debug_node_end,
    _debug_edge
)
from app.modules.medical_agent.agent.synthesis import (
    node_gemini_synthesis,
    _generate_fallback_synthesis
)
from app.modules.medical_agent.agent.validator import node_validate_output
from app.modules.medical_agent.agent.logging_utils import (
    log_node_start,
    log_node_end,
    log_edge_transition
)

# Context: State & Schemas
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
    SOAReviewRequest,
    SOAReviewResponse,
    SOAConfirmationRequest,
    SOARevisionConfirmationRequest
)

# Memory: Checkpointer
from app.modules.medical_agent.memory.checkpointer import (
    sqlite_checkpointer,
    get_sqlite_checkpointer
)

# Skills: Nodes & Schemas
from app.modules.medical_agent.skills.anamnesis import (
    node_fetch_patient_history,
    node_fetch_patient_anamnesis
)
from app.modules.medical_agent.skills.diagnostics import (
    node_eval_simrs_labs,
    node_diagnostic_recommendation
)
from app.modules.medical_agent.skills.pharmacology import (
    node_km_medication_recommendation,
    node_patient_drug_safety
)
from app.modules.medical_agent.skills.red_flags import node_km_red_flag_detection
from app.modules.medical_agent.skills.disease_explanation import node_km_disease_explanations
from app.modules.medical_agent.skills.audio_soap import (
    node_audio_transcription,
    node_audio_soap_summary
)
from app.modules.medical_agent.skills.output_schemas import (
    VitalSignsData,
    LabItemData,
    PatientDemographicsData,
    SubjectiveData,
    ObjectiveData,
    DiagnosisItemData,
    AssessmentData,
    MedicationItemData,
    RedFlagData,
    PlanData,
    ClinicalSOAPOutputSchema,
    GeneralConsultationKnowledgeSchema,
    SIMRSTransactionReportSchema,
    DiarizedUtterance,
    AudioDiarizationSchema,
    AudioConsultationSOAPSchema,
    OutputValidationReport,
    OutputValidator
)

# Tools: SIMRS, Clinical, and RAG
from app.modules.medical_agent.tools.simrs_tools import (
    tool_simrs_get_patient_profile,
    tool_simrs_get_patient_history,
    tool_simrs_get_patient_anamnesis,
    tool_simrs_get_patient_labs,
    tool_simrs_update_patient_record
)
from app.modules.medical_agent.tools.clinical_tools import (
    tool_query_patient_ehr,
    tool_generate_diagnostic_recommendations,
    tool_check_drug_interactions
)
from app.modules.medical_agent.tools.rag_tools import (
    tool_vector_rag_search,
    tool_get_clinical_literature_summary
)

tool_qdrant_vector_rag_search = tool_vector_rag_search
tool_search_medical_references = tool_get_clinical_literature_summary

__all__ = [
    # Graph & Nodes
    "medical_agent_graph",
    "build_medical_agent_graph",
    "node_planner",
    "node_execute_tools",
    "node_gemini_synthesis",
    "node_validate_output",
    "node_fetch_patient_history",
    "node_fetch_patient_anamnesis",
    "node_eval_simrs_labs",
    "node_diagnostic_recommendation",
    "node_km_medication_recommendation",
    "node_patient_drug_safety",
    "node_km_red_flag_detection",
    "node_km_disease_explanations",
    "node_audio_transcription",
    "node_audio_soap_summary",
    "log_node_start",
    "log_node_end",
    "log_edge_transition",
    # State & Schemas
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
    "SOAReviewRequest",
    "SOAReviewResponse",
    "SOAConfirmationRequest",
    "SOARevisionConfirmationRequest",
    # Memory
    "sqlite_checkpointer",
    "get_sqlite_checkpointer",
    # Output Models & Validators
    "VitalSignsData",
    "LabItemData",
    "PatientDemographicsData",
    "SubjectiveData",
    "ObjectiveData",
    "DiagnosisItemData",
    "AssessmentData",
    "MedicationItemData",
    "RedFlagData",
    "PlanData",
    "ClinicalSOAPOutputSchema",
    "GeneralConsultationKnowledgeSchema",
    "SIMRSTransactionReportSchema",
    "DiarizedUtterance",
    "AudioDiarizationSchema",
    "AudioConsultationSOAPSchema",
    "OutputValidationReport",
    "OutputValidator",
    # Tools
    "tool_simrs_get_patient_profile",
    "tool_simrs_get_patient_history",
    "tool_simrs_get_patient_anamnesis",
    "tool_simrs_get_patient_labs",
    "tool_simrs_update_patient_record",
    "tool_query_patient_ehr",
    "tool_generate_diagnostic_recommendations",
    "tool_check_drug_interactions",
    "tool_vector_rag_search",
    "tool_get_clinical_literature_summary",
    "tool_qdrant_vector_rag_search",
    "tool_search_medical_references"
]
