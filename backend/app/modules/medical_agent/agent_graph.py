"""
Lightweight Backward-Compatibility Facade for agent_graph.
Re-exports symbols from the modular subpackages (agent, context, memory, skills, tools).
"""

from app.modules.medical_agent.context.state import MedicalAgentState, AgentStepInfo
from app.modules.medical_agent.memory.checkpointer import sqlite_checkpointer, get_sqlite_checkpointer
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
    OutputValidator,
    OutputValidationReport,
    ClinicalSOAPOutputSchema,
    GeneralConsultationKnowledgeSchema,
    SIMRSTransactionReportSchema,
    AudioConsultationSOAPSchema
)

__all__ = [
    "MedicalAgentState",
    "AgentStepInfo",
    "sqlite_checkpointer",
    "get_sqlite_checkpointer",
    "medical_agent_graph",
    "build_medical_agent_graph",
    "node_planner",
    "node_fetch_patient_history",
    "node_fetch_patient_anamnesis",
    "node_eval_simrs_labs",
    "node_diagnostic_recommendation",
    "node_km_disease_explanations",
    "node_km_red_flag_detection",
    "node_km_medication_recommendation",
    "node_patient_drug_safety",
    "node_execute_tools",
    "node_gemini_synthesis",
    "_generate_fallback_synthesis",
    "node_validate_output",
    "node_audio_transcription",
    "node_audio_soap_summary",
    "OutputValidator",
    "OutputValidationReport",
    "ClinicalSOAPOutputSchema",
    "GeneralConsultationKnowledgeSchema",
    "SIMRSTransactionReportSchema",
    "AudioConsultationSOAPSchema"
]
