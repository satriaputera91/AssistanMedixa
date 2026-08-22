from typing import TypedDict, List, Dict, Any, Optional

class AgentStepInfo(TypedDict):
    step_name: str
    description: str
    status: str
    result: Optional[Any]

class MedicalAgentState(TypedDict, total=False):
    messages: List[Dict[str, str]]
    patient_id: Optional[str]
    user_query: str
    steps_executed: List[AgentStepInfo]
    ehr_data: Optional[Dict[str, Any]]
    simrs_profile: Optional[Dict[str, Any]]
    simrs_history: Optional[Dict[str, Any]]
    simrs_anamnesis: Optional[Dict[str, Any]]
    diagnostic_recommendations: Optional[Dict[str, Any]]
    simrs_lab_evaluations: Optional[Dict[str, Any]]
    medication_recommendations: Optional[Dict[str, Any]]
    disease_explanations: Optional[Dict[str, Any]]
    red_flag_detections: Optional[Dict[str, Any]]
    drug_safety_screening: Optional[Dict[str, Any]]
    simrs_update_res: Optional[Dict[str, Any]]
    drug_interaction_findings: Optional[List[str]]
    literature_summary: Optional[str]
    rag_chunks: Optional[List[Dict[str, Any]]]
    final_synthesis: str
    workflow_type: Optional[str]
    detected_intent: Optional[str]
    audio_bytes: Optional[bytes]
    audio_filename: Optional[str]
    audio_mime_type: Optional[str]
    audio_transcript: Optional[str]
    audio_error: Optional[str]
    output_validation: Optional[Dict[str, Any]]
    structured_output: Optional[Dict[str, Any]]
