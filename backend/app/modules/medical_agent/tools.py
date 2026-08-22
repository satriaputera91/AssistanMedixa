"""
Backward-compatibility forwarder for tools.
"""
from app.modules.medical_agent.tools.simrs_tools import (
    tool_simrs_get_patient_profile,
    tool_simrs_get_patient_history,
    tool_simrs_get_patient_anamnesis,
    tool_simrs_get_patient_labs,
    tool_simrs_update_patient_record
)
from app.modules.medical_agent.tools.clinical_tools import (
    tool_query_patient_ehr,
    tool_generate_diagnostic_recommendations
)
from app.modules.medical_agent.tools.rag_tools import (
    tool_vector_rag_search,
    tool_get_clinical_literature_summary
)

__all__ = [
    "tool_simrs_get_patient_profile",
    "tool_simrs_get_patient_history",
    "tool_simrs_get_patient_anamnesis",
    "tool_simrs_get_patient_labs",
    "tool_simrs_update_patient_record",
    "tool_query_patient_ehr",
    "tool_generate_diagnostic_recommendations",
    "tool_vector_rag_search",
    "tool_get_clinical_literature_summary"
]
