import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import dbApplication

class TestHITLMissingClinicalData(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        login_res = self.client.post(
            "/api/v1/auth/login",
            json={"email": "doctor@AssistantMedixa.com", "password": "doctor123"}
        )
        self.assertEqual(login_res.status_code, 200, f"Login failed: {login_res.text}")
        self.token = login_res.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_01_hitl_missing_clinical_data_trigger(self):
        """Test asking for diagnosis when subjective and objective data are missing triggers HITL."""
        # Create a new session with no prior SOAP data
        session_id = f"test-hitl-session-{int(datetime_now())}"
        
        res = self.client.post(
            "/api/v1/agent/chat",
            json={
                "user_query": "Berikan rekomendasi diagnosis dan ICD-10 untuk pasien ini",
                "patient_id": "P-EMPTY-PATIENT",
                "session_id": session_id
            },
            headers=self.headers
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        # Verify HITL flags and options
        self.assertTrue(data.get("hitl_required"), "Should require Human-in-The-Loop")
        self.assertIn("Mohon maaf", data.get("final_synthesis", ""))
        self.assertIsNotNone(data.get("hitl_data"))
        
        hitl_data = data["hitl_data"]
        self.assertEqual(hitl_data.get("type"), "missing_subjective_objective")
        self.assertEqual(len(hitl_data.get("options", [])), 3)
        option_keys = [o["key"] for o in hitl_data["options"]]
        self.assertIn("audio_record", option_keys)
        self.assertIn("file_upload", option_keys)
        self.assertIn("manual_input", option_keys)

    def test_02_create_manual_temp_soap_and_subsequent_query(self):
        """Test saving manual multi-step SOAP to temp SOAP database and querying diagnosis afterward."""
        session_id = f"test-manual-soap-{int(datetime_now())}"
        patient_id = "P-10492"

        # 1. Create Manual SOAP Temp
        create_res = self.client.post(
            "/api/v1/agent/soap-temp",
            json={
                "session_id": session_id,
                "patient_id": patient_id,
                "soap_content": {
                    "subjective": "Pasien mengeluh nyeri ulu hati perih terbakar sejak 4 hari, mual (+).",
                    "objective": "TD 120/80 mmHg, Nadi 80 x/mnt, Nyeri tekan epigastrium (+), Lab Hb 13.5.",
                    "assessment": "Dispepsia Fungsional dd Gastritis Akut",
                    "plan": "Omeprazole 20mg 2x1 a.c., Antasida 3x1 C.",
                    "instructions": "Hindari makanan pedas dan asam, makan teratur."
                },
                "raw_markdown": "### Catatan SOAP Manual Terstruktur"
            },
            headers=self.headers
        )
        self.assertEqual(create_res.status_code, 200)
        soap_rec = create_res.json()
        self.assertTrue(soap_rec["temp_id"].startswith("temp-soap-"))
        self.assertEqual(soap_rec["soap_content"]["assessment"], "Dispepsia Fungsional dd Gastritis Akut")

        # 2. Verify it is queryable in list_temp_soap
        get_res = self.client.get(f"/api/v1/agent/soap-temp/{soap_rec['temp_id']}", headers=self.headers)
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["session_id"], session_id)


def datetime_now():
    import time
    return time.time()

if __name__ == "__main__":
    unittest.main()
