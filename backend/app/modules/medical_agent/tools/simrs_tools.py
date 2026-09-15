from typing import Dict, Any, List, Optional
from app.modules.mcp.simrs_client import simrs_mcp_client
from app.modules.medical_agent.mcp_function_calling import (
    MCPGeminiFunctionAdapter,
    gemini_mcp_service,
    GeminiMCPService,
)


# ── Dynamic Tool Discovery & Generative AI Function Calling ─────────────────

def get_active_mcp_tools() -> List[Dict[str, Any]]:
    """Returns list of currently active and enabled MCP tools."""
    return simrs_mcp_client.get_available_mcp_tools()


def get_gemini_mcp_function_declarations() -> List[Dict[str, Any]]:
    """Generates Generative AI FunctionDeclarations schema from all active MCP tools."""
    return MCPGeminiFunctionAdapter.get_gemini_function_declarations()


def execute_mcp_tool_dynamically(tool_name: str, **kwargs) -> Dict[str, Any]:
    """Dynamically executes any registered MCP tool by name."""
    return simrs_mcp_client.execute_tool(tool_name, kwargs)


def execute_gemini_function_call(function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatches a Generative AI function call directly to the corresponding MCP Tool."""
    return MCPGeminiFunctionAdapter.execute_gemini_function_call(function_name, arguments)


def run_gemini_with_mcp_tools(
    prompt: str,
    system_instruction: Optional[str] = None,
    patient_id: Optional[str] = None
) -> Dict[str, Any]:
    """Runs a full Generative AI LLM query loop with dynamic MCP Function Calling."""
    return gemini_mcp_service.run_query_with_mcp_function_calling(
        prompt=prompt,
        system_instruction=system_instruction,
        patient_id=patient_id
    )


# ── Single Dynamic Patient Data Retrieval Tool ───────────────────────

def tool_simrs_get_patient(
    mrn: str, 
    data_type: str = "profile"
) -> Dict[str, Any]:
    """Single unified dynamic tool to fetch any category of SIMRS patient data via MCP.
    
    Args:
        mrn: SIMRS Medical Record Number (e.g. 'MRN-SIMRS-10492' or 'P-10492').
        data_type: Category of patient data to retrieve:
            - 'profile' / 'demographics': Demographics, NIK, BPJS status.
            - 'history' / 'medical_history': Past admissions & chronic conditions.
            - 'anamnesis': Clinical complaint, RPS, RPD, RPK, allergies.
            - 'labs' / 'laboratory': Latest laboratory panels and vital signs.
            - 'all' / 'full': Comprehensive combined patient record.
    """
    category = (data_type or "profile").strip().lower()
    
    if category in ("profile", "demographics"):
        return simrs_mcp_client.execute_tool("simrs.get_patient_profile", {"mrn": mrn})
    elif category in ("history", "medical_history", "admissions"):
        return simrs_mcp_client.execute_tool("simrs.get_patient_history", {"mrn": mrn})
    elif category in ("anamnesis", "complaint", "symptoms"):
        return simrs_mcp_client.execute_tool("simrs.get_patient_anamnesis", {"mrn": mrn})
    elif category in ("labs", "laboratory", "vitals"):
        return simrs_mcp_client.execute_tool("simrs.get_patient_labs", {"mrn": mrn})
    elif category in ("all", "full", "comprehensive"):
        return {
            "status": "success",
            "mrn": mrn,
            "profile": simrs_mcp_client.execute_tool("simrs.get_patient_profile", {"mrn": mrn}),
            "history": simrs_mcp_client.execute_tool("simrs.get_patient_history", {"mrn": mrn}),
            "anamnesis": simrs_mcp_client.execute_tool("simrs.get_patient_anamnesis", {"mrn": mrn}),
            "labs": simrs_mcp_client.execute_tool("simrs.get_patient_labs", {"mrn": mrn}),
        }
    else:
        # Fallback to dynamic tool name resolution
        tool_name = category if "." in category else f"simrs.get_patient_{category}"
        return simrs_mcp_client.execute_tool(tool_name, {"mrn": mrn})


# Backward compatibility aliases
tool_simrs_get_patient_data = tool_simrs_get_patient
tool_simrs_get_patient_profile = lambda mrn: tool_simrs_get_patient(mrn, data_type="profile")
tool_simrs_get_patient_history = lambda mrn: tool_simrs_get_patient(mrn, data_type="history")
tool_simrs_get_patient_anamnesis = lambda mrn: tool_simrs_get_patient(mrn, data_type="anamnesis")
tool_simrs_get_patient_labs = lambda mrn: tool_simrs_get_patient(mrn, data_type="labs")


def tool_simrs_update_patient_record(
    mrn: str, 
    doctor_notes: str, 
    primary_diagnosis: str, 
    treatment_plan: str
) -> Dict[str, Any]:
    """Updates/commits CPPT progress note transaction directly into SIMRS EMR system via MCP."""
    return simrs_mcp_client.update_patient_record(mrn, doctor_notes, primary_diagnosis, treatment_plan)

