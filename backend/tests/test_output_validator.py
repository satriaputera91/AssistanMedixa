import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.modules.guardrails.output_validator import LLMOutputValidator
from app.modules.medical_agent import medical_agent_graph



def test_grounding_valid_demographics():
    simrs_profile = {
        "mrn": "MRN-SIMRS-10492",
        "full_name": "Eleanor Vance",
        "gender": "Female",
        "age": 58
    }
    simrs_labs = {
        "vital_signs": {
            "blood_pressure": "140/90 mmHg",
            "heart_rate": "82 bpm"
        }
    }
    output_text = (
        "Pasien Ny. Eleanor Vance (MRN-SIMRS-10492) diperiksa dengan TD 140/90 mmHg. "
        "Hasil evaluasi menunjukkan hipertensi stage 1."
    )
    result = LLMOutputValidator.validate_grounding(
        output_text,
        simrs_profile=simrs_profile,
        simrs_labs=simrs_labs
    )
    assert result["status"] == "PASSED"
    assert result["grounding_score"] == 1.0
    assert len(result["anomalies"]) == 0


def test_grounding_anomalies_mismatched_mrn_and_gender():
    simrs_profile = {
        "mrn": "MRN-SIMRS-10492",
        "full_name": "Eleanor Vance",
        "gender": "Female",
        "age": 58
    }
    output_text = (
        "Pasien Tn. Eleanor Vance dengan nomor rekam medis MRN-SIMRS-99999 datang dengan keluhan pusing."
    )
    result = LLMOutputValidator.validate_grounding(
        output_text,
        simrs_profile=simrs_profile
    )
    assert result["grounding_score"] < 1.0
    assert len(result["anomalies"]) >= 2
    assert any("MRN-SIMRS-99999" in a for a in result["anomalies"])
    assert any("gender" in a.lower() for a in result["anomalies"])


def test_allergy_contraindication_penicillin():
    simrs_anamnesis = {
        "allergy_history": "Riwayat alergi antibiotik golongan penisilin (ruam dan gatal)"
    }
    # Output proposing amoxicillin to a penicillin allergic patient
    output_text = (
        "### Plan\n"
        "1. Berikan terapi Amoxicillin 500mg 3x sehari selama 5 hari.\n"
        "2. Paracetamol 500mg jika demam."
    )
    result = LLMOutputValidator.validate_allergy_contraindications(
        output_text,
        simrs_anamnesis=simrs_anamnesis
    )
    assert result["allergy_safe"] is False
    assert len(result["contraindication_alerts"]) > 0
    assert any("KONTRAINDIKASI ALERGI" in alert for alert in result["contraindication_alerts"])


def test_allergy_safe_patient():
    simrs_anamnesis = {
        "allergy_history": "Tidak ada riwayat alergi obat atau makanan"
    }
    output_text = (
        "### Plan\n"
        "1. Berikan terapi Amoxicillin 500mg 3x sehari.\n"
        "2. Paracetamol 500mg jika demam."
    )
    result = LLMOutputValidator.validate_allergy_contraindications(
        output_text,
        simrs_anamnesis=simrs_anamnesis
    )
    assert result["allergy_safe"] is True
    assert len(result["contraindication_alerts"]) == 0


def test_red_flag_coverage_omission():
    red_flag_detections = {
        "detected_red_flags": [
            {"title": "Krisis Hipertensi Emergensi dengan Gejala Serebral", "severity": "Critical"}
        ]
    }
    # Output that does not mention any warning or red flag precautions
    output_text = "Pasien disarankan istirahat cukup dan minum air putih."
    result = LLMOutputValidator.validate_red_flag_coverage(
        output_text,
        red_flag_detections=red_flag_detections
    )
    assert result["red_flag_covered"] is False
    assert len(result["missing_red_flags"]) > 0


def test_disclaimer_auto_remediation():
    config = {"auto_disclaimer_enforced": True}
    output_without_disclaimer = (
        "### Assessment\n"
        "Pasien didiagnosis menderita Gastritis Akut [K29.0].\n"
        "### Plan\n"
        "Diberikan Omeprazole 20mg 1x1 sebelum makan pagi selama 14 hari."
    )
    result = LLMOutputValidator.validate_formatting_and_disclaimer(
        output_without_disclaimer,
        config=config
    )
    assert result["remediation_applied"] is True
    assert "Clinical Disclaimer" in result["remediated_text"]


def test_evaluate_all_comprehensive():
    simrs_profile = {
        "mrn": "MRN-SIMRS-10492",
        "full_name": "Eleanor Vance",
        "gender": "Female",
        "age": 58
    }
    simrs_anamnesis = {
        "allergy_history": "Penisilin"
    }
    # Unsafe output: prescribing Ampicillin to penicillin allergic patient, without disclaimer
    unsafe_output = (
        "Pasien Ny. Eleanor Vance (MRN-SIMRS-10492) diberikan Ampisilin 500mg 3x1."
    )
    evaluation = LLMOutputValidator.evaluate_all(
        output_text=unsafe_output,
        simrs_profile=simrs_profile,
        simrs_anamnesis=simrs_anamnesis,
        config={"safety_level": "Strict", "auto_disclaimer_enforced": True, "enabled": True}
    )
    assert evaluation["status"] == "REJECTED"
    assert evaluation["is_valid"] is False
    assert len(evaluation["alerts"]) > 0


def test_pydantic_soap_schema_to_markdown():
    from app.modules.medical_agent import (
        ClinicalSOAPOutputSchema, SubjectiveData, ObjectiveData, VitalSignsData,
        LabItemData, AssessmentData, DiagnosisItemData, PlanData, MedicationItemData,
        RedFlagData, PatientDemographicsData
    )
    soap = ClinicalSOAPOutputSchema(
        patient=PatientDemographicsData(mrn="MRN-SIMRS-10492", full_name="Eleanor Vance", age=58, gender="Female"),
        subjective=SubjectiveData(chief_complaint="Nyeri ulu hati", allergy_history="Penisilin"),
        objective=ObjectiveData(
            vital_signs=VitalSignsData(blood_pressure="130/80 mmHg", heart_rate="78 bpm"),
            laboratory_results=[LabItemData(test_name="HbA1c", value="6.5", unit="%")]
        ),
        assessment=AssessmentData(
            primary_diagnosis=DiagnosisItemData(diagnosis="Dispepsia Fungsional", icd10="K30"),
            differential_diagnoses=[DiagnosisItemData(diagnosis="Gastritis Akut", icd10="K29.0")]
        ),
        plan=PlanData(
            medications=[MedicationItemData(drug_name="Omeprazole", dosage="20mg", frequency="2x1", notes="Sebelum makan")],
            patient_education=["Hindari makanan pedas dan asam"]
        ),
        red_flags=[RedFlagData(title="Hematemesis / Melena", severity="Critical", action_required="Segera ke IGD")]
    )
    md = soap.to_markdown()
    assert "Dispepsia Fungsional" in md
    assert "K30" in md
    assert "130/80 mmHg" in md
    assert "Omeprazole" in md
    assert "Clinical Disclaimer" in md
    d = soap.model_dump()
    assert d["output_type"] == "clinical_soap"
    assert d["subjective"]["chief_complaint"] == "Nyeri ulu hati"


def test_pydantic_general_knowledge_schema_to_markdown():
    from app.modules.medical_agent import (
        GeneralConsultationKnowledgeSchema, MedicationItemData, RedFlagData
    )
    knowledge = GeneralConsultationKnowledgeSchema(
        title="Panduan Terapi Diabetes Melitus Tipe 2",
        summary="Ringkasan pedoman tatalaksana DM Tipe 2 berbasis bukti.",
        key_points=["Target HbA1c < 7.0%", "Modifikasi gaya hidup dan metformin sebagai lini pertama."],
        treatment_recommendations=[
            MedicationItemData(drug_name="Metformin", dosage="500 mg", frequency="2x sehari", notes="Dosis titrasi")
        ],
        red_flags=[RedFlagData(title="Gejala Hipoglikemia Akut", severity="Critical", action_required="Pemberian glukosa cepat")]
    )
    md = knowledge.to_markdown()
    assert "Diabetes Melitus Tipe 2" in md
    assert "Metformin" in md
    assert "Hipoglikemia" in md
    assert "Clinical Disclaimer" in md


def test_structured_allergy_contraindication_validation():
    from app.modules.guardrails.output_validator import LLMOutputValidator
    structured_plan = {
        "plan": {
            "medications": [
                {"drug_name": "Amoxicillin 500mg", "dosage": "500mg", "frequency": "3x1"}
            ]
        }
    }
    res = LLMOutputValidator.validate_allergy_contraindications(
        output_text="Pasien diberikan obat antibiotik.",
        simrs_anamnesis={"allergy_history": "Riwayat alergi penisilin"},
        structured_output=structured_plan
    )
    assert res["allergy_safe"] is False
    assert any("Structured Plan" in a for a in res["contraindication_alerts"])


def test_langgraph_agent_output_validation_integration():
    """Verify that LangGraph executes validate_output node and populates output_validation in final state."""
    initial_state = {
        "messages": [{"role": "user", "content": "Halo apa saja layanan yang tersedia?"}],
        "patient_id": None,
        "user_query": "Halo apa saja layanan yang tersedia?",
        "workflow_type": "text",
        "steps_executed": [],
        "ehr_data": None,
        "drug_interaction_findings": None,
        "literature_summary": None,
        "final_synthesis": "",
    }
    config = {"configurable": {"thread_id": "test-val-session-1"}}
    final_state = medical_agent_graph.invoke(initial_state, config=config)
    
    assert "output_validation" in final_state
    assert final_state["output_validation"] is not None
    assert "validation_score" in final_state["output_validation"]
    assert "verdict" in final_state["output_validation"]
    
    # Check that the validate_output step was recorded
    step_names = [s["step_name"] for s in final_state["steps_executed"]]
    assert any("Validasi Output LLM" in name for name in step_names)


if __name__ == "__main__":
    tests = [
        ("Demographics & Vitals Grounding", test_grounding_valid_demographics),
        ("Grounding Anomalies & Discrepancies", test_grounding_anomalies_mismatched_mrn_and_gender),
        ("Allergy Contraindication (Penicillin)", test_allergy_contraindication_penicillin),
        ("Allergy Safe Verification", test_allergy_safe_patient),
        ("Red Flag Omission Detection", test_red_flag_coverage_omission),
        ("Clinical Disclaimer Auto-Remediation", test_disclaimer_auto_remediation),
        ("Comprehensive Output Evaluation", test_evaluate_all_comprehensive),
        ("Pydantic SOAP Schema Validation & Markdown Render", test_pydantic_soap_schema_to_markdown),
        ("Pydantic General Knowledge Schema Validation & Markdown Render", test_pydantic_general_knowledge_schema_to_markdown),
        ("Structured Field-Level Allergy Validation", test_structured_allergy_contraindication_validation),
        ("LangGraph Agent Graph Output Validation Integration", test_langgraph_agent_output_validation_integration),
    ]

    print("=" * 70)
    print("RUNNING LLM OUTPUT VALIDATION & PYDANTIC SCHEMA TEST SUITE")
    print("=" * 70)
    passed = 0
    for name, test_fn in tests:
        try:
            test_fn()
            print(f"  ✅ PASS: {name}")
            passed += 1
        except AssertionError as e:
            print(f"  ❌ FAIL: {name} -> {e}")
        except Exception as e:
            print(f"  💥 ERROR: {name} -> {e}")

    print("=" * 70)
    print(f"RESULT: {passed}/{len(tests)} tests passed successfully.")
    print("=" * 70)
    if passed != len(tests):
        sys.exit(1)


