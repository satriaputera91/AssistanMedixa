"""
Comprehensive End-to-End Test Suite for Medical Agent Scenarios & Modular Architecture.
Tests all clinical skills, tools, context schemas, memory checkpointer, and LangGraph workflow nodes.
"""

import os
import sys
import unittest
from typing import Dict, Any

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.modules.medical_agent.agent.graph import medical_agent_graph, build_medical_agent_graph
from app.modules.medical_agent.context.state import MedicalAgentState
from app.modules.medical_agent.context.schemas import (
    AgentChatRequest,
    AgentChatResponse,
    AgentStepSchema,
    OutputValidationSchema,
    SOAContentSchema,
    SOANoteSchema
)
from app.modules.medical_agent.memory.checkpointer import get_sqlite_checkpointer
from app.modules.medical_agent.skills.output_schemas import (
    ClinicalSOAPOutputSchema,
    GeneralConsultationKnowledgeSchema,
    SIMRSTransactionReportSchema,
    OutputValidator
)
from app.modules.medical_agent.tools.simrs_tools import (
    tool_simrs_get_patient_profile,
    tool_simrs_get_patient_history,
    tool_simrs_get_patient_anamnesis,
    tool_simrs_get_patient_labs,
    tool_simrs_update_patient_record
)
from app.modules.medical_agent.tools.clinical_tools import tool_query_patient_ehr


class TestMedicalAgentScenarios(unittest.TestCase):
    """End-to-end integration and scenario tests for the modular Medical Agent."""

    def test_01_general_knowledge_consultation_scenario(self):
        """Scenario 1: Doctor asks for KDIGO / ADA clinical guidelines without patient selected."""
        state: MedicalAgentState = {
            "messages": [{"role": "user", "content": "Jelaskan pedoman diagnosis dan staging CKD menurut KDIGO 2024"}],
            "patient_id": None,
            "user_query": "Jelaskan pedoman diagnosis dan staging CKD menurut KDIGO 2024",
            "workflow_type": "text",
            "steps_executed": [],
            "final_synthesis": ""
        }
        config = {"configurable": {"thread_id": "scenario-01-general-knowledge"}}
        res = medical_agent_graph.invoke(state, config=config)

        self.assertIn("final_synthesis", res)
        self.assertTrue(len(res["final_synthesis"]) > 100)
        self.assertIsNotNone(res.get("output_validation"))
        self.assertTrue(res["output_validation"]["is_valid"])
        
        # Verify planner routed to general consultation
        step_names = [s["step_name"] for s in res["steps_executed"]]
        self.assertTrue(any("Planner" in name or "Conversation" in name for name in step_names))

    def test_02_patient_history_and_demographics_scenario(self):
        """Scenario 2: FAQ 1 - Retrieve patient demographics, chronic history, admissions, and labs from SIMRS."""
        state: MedicalAgentState = {
            "messages": [{"role": "user", "content": "Ambil data profil demografi, riwayat penyakit kronis, rawat inap pasien dan hasil laboratorium"}],
            "patient_id": "P-10492",
            "user_query": "Ambil data profil demografi, riwayat penyakit kronis, rawat inap pasien dan hasil laboratorium",
            "workflow_type": "text",
            "steps_executed": [],
            "final_synthesis": ""
        }
        config = {"configurable": {"thread_id": "scenario-02-patient-history"}}
        res = medical_agent_graph.invoke(state, config=config)

        self.assertIsNotNone(res.get("simrs_profile"))
        self.assertEqual(res["simrs_profile"]["mrn"], "MRN-SIMRS-10492")
        self.assertIn("Eleanor Vance", res["simrs_profile"]["full_name"])
        self.assertIsNotNone(res.get("simrs_history"))
        self.assertTrue(len(res["simrs_history"]["chronic_conditions"]) > 0)
        self.assertTrue(any(k in res["final_synthesis"] for k in ["Eleanor Vance", "MRN-SIMRS-10492", "Profil", "Riwayat", "Informasi Riwayat"]))

    def test_03_patient_anamnesis_retrieval_scenario(self):
        """Scenario 3: FAQ 2 - Retrieve patient clinical anamnesis (Keluhan Utama, RPS, RPD, RPK)."""
        state: MedicalAgentState = {
            "messages": [{"role": "user", "content": "Ambil data anamnesis klinis pasien, keluhan utama, dan RPS"}],
            "patient_id": "P-30124",
            "user_query": "Ambil data anamnesis klinis pasien, keluhan utama, dan RPS",
            "workflow_type": "text",
            "steps_executed": [],
            "final_synthesis": ""
        }
        config = {"configurable": {"thread_id": "scenario-03-anamnesis"}}
        res = medical_agent_graph.invoke(state, config=config)

        self.assertIsNotNone(res.get("simrs_anamnesis"))
        self.assertIn("chief_complaint", res["simrs_anamnesis"])
        self.assertIn("ulu hati", res["simrs_anamnesis"]["chief_complaint"].lower())
        self.assertTrue(any("2. Ambil Data Anamnesis SIMRS" in s["step_name"] for s in res["steps_executed"]))

    def test_04_patient_labs_and_vitals_evaluation_scenario(self):
        """Scenario 4: FAQ 3 - Evaluate serial laboratory values and vital signs via SIMRS MCP."""
        state: MedicalAgentState = {
            "messages": [{"role": "user", "content": "Evaluasi hasil lab serial, eGFR, dan tanda vital pasien"}],
            "patient_id": "P-10492",
            "user_query": "Evaluasi hasil lab serial, eGFR, dan tanda vital pasien",
            "workflow_type": "text",
            "steps_executed": [],
            "final_synthesis": ""
        }
        config = {"configurable": {"thread_id": "scenario-04-labs"}}
        res = medical_agent_graph.invoke(state, config=config)

        self.assertIsNotNone(res.get("simrs_lab_evaluations"))
        self.assertIn("vital_signs", res["simrs_lab_evaluations"])
        self.assertIn("latest_labs", res["simrs_lab_evaluations"])
        self.assertTrue(any("3. Evaluasi Hasil Lab" in s["step_name"] for s in res["steps_executed"]))

    def test_05_diagnostic_icd10_recommendations_scenario(self):
        """Scenario 5: FAQ 4 - Diagnostic recommendations with ICD-10 codification."""
        state: MedicalAgentState = {
            "messages": [{"role": "user", "content": "Berikan rekomendasi diagnosis kerja dan kode ICD-10 untuk pasien"}],
            "patient_id": "P-30124",
            "user_query": "Berikan rekomendasi diagnosis kerja dan kode ICD-10 untuk pasien",
            "workflow_type": "text",
            "steps_executed": [],
            "final_synthesis": ""
        }
        config = {"configurable": {"thread_id": "scenario-05-diagnosis"}}
        res = medical_agent_graph.invoke(state, config=config)

        self.assertIsNotNone(res.get("diagnostic_recommendations"))
        diag = res["diagnostic_recommendations"]
        self.assertTrue(len(diag["primary_recommendations"]) > 0)
        self.assertTrue(len(diag["icd10_coding"]) > 0)
        self.assertIn("K29.1", diag["icd10_coding"])

    def test_06_pharmacology_and_renal_dosing_scenario(self):
        """Scenario 6: FAQ 5 - Evidence-based drug therapy regimens with renal clearance dosing."""
        state: MedicalAgentState = {
            "messages": [{"role": "user", "content": "Rekomendasi terapi obat lini pertama dan penyesuaian dosis ginjal"}],
            "patient_id": "P-10492",
            "user_query": "Rekomendasi terapi obat lini pertama dan penyesuaian dosis ginjal",
            "workflow_type": "text",
            "steps_executed": [],
            "final_synthesis": ""
        }
        config = {"configurable": {"thread_id": "scenario-06-pharmacology"}}
        res = medical_agent_graph.invoke(state, config=config)

        self.assertIsNotNone(res.get("medication_recommendations"))
        meds = res["medication_recommendations"]
        self.assertTrue(len(meds["recommended_regimens"]) > 0)
        # Verify renal dosing guidance is present
        self.assertTrue(any("renal_dosing" in m for m in meds["recommended_regimens"]))

    def test_07_disease_pathophysiology_scenario(self):
        """Scenario 7: FAQ 7 - Disease overview, pathophysiology, and staging criteria."""
        state: MedicalAgentState = {
            "messages": [{"role": "user", "content": "Jelaskan patofisiologi dan stadium klinis penyakit pasien ini"}],
            "patient_id": "P-20811",
            "user_query": "Jelaskan patofisiologi dan stadium klinis penyakit pasien ini",
            "workflow_type": "text",
            "steps_executed": [],
            "final_synthesis": ""
        }
        config = {"configurable": {"thread_id": "scenario-07-pathophysiology"}}
        res = medical_agent_graph.invoke(state, config=config)

        self.assertIsNotNone(res.get("disease_explanations"))
        exp = res["disease_explanations"]
        self.assertIn("disease_name", exp)
        self.assertIn("diagnostic_criteria", exp)
        self.assertIn("key_complications", exp)

    def test_08_red_flag_emergency_detection_scenario(self):
        """Scenario 8: FAQ 8 - Clinical red flag alerts and triage thresholds."""
        state: MedicalAgentState = {
            "messages": [{"role": "user", "content": "Deteksi tanda bahaya klinis dan kriteria kegawatdaruratan pasien"}],
            "patient_id": "P-30124",
            "user_query": "Deteksi tanda bahaya klinis dan kriteria kegawatdaruratan pasien",
            "workflow_type": "text",
            "steps_executed": [],
            "final_synthesis": ""
        }
        config = {"configurable": {"thread_id": "scenario-08-red-flags"}}
        res = medical_agent_graph.invoke(state, config=config)

        self.assertIsNotNone(res.get("red_flag_detections"))
        rf = res["red_flag_detections"]
        self.assertTrue(len(rf["detected_red_flags"]) > 0)
        self.assertTrue(any(f["severity"] in ["Critical", "High"] for f in rf["detected_red_flags"]))

    def test_09_drug_safety_and_allergy_screening_scenario(self):
        """Scenario 9: FAQ 9 - Drug-Drug Interaction (DDI) and allergy safety screening."""
        state: MedicalAgentState = {
            "messages": [{"role": "user", "content": "Skrining interaksi obat dan keamanan alergi pasien"}],
            "patient_id": "P-10492",
            "user_query": "Skrining interaksi obat dan keamanan alergi pasien",
            "workflow_type": "text",
            "steps_executed": [],
            "final_synthesis": ""
        }
        config = {"configurable": {"thread_id": "scenario-09-ddi"}}
        res = medical_agent_graph.invoke(state, config=config)

        self.assertIsNotNone(res.get("drug_safety_screening"))
        safety = res["drug_safety_screening"]
        self.assertIn("overall_safety_status", safety)
        self.assertIn("ddi_screening", safety)

    def test_10_cppt_commit_simrs_transaction_scenario(self):
        """Scenario 10: FAQ 10 - Generate CPPT S/O/A/P and commit directly into SIMRS via MCP."""
        state: MedicalAgentState = {
            "messages": [{"role": "user", "content": "Buat dan kirim CPPT S/O/A/P pasien ini ke SIMRS RME"}],
            "patient_id": "P-10492",
            "user_query": "Buat dan kirim CPPT S/O/A/P pasien ini ke SIMRS RME",
            "workflow_type": "text",
            "steps_executed": [],
            "final_synthesis": ""
        }
        config = {"configurable": {"thread_id": "scenario-10-cppt-commit"}}
        res = medical_agent_graph.invoke(state, config=config)

        self.assertIsNotNone(res.get("simrs_update_res"))
        self.assertEqual(res["simrs_update_res"]["status"], "success")
        self.assertIn("log_id", res["simrs_update_res"])
        self.assertTrue(any(k in res["final_synthesis"] for k in ["CPPT", "Catatan Perkembangan", "S (Subjective)", "SIMRS", "Pengiriman"]))

    def test_11_audio_stt_and_soap_synthesis_scenario(self):
        """Scenario 11: Audio consultation recording transcription and automated SOAP synthesis."""
        state: MedicalAgentState = {
            "messages": [],
            "patient_id": "P-10492",
            "user_query": "Proses rekaman audio konsultasi pasien",
            "workflow_type": "audio",
            "audio_bytes": b"MOCK_WAV_HEADER_AND_AUDIO_PCM_DATA",
            "audio_filename": "konsultasi_ibu_eleanor.wav",
            "steps_executed": [],
            "final_synthesis": ""
        }
        config = {"configurable": {"thread_id": "scenario-11-audio-soap"}}
        res = medical_agent_graph.invoke(state, config=config)

        self.assertIsNotNone(res.get("audio_transcript"))
        self.assertTrue(len(res["audio_transcript"]) > 50)
        self.assertIn("Transkrip Percakapan", res["final_synthesis"])
        self.assertIn("Catatan S/O/A/P Terstruktur", res["final_synthesis"])
        self.assertTrue(any("Transkripsi Audio" in s["step_name"] for s in res["steps_executed"]))


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMedicalAgentScenarios)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
