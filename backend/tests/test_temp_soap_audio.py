"""
Unit & Integration Test Suite for Temporary SOAP Records & Audio Recording Storage (Pre-SIMRS Workflow).
Tests creation of temp SOAP from audio consultation, relational linkage to chat sessions, audio streaming,
DPJP editing, and final transaction commit to SIMRS EMR via MCP.
"""

import os
import sys
import unittest
from datetime import datetime

# Ensure backend root is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.database import dbApplication, InMemoryDatabase
from app.modules.medical_agent.context.schemas import (
    TempSOAPContentSchema,
    TempSOAPRecordSchema,
    TempSOAPUpdateRequest,
    TempSOAPCommitResponse
)
from app.modules.medical_agent.tools.simrs_tools import tool_simrs_update_patient_record


class TestTempSOAPAudioStorage(unittest.TestCase):
    """Test suite for temporary SOAP database operations and chat session relations."""

    def setUp(self):
        self.db = dbApplication
        # Prepare a mock session
        self.test_session_id = f"test-sess-{int(datetime.now().timestamp() * 1000)}"
        self.db.chat_sessions[self.test_session_id] = {
            "session_id": self.test_session_id,
            "user_id": "u1",
            "title": "Konsultasi Audio Pasien Demo",
            "created_at": datetime.now().isoformat(),
            "patient_id": "P-10492",
            "temp_soap_id": None,
            "messages": []
        }

    def test_01_create_temp_soap_and_relate_to_chat_session(self):
        """Test creating a temporary SOAP record and ensuring bilateral relation with chat session."""
        soap_content = {
            "subjective": "Pasien mengeluh pusing berputar dan nokturia 3x per malam.",
            "objective": "TD: 140/90 mmHg, Nadi: 78 bpm, GDP: 142 mg/dL, HbA1c: 7.2%",
            "assessment": "Diabetes Mellitus Tipe 2 dengan Hipertensi Esensial Stage 1",
            "plan": "Metformin 1000mg BID, Lisinopril 20mg Daily, Diet Rendah Garam",
            "instructions": "Kontrol serial 1 bulan dan monitor berkala gula darah puasa."
        }

        temp_rec = self.db.create_temp_soap(
            session_id=self.test_session_id,
            patient_id="P-10492",
            user_id="u1",
            doctor_name="Dr. Sarah Jenkins, MD",
            audio_filename="konsultasi_audio_pasien.wav",
            audio_url=f"/api/v1/agent/soap-temp/audio-file/mock_recording.wav",
            audio_path="/tmp/mock_recording.wav",
            audio_size_bytes=48000,
            audio_transcript="Dokter: Selamat pagi... Pasien: Pagi dok...",
            soap_content=soap_content,
            raw_markdown="## 📋 Resume CPPT S-O-A-P...",
            structured_output={"confidence": 0.95},
            patient_name="Eleanor Vance",
            mrn="MRN-SIMRS-10492",
            nik="3201015508600002"
        )

        self.assertIsNotNone(temp_rec)
        self.assertTrue(temp_rec["temp_id"].startswith("temp-soap-"))
        self.assertEqual(temp_rec["session_id"], self.test_session_id)
        self.assertEqual(temp_rec["status"], "draft")
        self.assertEqual(temp_rec["simrs_sync_status"], "pending")

        # Verify chat session relation
        session_rec = self.db.chat_sessions.get(self.test_session_id)
        self.assertIsNotNone(session_rec)
        self.assertEqual(session_rec.get("temp_soap_id"), temp_rec["temp_id"])

        # Query by session
        fetched_by_sess = self.db.get_temp_soap_by_session(self.test_session_id)
        self.assertIsNotNone(fetched_by_sess)
        self.assertEqual(fetched_by_sess["temp_id"], temp_rec["temp_id"])

    def test_02_update_temp_soap_content_by_doctor(self):
        """Test DPJP editing the temporary SOAP record content before SIMRS submission."""
        # Create initial record
        temp_rec = self.db.create_temp_soap(
            session_id=self.test_session_id,
            patient_id="P-10492",
            user_id="u1",
            doctor_name="Dr. Sarah Jenkins, MD",
            audio_filename="consult.wav",
            audio_url="/api/v1/agent/soap-temp/audio-file/consult.wav",
            audio_path="/tmp/consult.wav",
            audio_size_bytes=32000,
            audio_transcript="Percakapan klinis...",
            soap_content={
                "subjective": "Keluhan awal",
                "objective": "TD 120/80",
                "assessment": "Diagnosis awal",
                "plan": "Terapi awal"
            },
            raw_markdown="Resume awal"
        )
        temp_id = temp_rec["temp_id"]

        # Doctor updates assessment and plan
        updated_content = {
            "subjective": "Keluhan awal terevisi",
            "objective": "TD 130/85 mmHg",
            "assessment": "DM Tipe 2 Terkontrol + CKD 3a Stabil",
            "plan": "Metformin 500mg BID + Edukasi Nutrisi",
            "instructions": "Periksa eGFR 3 bulan lagi"
        }
        updated = self.db.update_temp_soap(temp_id, {
            "soap_content": updated_content,
            "status": "ready_for_simrs"
        })

        self.assertIsNotNone(updated)
        self.assertEqual(updated["status"], "ready_for_simrs")
        self.assertEqual(updated["soap_content"]["assessment"], "DM Tipe 2 Terkontrol + CKD 3a Stabil")

    def test_03_commit_temp_soap_to_simrs_mcp(self):
        """Test committing temporary SOAP data to SIMRS EMR via MCP tool and updating sync status."""
        temp_rec = self.db.create_temp_soap(
            session_id=self.test_session_id,
            patient_id="P-10492",
            user_id="u1",
            doctor_name="Dr. Sarah Jenkins, MD",
            audio_filename="eleanor_vance_checkup.wav",
            audio_url="/api/v1/agent/soap-temp/audio-file/eleanor.wav",
            audio_path="/tmp/eleanor.wav",
            audio_size_bytes=64000,
            audio_transcript="Konsultasi nefrologi...",
            soap_content={
                "subjective": "Pusing berkurang setelah terapi rutin.",
                "objective": "eGFR 58 mL/min, Serum Creatinine 1.3 mg/dL",
                "assessment": "CKD Stage 3a (N18.31) & DM Tipe 2",
                "plan": "Lisinopril 20mg Daily",
                "instructions": "Kontrol 3 bulan"
            },
            raw_markdown="## CPPT...",
            patient_name="Eleanor Vance",
            mrn="MRN-SIMRS-10492"
        )
        temp_id = temp_rec["temp_id"]

        # Call MCP update
        simrs_res = tool_simrs_update_patient_record(
            mrn="MRN-SIMRS-10492",
            doctor_notes=f"S: {temp_rec['soap_content']['subjective']}\nO: {temp_rec['soap_content']['objective']}",
            primary_diagnosis=temp_rec['soap_content']['assessment'],
            treatment_plan=f"P: {temp_rec['soap_content']['plan']}\nI: {temp_rec['soap_content']['instructions']}"
        )

        self.assertEqual(simrs_res.get("status"), "success")
        self.assertIn("log_id", simrs_res)

        # Mark synced in DB
        synced_rec = self.db.mark_temp_soap_synced(temp_id, simrs_res)
        self.assertIsNotNone(synced_rec)
        self.assertEqual(synced_rec["status"], "synced_to_simrs")
        self.assertEqual(synced_rec["simrs_sync_status"], "synced")
        self.assertEqual(synced_rec["simrs_log_id"], simrs_res["log_id"])
        self.assertIsNotNone(synced_rec["synced_at"])

    def test_04_delete_temp_soap_and_unlink_session(self):
        """Test deleting a temporary SOAP and verifying session link uncoupling."""
        temp_rec = self.db.create_temp_soap(
            session_id=self.test_session_id,
            patient_id="P-10492",
            user_id="u1",
            doctor_name="Dr. Sarah Jenkins, MD",
            audio_filename="temp_delete.wav",
            audio_url="/api/v1/agent/soap-temp/audio-file/temp_delete.wav",
            audio_path="/tmp/temp_delete.wav",
            audio_size_bytes=1000,
            audio_transcript="Temp transcript",
            soap_content={"subjective": "-", "objective": "-", "assessment": "-", "plan": "-"},
            raw_markdown="-"
        )
        temp_id = temp_rec["temp_id"]

        self.assertEqual(self.db.chat_sessions[self.test_session_id].get("temp_soap_id"), temp_id)

        # Delete
        success = self.db.delete_temp_soap(temp_id)
        self.assertTrue(success)
        self.assertIsNone(self.db.get_temp_soap(temp_id))
        self.assertIsNone(self.db.chat_sessions[self.test_session_id].get("temp_soap_id"))

    def test_05_extract_soap_plan_and_instructions_reliably(self):
        """Test that Plan and Instructions are properly extracted from structured_output and markdown."""
        from app.modules.medical_agent.router import _extract_soap_from_state, _soap_section

        # 1. Test markdown parsing with typical synthesis output
        sample_markdown = (
            "## 📋 Resume CPPT\n\n"
            "### 📝 S — Subjective (Anamnesis)\n- Keluhan Utama: Nyeri dada kiri menjalar\n\n"
            "### 🔬 O — Objective (Pemeriksaan Fisik & Penunjang)\n- Tanda Vital: TD 150/95 mmHg, HR 92 bpm\n\n"
            "### 🎯 A — Assessment (Diagnosis Kerja & Banding)\n- Diagnosis Utama: Angina Pectoris Stabil [ICD-10: I20.9]\n\n"
            "### 💊 P — Plan (Penatalaksanaan & Terapi)\n"
            "**Rekomendasi Terapi Farmakologi:**\n"
            "| Obat / Zat Aktif | Dosis | Frekuensi |\n"
            "| ISDN | 5 mg | Sublingual bila nyeri |\n"
            "| Bisoprolol | 5 mg | 1x sehari |\n\n"
            "**Rencana Pemeriksaan Penunjang Lanjutan:**\n- EKG 12 Lead Serial\n- Profil Lipid Lengkap\n\n"
            "**Edukasi Pasien & Modifikasi Gaya Hidup:**\n- Batasi konsumsi garam dan lemak jenuh\n- Segera ke IGD jika nyeri dada > 20 menit\n\n"
            "---\n*(⚠️ **Clinical Disclaimer**: Sistem pendukung keputusan klinis AI...)*"
        )

        plan_extracted = _soap_section(sample_markdown, "Plan")
        self.assertNotEqual(plan_extracted, "Tidak disebutkan.")
        self.assertIn("ISDN", plan_extracted)
        self.assertIn("Bisoprolol", plan_extracted)
        self.assertIn("EKG 12 Lead Serial", plan_extracted)

        # 2. Test _extract_soap_from_state with structured_output
        state_with_struct = {
            "final_synthesis": sample_markdown,
            "structured_output": {
                "soap": {
                    "subjective": {"chief_complaint": "Nyeri dada kiri"},
                    "objective": {"vital_signs": {"blood_pressure": "150/95 mmHg"}},
                    "assessment": {
                        "primary_diagnosis": {"diagnosis": "Angina Pectoris", "icd10": "I20.9", "confidence": 0.9}
                    },
                    "plan": {
                        "medications": [{"drug_name": "ISDN", "dosage": "5 mg", "frequency": "Sublingual"}],
                        "diagnostic_workup": ["EKG 12 Lead", "Troponin I"],
                        "patient_education": ["Hindari aktivitas fisik berat mendadak"],
                        "follow_up": "Kontrol Poli Jantung 1 minggu"
                    },
                    "red_flags": [{"title": "Nyeri dada menetap >20 menit", "severity": "Critical", "action_required": "Segera ke IGD"}]
                }
            }
        }

        extracted = _extract_soap_from_state(state_with_struct)
        self.assertIn("ISDN", extracted["plan"])
        self.assertIn("EKG 12 Lead", extracted["plan"])
        self.assertIn("Poli Jantung", extracted["plan"])
        self.assertIn("Hindari aktivitas", extracted["instructions"])
        self.assertIn("Segera ke IGD", extracted["instructions"])

    def test_06_cppt_intent_uses_temp_soap_data(self):
        """Test that CPPT commit and synthesis logic directly uses Temp SOAP data when available."""
        from app.modules.medical_agent.agent.graph import node_execute_tools
        from app.modules.medical_agent.agent.synthesis import _generate_fallback_synthesis

        # Create a temp soap in database
        temp_soap = self.db.create_temp_soap(
            session_id=self.test_session_id,
            patient_id="P-10492",
            user_id="u1",
            doctor_name="Dr. Sarah Jenkins",
            audio_filename="consultation_temp.wav",
            audio_url="/api/v1/agent/soap-temp/audio-file/consultation_temp.wav",
            audio_path="/tmp/consultation_temp.wav",
            audio_size_bytes=50000,
            audio_transcript="Keluhan batuk berdahak 4 hari...",
            soap_content={
                "subjective": "Batuk berdahak kuning kehijauan dan demam 38.2°C",
                "objective": "TD 120/80 mmHg, Ronkhi basah halus pada basal paru kanan",
                "assessment": "Pneumonia Komunitas (CAP) Ringan [ICD-10: J18.9]",
                "plan": "Azithromycin 500mg OD selama 3 hari, Paracetamol 500mg PRN",
                "instructions": "Edukasi hidrasi cukup >2L/hari, kontrol jika sesak memberat"
            },
            raw_markdown="## Resume..."
        )

        state = {
            "user_query": "Buat draft CPPT S/O/A/P dan kirim ke SIMRS",
            "patient_id": "P-10492",
            "session_id": self.test_session_id,
            "steps_executed": [],
            "simrs_profile": {"mrn": "MRN-SIMRS-10492", "full_name": "Eleanor Vance"},
            "simrs_anamnesis": {},
            "simrs_labs": {},
            "diagnostic_recommendations": {},
            "medication_recommendations": {}
        }

        # Run node_execute_tools
        res_state = node_execute_tools(state)
        steps = res_state.get("steps_executed", [])
        cppt_steps = [s for s in steps if "Sinkronisasi & Commit CPPT ke SIMRS" in s["step_name"]]
        self.assertTrue(len(cppt_steps) > 0)
        self.assertIn("SOAP Temp", cppt_steps[0]["description"])

        # Check that temp soap was marked synced
        synced_soap = self.db.get_temp_soap(temp_soap["temp_id"])
        self.assertEqual(synced_soap["status"], "synced_to_simrs")

    def test_07_diagnosis_medication_procedure_enriched_with_temp_soap(self):
        """Test that FAQ 4 (Diagnosis), FAQ 5 (Medication), and FAQ 6 (Procedure) are enriched with Temp SOAP analysis."""
        from app.modules.medical_agent.skills.anamnesis import node_fetch_patient_history
        from app.modules.medical_agent.skills.diagnostics import node_diagnostic_recommendation
        from app.modules.medical_agent.skills.pharmacology import node_km_medication_recommendation
        from app.modules.medical_agent.agent.synthesis import _generate_fallback_synthesis

        # 1. Create a temp SOAP record
        temp_soap = self.db.create_temp_soap(
            session_id=self.test_session_id,
            patient_id="P-90112",
            user_id="u1",
            doctor_name="Dr. Sarah Jenkins",
            audio_filename="konsultasi_bambang.mp3",
            audio_url="/api/v1/agent/soap-temp/audio-file/konsultasi_bambang.mp3",
            audio_path="/tmp/konsultasi_bambang.mp3",
            audio_size_bytes=45000,
            audio_transcript="Pasien mengeluh sesak dan batuk berdahak kuning...",
            soap_content={
                "subjective": "Batuk berdahak kuning kehijauan disertai demam dan sesak napas",
                "objective": "TD 130/85 mmHg, HR 96 bpm, Ronkhi basah kasar lapangan paru kanan",
                "assessment": "Pneumonia Komunitas (CAP) [ICD-10: J18.9]",
                "plan": "Azithromycin 500mg PO 1x1 (3 hari), N-Acetylcysteine 200mg 3x1, Paracetamol 500mg PRN",
                "instructions": "Edukasi hidrasi >2L per hari, istirahat tirah baring, kontrol IGD bila sesak memberat"
            },
            raw_markdown="## Resume..."
        )

        # 2. Test node_fetch_patient_history retrieves temp_soap_data
        state = {
            "patient_id": "P-90112",
            "session_id": self.test_session_id,
            "steps_executed": [],
            "user_query": "4. Rekomendasi Diagnosis & ICD-10 Pasien"
        }
        res_history = node_fetch_patient_history(state)
        self.assertIsNotNone(res_history.get("temp_soap_data"))
        self.assertEqual(res_history["temp_soap_data"]["temp_id"], temp_soap["temp_id"])

        # 3. Test node_diagnostic_recommendation executes successfully
        res_diag = node_diagnostic_recommendation(res_history)
        diag_rec = res_diag.get("diagnostic_recommendations", {})
        self.assertIn("primary_recommendations", diag_rec)

        # 4. Test node_km_medication_recommendation incorporates temp_soap_data
        res_med = node_km_medication_recommendation(res_history)
        med_rec = res_med.get("medication_recommendations", {})
        self.assertIn("temp_soap_regimens", med_rec)
        self.assertIn("Azithromycin", med_rec["temp_soap_regimens"]["terapi_soap_temp"])

        # 5. Test fallback synthesis for Diagnosis query
        diag_text, _ = _generate_fallback_synthesis(
            query="4. Rekomendasi Diagnosis & ICD-10 Pasien",
            ehr_data={},
            simrs_profile={"mrn": "MRN-SIMRS-90112", "full_name": "Bambang Sudarsono"},
            simrs_history={},
            simrs_anamnesis={"chief_complaint": "Batuk dan demam"},
            simrs_labs={},
            diagnostic_rec=diag_rec,
            disease_exp={},
            red_flags={},
            med_rec=med_rec,
            drug_safety={},
            simrs_update_res={},
            drug_findings=[],
            lit_summary="",
            rag_chunks=[]
        )
        self.assertIn("Rekomendasi Diagnosis", diag_text)

        # 6. Test fallback synthesis for Medication query
        med_text, _ = _generate_fallback_synthesis(
            query="5. Rekomendasi Terapi Obat Pasien Ini",
            ehr_data={},
            simrs_profile={"mrn": "MRN-SIMRS-90112", "full_name": "Bambang Sudarsono"},
            simrs_history={},
            simrs_anamnesis={},
            simrs_labs={},
            diagnostic_rec=diag_rec,
            disease_exp={},
            red_flags={},
            med_rec=med_rec,
            drug_safety={},
            simrs_update_res={},
            drug_findings=[],
            lit_summary="",
            rag_chunks=[]
        )
        self.assertIn("Rekomendasi Terapi Obat", med_text)
        self.assertIn("Analisis Kesesuaian Terapi Obat dari SOAP Temp", med_text)
        self.assertIn("Azithromycin", med_text)

        # 7. Test fallback synthesis for Procedure query
        proc_text, _ = _generate_fallback_synthesis(
            query="6. Rekomendasi Tindakan & Prosedur Medis",
            ehr_data={},
            simrs_profile={"mrn": "MRN-SIMRS-90112", "full_name": "Bambang Sudarsono"},
            simrs_history={},
            simrs_anamnesis={},
            simrs_labs={},
            diagnostic_rec=diag_rec,
            disease_exp={},
            red_flags={},
            med_rec=med_rec,
            drug_safety={},
            simrs_update_res={},
            drug_findings=[],
            lit_summary="",
            rag_chunks=[]
        )
        self.assertIn("Rekomendasi Tindakan", proc_text)
        self.assertIn("Rencana Tindakan & Edukasi dari SOAP Temp", proc_text)


if __name__ == "__main__":
    unittest.main()
