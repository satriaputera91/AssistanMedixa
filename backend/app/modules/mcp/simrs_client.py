from typing import Dict, Any, List
from app.modules.mcp.simrs_server import simrs_mcp_server

class SIMRSMCPClientBridge:
    """Bridge connecting external callers or LangGraph agent tools to SIMRS MCP Server."""
    
    def __init__(self):
        self.server = simrs_mcp_server

    def get_available_mcp_tools(self) -> List[Dict[str, Any]]:
        """Queries MCP Server for registered tools."""
        return self.server.list_tools()

    def get_patient_profile(self, mrn: str) -> Dict[str, Any]:
        """Calls MCP tool 'simrs.get_patient_profile'."""
        return self.server.call_tool("simrs.get_patient_profile", {"mrn": mrn})

    def get_patient_history(self, mrn: str) -> Dict[str, Any]:
        """Calls MCP tool 'simrs.get_patient_history'."""
        return self.server.call_tool("simrs.get_patient_history", {"mrn": mrn})

    def get_patient_anamnesis(self, mrn: str) -> Dict[str, Any]:
        """Calls MCP tool 'simrs.get_patient_anamnesis'."""
        return self.server.call_tool("simrs.get_patient_anamnesis", {"mrn": mrn})

    def get_patient_labs(self, mrn: str) -> Dict[str, Any]:
        """Calls MCP tool 'simrs.get_patient_labs'."""
        return self.server.call_tool("simrs.get_patient_labs", {"mrn": mrn})

    def update_patient_record(
        self, 
        mrn: str, 
        doctor_notes: str, 
        primary_diagnosis: str, 
        treatment_plan: str
    ) -> Dict[str, Any]:
        """Calls MCP tool 'simrs.update_patient_record'."""
        return self.server.call_tool(
            "simrs.update_patient_record", 
            {
                "mrn": mrn,
                "doctor_notes": doctor_notes,
                "primary_diagnosis": primary_diagnosis,
                "treatment_plan": treatment_plan
            }
        )

simrs_mcp_client = SIMRSMCPClientBridge()
