from app.modules.medical_agent.tools.simrs_tools import (
    tool_simrs_get_patient,
    tool_simrs_get_patient_data,
    tool_simrs_get_patient_profile,
    tool_simrs_get_patient_history,
    tool_simrs_get_patient_anamnesis,
    tool_simrs_get_patient_labs,
    tool_simrs_update_patient_record,
    get_active_mcp_tools,
    get_gemini_mcp_function_declarations,
    execute_mcp_tool_dynamically,
    execute_gemini_function_call,
    run_gemini_with_mcp_tools,
)
from app.modules.medical_agent.mcp_function_calling import (
    MCPGeminiFunctionAdapter,
    GeminiMCPService,
    gemini_mcp_service,
)
from app.modules.medical_agent.tools.clinical_tools import (
    tool_query_patient_ehr,
    tool_generate_diagnostic_recommendations,
    tool_generate_med_generation,
    tool_detect_clinical_red_flags,
    tool_check_drug_interactions
)
from app.modules.medical_agent.tools.rag_tools import (
    tool_vector_rag_search,
    tool_get_clinical_literature_summary
)

# Backward-compatibility aliases
tool_qdrant_vector_rag_search = tool_vector_rag_search
tool_search_medical_references = tool_get_clinical_literature_summary

__all__ = [
    "tool_simrs_get_patient",
    "tool_simrs_get_patient_data",
    "tool_simrs_get_patient_profile",
    "tool_simrs_get_patient_history",
    "tool_simrs_get_patient_anamnesis",
    "tool_simrs_get_patient_labs",
    "tool_simrs_update_patient_record",
    "get_active_mcp_tools",
    "get_gemini_mcp_function_declarations",
    "execute_mcp_tool_dynamically",
    "execute_gemini_function_call",
    "run_gemini_with_mcp_tools",
    "MCPGeminiFunctionAdapter",
    "GeminiMCPService",
    "gemini_mcp_service",
    "tool_query_patient_ehr",
    "tool_generate_diagnostic_recommendations",
    "tool_generate_med_generation",
    "tool_detect_clinical_red_flags",
    "tool_check_drug_interactions",
    "tool_vector_rag_search",
    "tool_get_clinical_literature_summary",
    "tool_qdrant_vector_rag_search",
    "tool_search_medical_references"
]

