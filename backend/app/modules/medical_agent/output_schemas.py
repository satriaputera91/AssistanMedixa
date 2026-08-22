"""
Backward-compatibility forwarder for output_schemas.
"""
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
    AudioConsultationSOAPSchema,
    OutputValidationReport,
    OutputValidator,
    MANDATORY_CLINICAL_DISCLAIMER
)

__all__ = [
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
    "AudioConsultationSOAPSchema",
    "OutputValidationReport",
    "OutputValidator",
    "MANDATORY_CLINICAL_DISCLAIMER"
]
