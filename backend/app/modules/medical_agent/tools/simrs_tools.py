from typing import Dict, Any
from app.modules.mcp.simrs_client import simrs_mcp_client

def tool_simrs_get_patient_profile(mrn: str) -> Dict[str, Any]:
    """Fetches SIMRS patient demographics, NIK, BPJS status, age, sex, and clinic assignment via MCP."""
    return simrs_mcp_client.get_patient_profile(mrn)

def tool_simrs_get_patient_history(mrn: str) -> Dict[str, Any]:
    """Retrieves SIMRS patient past admissions, chronic conditions, and historical lab panels via MCP."""
    return simrs_mcp_client.get_patient_history(mrn)

def tool_simrs_get_patient_anamnesis(mrn: str) -> Dict[str, Any]:
    """Retrieves comprehensive clinical anamnesis (Keluhan Utama, RPS, RPD, RPK, Alergi) via SIMRS MCP."""
    return simrs_mcp_client.get_patient_anamnesis(mrn)

def tool_simrs_get_patient_labs(mrn: str) -> Dict[str, Any]:
    """Fetches SIMRS patient latest laboratory panels, serial results, and vital signs via MCP."""
    return simrs_mcp_client.get_patient_labs(mrn)

def tool_simrs_update_patient_record(
    mrn: str, 
    doctor_notes: str, 
    primary_diagnosis: str, 
    treatment_plan: str
) -> Dict[str, Any]:
    """Updates/commits CPPT progress note transaction directly into SIMRS EMR system via MCP."""
    return simrs_mcp_client.update_patient_record(mrn, doctor_notes, primary_diagnosis, treatment_plan)
