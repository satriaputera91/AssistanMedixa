"""
Backward-compatibility forwarder for state.
"""
from app.modules.medical_agent.context.state import MedicalAgentState, AgentStepInfo

__all__ = [
    "MedicalAgentState",
    "AgentStepInfo"
]
