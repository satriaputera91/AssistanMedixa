import unittest
from app.modules.rag.rag_service import qdrant_rag_service
from app.modules.medical_agent.tools.rag_tools import tool_vector_rag_search
from app.modules.medical_agent.skills.pharmacology import node_km_medication_recommendation


class TestMedicalKnowledgeRAG(unittest.TestCase):
    """Test suite for expanded Knowledge Management and Qdrant RAG search."""

    def test_01_knowledge_base_count_and_categories(self):
        """Verify that knowledge items include all diseases and medications from pharmacology lines 17-103."""
        items = qdrant_rag_service.list_knowledge_items()
        self.assertGreaterEqual(items["total_items"], 20)
        
        doc_ids = [d["id"] for d in items["items"]]
        # Diseases
        self.assertIn("kb-dis-001", doc_ids) # T2DM
        self.assertIn("kb-dis-002", doc_ids) # CKD
        self.assertIn("kb-dis-003", doc_ids) # HTN
        self.assertIn("kb-dis-004", doc_ids) # ACS
        self.assertIn("kb-dis-005", doc_ids) # Gastritis Kronis Erosif & Dispepsia
        self.assertIn("kb-dis-006", doc_ids) # Anemia Defisiensi Besi
        self.assertIn("kb-dis-007", doc_ids) # Chronic Coronary Syndrome (CAD Post-PCI)

        # Medications
        self.assertIn("kb-med-001", doc_ids) # Metformin
        self.assertIn("kb-med-002", doc_ids) # Lisinopril
        self.assertIn("kb-med-003", doc_ids) # Clopidogrel
        self.assertIn("kb-med-004", doc_ids) # Omeprazole
        self.assertIn("kb-med-005", doc_ids) # Sukralfat
        self.assertIn("kb-med-006", doc_ids) # Ferrous Fumarate / Sulfas Ferosus
        self.assertIn("kb-med-007", doc_ids) # Bisoprolol & Metoprolol
        self.assertIn("kb-med-008", doc_ids) # Rosuvastatin & Atorvastatin
        self.assertIn("kb-med-009", doc_ids) # ISDN
        self.assertIn("kb-med-010", doc_ids) # Empagliflozin
        self.assertIn("kb-med-011", doc_ids) # Amlodipine

    def test_02_rag_search_gastritis_and_anemia_meds(self):
        """Test RAG search for Gastritis & Anemia returns Omeprazole, Sukralfat, and Iron."""
        results = tool_vector_rag_search("Gastritis Erosif ulu hati perih lambung mual omeprazole sukralfat ferrous", top_k=3)
        self.assertGreater(len(results), 0)
        titles = [r["title"] for r in results]
        found = any("Omeprazole" in t or "Sukralfat" in t or "Gastritis" in t or "Ferrous" in t for t in titles)
        self.assertTrue(found, f"Expected Gastritis/PPI/Sucralfate/Iron in top results, got: {titles}")

    def test_03_rag_search_cad_post_pci_meds(self):
        """Test RAG search for CAD Post-PCI returns Clopidogrel, Bisoprolol, Statin, and ISDN."""
        results = tool_vector_rag_search("CAD Post-PCI nyeri dada angina clopidogrel bisoprolol statin isdn", top_k=3)
        self.assertGreater(len(results), 0)
        titles = [r["title"] for r in results]
        found = any("Clopidogrel" in t or "Bisoprolol" in t or "Statin" in t or "ISDN" in t or "Coronary" in t for t in titles)
        self.assertTrue(found, f"Expected CAD/Beta-blocker/Statin/ISDN in top results, got: {titles}")

    def test_04_rag_search_t2dm_ckd_meds(self):
        """Test RAG search for T2DM & CKD returns Metformin, Lisinopril, Empagliflozin, SGLT2i."""
        results = tool_vector_rag_search("Diabetes CKD renal dosing metformin lisinopril empagliflozin", top_k=3)
        self.assertGreater(len(results), 0)
        titles = [r["title"] for r in results]
        found = any("Metformin" in t or "Lisinopril" in t or "Empagliflozin" in t or "Kidney" in t or "Diabetes" in t for t in titles)
        self.assertTrue(found, f"Expected T2DM/CKD/Metformin/Lisinopril in top results, got: {titles}")

    def test_05_pharmacology_node_executes_rag_dynamically(self):
        """Test node_km_medication_recommendation dynamically populates RAG evidence chunks."""
        state = {
            "patient_id": "P-30124",
            "user_query": "5. Rekomendasi Terapi Obat Pasien Ini",
            "simrs_anamnesis": {
                "chief_complaint": "Nyeri ulu hati hebat, perih setelah makan, dan lemas",
                "history_present_illness": "Gastritis kronis kambuh sejak 1 minggu"
            },
            "steps_executed": [],
            "ehr_data": {}
        }
        res_state = node_km_medication_recommendation(state)
        med_rec = res_state.get("medication_recommendations", {})
        
        self.assertEqual(med_rec.get("disease"), "Gastritis Kronis Erosif & Anemia Defisiensi Besi")
        self.assertIn("rag_guideline_evidence", med_rec)
        self.assertGreater(len(med_rec["rag_guideline_evidence"]), 0)
        
        # Check that state.rag_chunks is populated
        self.assertIn("rag_chunks", res_state)
        self.assertGreater(len(res_state["rag_chunks"]), 0)

    def test_06_disease_explanation_node_gastritis_anemia_rag(self):
        """Test node_km_disease_explanations retrieves and parses Gastritis & Anemia from Qdrant Vector DB."""
        from app.modules.medical_agent.skills.disease_explanation import node_km_disease_explanations
        state = {
            "patient_id": "P-30124",
            "user_query": "7. Penjelasan Patofisiologi Penyakit Pasien",
            "simrs_anamnesis": {
                "chief_complaint": "Nyeri ulu hati perih hebat dan mual",
                "history_present_illness": "Gastritis erosif kronis dan anemia defisiensi besi"
            },
            "steps_executed": [],
            "ehr_data": {}
        }
        res_state = node_km_disease_explanations(state)
        exp = res_state.get("disease_explanations", {})
        
        self.assertIsNotNone(exp)
        self.assertIn("Gastritis", exp.get("disease_name", ""))
        self.assertGreater(len(exp.get("disease_overview", "")), 20)
        self.assertGreater(len(exp.get("diagnostic_criteria", [])), 0)
        self.assertGreater(len(exp.get("clinical_staging", "")), 0)
        self.assertGreater(len(exp.get("key_complications", [])), 0)
        self.assertIn("rag_score", exp)

    def test_07_disease_explanation_node_cad_post_pci_rag(self):
        """Test node_km_disease_explanations retrieves and parses CAD Post-PCI LAD from Qdrant Vector DB."""
        from app.modules.medical_agent.skills.disease_explanation import node_km_disease_explanations
        state = {
            "patient_id": "P-20811",
            "user_query": "7. Penjelasan Patofisiologi Penyakit Pasien",
            "simrs_anamnesis": {
                "chief_complaint": "Nyeri dada seperti tertimpa beban saat naik tangga",
                "history_present_illness": "Penyakit jantung koroner riwayat pemasangan stent LAD (CAD Post-PCI)"
            },
            "steps_executed": [],
            "ehr_data": {}
        }
        res_state = node_km_disease_explanations(state)
        exp = res_state.get("disease_explanations", {})
        
        self.assertIsNotNone(exp)
        self.assertTrue("Coronary" in exp.get("disease_name", "") or "CAD" in exp.get("disease_name", ""))
        self.assertGreater(len(exp.get("disease_overview", "")), 20)
        self.assertGreater(len(exp.get("diagnostic_criteria", [])), 0)
        self.assertGreater(len(exp.get("key_complications", [])), 0)

    def test_08_disease_explanation_node_t2dm_ckd_rag(self):
        """Test node_km_disease_explanations retrieves and parses T2DM & CKD with Neuropathy from Qdrant Vector DB."""
        from app.modules.medical_agent.skills.disease_explanation import node_km_disease_explanations
        state = {
            "patient_id": "P-10492",
            "user_query": "7. Penjelasan Patofisiologi Penyakit Pasien",
            "simrs_anamnesis": {
                "chief_complaint": "Kontrol rutin diabetes melitus tipe 2 dan hipertensi",
                "history_present_illness": "DM Tipe 2 dengan komplikasi CKD stage 3a dan neuropati diabetik perifer"
            },
            "steps_executed": [],
            "ehr_data": {}
        }
        res_state = node_km_disease_explanations(state)
        exp = res_state.get("disease_explanations", {})
        
        self.assertIsNotNone(exp)
        self.assertTrue("Diabetes" in exp.get("disease_name", "") or "CKD" in exp.get("disease_name", "") or "T2DM" in exp.get("disease_name", ""))
        self.assertGreater(len(exp.get("disease_overview", "")), 20)
        self.assertGreater(len(exp.get("diagnostic_criteria", [])), 0)

    def test_09_disease_explanation_empty_when_no_rag_query(self):
        """Test node_km_disease_explanations leaves disease_explanations as None when no query/clinical data is present."""
        from app.modules.medical_agent.skills.disease_explanation import node_km_disease_explanations
        state = {
            "patient_id": "P-UNKNOWN",
            "user_query": "",
            "simrs_anamnesis": {},
            "diagnostic_recommendations": {},
            "steps_executed": [],
            "ehr_data": {}
        }
        res_state = node_km_disease_explanations(state)
        exp = res_state.get("disease_explanations")
        self.assertIsNone(exp, f"Expected disease_explanations to be None/empty, got: {exp}")

    def test_10_diagnostic_recommendations_gastritis_rag(self):
        """Test tool_generate_diagnostic_recommendations dynamically retrieves Gastritis & Anemia from Qdrant RAG."""
        from app.modules.medical_agent.tools.clinical_tools import tool_generate_diagnostic_recommendations
        res = tool_generate_diagnostic_recommendations(
            anamnesis={
                "chief_complaint": "Nyeri ulu hati perih terbakar dan mual pasca makan",
                "history_present_illness": "Gastritis kronis erosif dan pusing lemas anemia defisiensi besi"
            },
            ehr_data={},
            chronic_conditions=["Gastritis Kronis"]
        )
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["primary_recommendations"]), 0)
        self.assertGreater(len(res["differential_diagnoses"]), 0)
        self.assertGreater(len(res["recommended_workups"]), 0)
        self.assertIn("K29.1", res["icd10_coding"])

    def test_11_diagnostic_recommendations_cad_post_pci_rag(self):
        """Test tool_generate_diagnostic_recommendations dynamically retrieves CAD Post-PCI from Qdrant RAG."""
        from app.modules.medical_agent.tools.clinical_tools import tool_generate_diagnostic_recommendations
        res = tool_generate_diagnostic_recommendations(
            anamnesis={
                "chief_complaint": "Nyeri dada dan rasa tidak nyaman saat menaiki tangga",
                "history_present_illness": "Angina pektoris stabil riwayat CAD post-PCI LAD stent DES"
            },
            ehr_data={},
            chronic_conditions=["CAD Post-PCI LAD"]
        )
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["primary_recommendations"]), 0)
        self.assertGreater(len(res["differential_diagnoses"]), 0)
        self.assertIn("I20.8", res["icd10_coding"])

    def test_12_diagnostic_recommendations_t2dm_ckd_rag(self):
        """Test tool_generate_diagnostic_recommendations dynamically retrieves T2DM & CKD from Qdrant RAG."""
        from app.modules.medical_agent.tools.clinical_tools import tool_generate_diagnostic_recommendations
        res = tool_generate_diagnostic_recommendations(
            anamnesis={
                "chief_complaint": "Kontrol rutin diabetes melitus tipe 2 dan hipertensi",
                "history_present_illness": "DM Tipe 2, CKD stage 3a, neuropati diabetik kesemutan ujung kaki"
            },
            ehr_data={},
            chronic_conditions=["Type 2 Diabetes Mellitus", "Hypertension", "CKD Stage 3a"]
        )
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["primary_recommendations"]), 0)
        self.assertIn("E11.22", res["icd10_coding"])

    def test_13_diagnostic_recommendations_empty_when_no_data(self):
        """Test tool_generate_diagnostic_recommendations returns empty lists when no query/clinical data is present."""
        from app.modules.medical_agent.tools.clinical_tools import tool_generate_diagnostic_recommendations
        res = tool_generate_diagnostic_recommendations(
            anamnesis={},
            ehr_data={},
            chronic_conditions=[]
        )
        self.assertEqual(res["status"], "info")
        self.assertEqual(len(res["primary_recommendations"]), 0)
        self.assertEqual(len(res["differential_diagnoses"]), 0)

    def test_14_med_generation_gastritis_rag(self):
        """Test tool_generate_med_generation dynamically retrieves Gastritis & Anemia regimens from Qdrant RAG."""
        from app.modules.medical_agent.tools.clinical_tools import tool_generate_med_generation
        res = tool_generate_med_generation(
            anamnesis={
                "chief_complaint": "Nyeri ulu hati perih melilit dan badan lemas pucat",
                "history_present_illness": "Gastritis kronis erosif, dispepsia perih ulu hati, anemia defisiensi besi"
            },
            diagnostic_recommendations={
                "primary_recommendations": [{"diagnosis": "Gastritis Kronis Erosif & Anemia Defisiensi Besi"}]
            }
        )
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["recommended_regimens"]), 0)
        drug_names = [r["drug_name"] for r in res["recommended_regimens"]]
        self.assertTrue(any("Omeprazole" in d for d in drug_names))
        self.assertTrue(any("Sukralfat" in d or "Ferrous" in d for d in drug_names))
        self.assertGreater(len(res["contraindicated_drugs"]), 0)
        self.assertGreater(len(res["monitoring_points"]), 0)

    def test_15_med_generation_cad_rag(self):
        """Test tool_generate_med_generation dynamically retrieves CAD Post-PCI regimens from Qdrant RAG."""
        from app.modules.medical_agent.tools.clinical_tools import tool_generate_med_generation
        res = tool_generate_med_generation(
            anamnesis={
                "chief_complaint": "Rasa tidak nyaman dada kiri saat naik tangga 2 lantai",
                "history_present_illness": "Riwayat PCI LAD DES 1 tahun lalu, riwayat angina pektoris stabil"
            },
            diagnostic_recommendations={
                "primary_recommendations": [{"diagnosis": "Chronic Coronary Syndrome (CAD Post-PCI LAD)"}]
            }
        )
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["recommended_regimens"]), 0)
        drug_names = [r["drug_name"] for r in res["recommended_regimens"]]
        self.assertTrue(any("Clopidogrel" in d for d in drug_names))
        self.assertTrue(any("Bisoprolol" in d or "Metoprolol" in d for d in drug_names))

    def test_16_med_generation_t2dm_ckd_rag(self):
        """Test tool_generate_med_generation dynamically retrieves T2DM & CKD regimens from Qdrant RAG."""
        from app.modules.medical_agent.tools.clinical_tools import tool_generate_med_generation
        res = tool_generate_med_generation(
            anamnesis={
                "chief_complaint": "Kontrol diabetes melitus tipe 2 dan hipertensi",
                "history_present_illness": "Diabetes Melitus Tipe 2 dengan CKD Stage 3a"
            },
            diagnostic_recommendations={
                "primary_recommendations": [{"diagnosis": "Type 2 Diabetes Mellitus with CKD Stage 3a"}]
            }
        )
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["recommended_regimens"]), 0)
        drug_names = [r["drug_name"] for r in res["recommended_regimens"]]
        self.assertTrue(any("Metformin" in d for d in drug_names))
        self.assertTrue(any("Lisinopril" in d for d in drug_names))

    def test_17_med_generation_empty_when_no_data(self):
        """Test tool_generate_med_generation returns empty results when no clinical context is present."""
        from app.modules.medical_agent.tools.clinical_tools import tool_generate_med_generation
        res = tool_generate_med_generation()
        self.assertEqual(res["status"], "info")
        self.assertIsNone(res["disease"])
        self.assertEqual(len(res["recommended_regimens"]), 0)

    def test_18_red_flags_gastritis_rag(self):
        """Test tool_detect_clinical_red_flags dynamically retrieves Gastritis & Anemia red flags from Qdrant RAG."""
        from app.modules.medical_agent.tools.clinical_tools import tool_detect_clinical_red_flags
        res = tool_detect_clinical_red_flags(
            anamnesis={
                "chief_complaint": "Nyeri ulu hati perih melilit dan badan lemas pucat",
                "history_present_illness": "Gastritis kronis erosif, dispepsia perih ulu hati, anemia defisiensi besi"
            },
            diagnostic_recommendations={
                "primary_recommendations": [{"diagnosis": "Gastritis Kronis Erosif & Anemia Defisiensi Besi"}]
            }
        )
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["detected_red_flags"]), 0)
        alerts = [f["alert"] for f in res["detected_red_flags"]]
        self.assertTrue(any("Perdarahan Saluran Cerna" in a or "Hematemesis" in a for a in alerts))
        self.assertTrue(any(f["severity"] in ["Critical", "High"] for f in res["detected_red_flags"]))

    def test_19_red_flags_cad_rag(self):
        """Test tool_detect_clinical_red_flags dynamically retrieves CAD Post-PCI red flags from Qdrant RAG."""
        from app.modules.medical_agent.tools.clinical_tools import tool_detect_clinical_red_flags
        res = tool_detect_clinical_red_flags(
            anamnesis={
                "chief_complaint": "Rasa tidak nyaman di dada saat beraktivitas",
                "history_present_illness": "Riwayat PCI DES LAD, Angina pektoris stabil CCS II"
            },
            diagnostic_recommendations={
                "primary_recommendations": [{"diagnosis": "Chronic Coronary Syndrome (CAD Post-PCI LAD)"}]
            }
        )
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["detected_red_flags"]), 0)
        alerts = [f["alert"] for f in res["detected_red_flags"]]
        self.assertTrue(any("Sindrom Koroner Akut" in a or "Syok Kardiogenik" in a for a in alerts))
        self.assertTrue(any(f["severity"] == "Critical" for f in res["detected_red_flags"]))

    def test_20_red_flags_t2dm_ckd_rag(self):
        """Test tool_detect_clinical_red_flags dynamically retrieves T2DM & CKD red flags from Qdrant RAG."""
        from app.modules.medical_agent.tools.clinical_tools import tool_detect_clinical_red_flags
        res = tool_detect_clinical_red_flags(
            anamnesis={
                "chief_complaint": "Kontrol rutin diabetes melitus dan hipertensi",
                "history_present_illness": "Diabetes melitus tipe 2 dengan CKD Stage 3a dan hipertensi primer"
            },
            diagnostic_recommendations={
                "primary_recommendations": [{"diagnosis": "Type 2 Diabetes Mellitus with CKD Stage 3a & Diabetic Neuropathy"}]
            }
        )
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["detected_red_flags"]), 0)
        alerts = [f["alert"] for f in res["detected_red_flags"]]
        self.assertTrue(any("Krisis Hipertensi" in a or "AKI on CKD" in a or "Hipoglikemia" in a for a in alerts))

    def test_21_red_flags_empty_when_no_data(self):
        """Test tool_detect_clinical_red_flags returns empty results when no clinical context is provided."""
        from app.modules.medical_agent.tools.clinical_tools import tool_detect_clinical_red_flags
        res = tool_detect_clinical_red_flags()
        self.assertEqual(res["status"], "info")
        self.assertIsNone(res["disease"])
        self.assertEqual(len(res["detected_red_flags"]), 0)


if __name__ == "__main__":
    unittest.main()

