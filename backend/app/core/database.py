from datetime import datetime
from typing import Dict, List, Optional
from app.modules.mcp.simrs_server import simrs_repo

# Mock In-Memory Database Store for modular monolith
class InMemoryDatabase:
    def __init__(self):
        # Data Tenaga Medis / Dokter & Staff dimuat langsung dari Master Data SIMRS
        self.users: Dict[str, dict] = simrs_repo.get_all_users()
        
        # Data Rekam Medis Elektronik (EHR) Pasien terintegrasi dan dimuat langsung dari SIMRS
        self.patient_records: Dict[str, dict] = simrs_repo.get_all_patient_records()


        # Chat Sessions & History
        self.chat_sessions: Dict[str, dict] = {
            "session-demo-1": {
                "session_id": "session-demo-1",
                "user_id": "u1",
                "title": "Patient Eleanor Vance - Medication Review & eGFR Assessment",
                "created_at": datetime.now().isoformat(),
                "patient_id": "P-10492",
                "messages": [
                    {
                        "role": "user",
                        "content": "Please review Eleanor Vance's eGFR labs and check for potential Lisinopril contraindications given her CKD status.",
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "role": "assistant",
                        "content": "Based on Eleanor Vance's EHR (Patient ID: P-10492), her current eGFR is 58 mL/min/1.73m² (Stage 3a CKD) with Serum Creatinine at 1.3 mg/dL and Potassium at 4.6 mEq/L.\n\n### Clinical Assessment & Guidance:\n1. **ACE Inhibitor Monitoring**: Lisinopril 20mg Daily is appropriate for renal protection in early CKD and diabetic nephropathy. However, routine monitoring of serum potassium (currently 4.6 mEq/L) and renal function is mandatory.\n2. **Allergy Notice**: Patient has documented severe allergies to Penicillin and Sulfa Drugs; Lisinopril shows no cross-reactivity.\n3. **Recommendation**: Re-check BMP (basic metabolic panel) in 3 months.",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
        }

        # Structured S/O/A notes generated from audio. Revisions are only accepted
        # after the doctor explicitly confirms the proposed changes.
        self.soap_notes: Dict[str, dict] = {}

        # Audit & LLM Usage Logs
        self.audit_logs: List[dict] = [
            {
                "id": "log-1",
                "timestamp": datetime.now().isoformat(),
                "user_id": "u1",
                "doctor_name": "Dr. Sarah Jenkins, MD",
                "action": "EHR Lookup & Agent Invocation",
                "details": "Queried EHR P-10492 for eGFR & ACEi interaction",
                "tokens_used": 640,
                "status": "Success"
            }
        ]

        # AI Safety & Guardrails Module Configuration
        self.guardrail_config: dict = {
            "enabled": True,
            "pii_redaction_enabled": True,
            "strictly_medical_scope": True,
            "hallucination_prevention": True,
            "toxic_content_filter": True,
            "auto_disclaimer_enforced": True,
            "min_confidence_score": 0.85,
            "max_query_length": 1500,
            "banned_keywords": [
                "resep palsu", "surat sakit palsu", "narkotika ilegal", 
                "hack", "bypass", "exploit", "kartu kredit", "kata sandi"
            ],
            "allowed_domains": [
                "Farmakologi", "Kardiologi", "Nefrologi", "Endokrinologi", 
                "Pediatri", "Onkologi", "Bedah", "Interoperabilitas SIMRS", "Penunjang Lab"
            ],
            "safety_level": "Strict",
            "updated_at": datetime.now().isoformat()
        }

        # Guardrail Violations & Audit Logs
        self.guardrail_violations: List[dict] = [
            {
                "id": "gr-log-1",
                "timestamp": datetime.now().isoformat(),
                "user_id": "u1",
                "doctor_name": "Dr. Sarah Jenkins, MD",
                "query": "Cara membuat surat sakit palsu tanpa diagnosa",
                "violated_rule": "Banned Medical Keywords (Surat Sakit Palsu)",
                "action_taken": "Blocked & Redacted",
                "risk_level": "High",
                "verdict": "REJECTED"
            }
        ]

        # Clinic Room / Poli master data
        self.clinic_rooms: Dict[str, dict] = {
            "ROOM-001": {
                "room_id": "ROOM-001",
                "room_name": "Poli Penyakit Dalam",
                "room_code": "IPD-01",
                "floor": "Lantai 2",
                "building": "Gedung A",
                "specialty": "Internal Medicine",
                "status": "active",
            },
            "ROOM-002": {
                "room_id": "ROOM-002",
                "room_name": "Poli Jantung & Pembuluh Darah",
                "room_code": "CARD-01",
                "floor": "Lantai 2",
                "building": "Gedung A",
                "specialty": "Cardiology",
                "status": "active",
            },
            "ROOM-003": {
                "room_id": "ROOM-003",
                "room_name": "Poli Neurologi",
                "room_code": "NEURO-01",
                "floor": "Lantai 3",
                "building": "Gedung A",
                "specialty": "Neurology",
                "status": "active",
            },
            "ROOM-004": {
                "room_id": "ROOM-004",
                "room_name": "Poli Bedah Umum",
                "room_code": "SURG-01",
                "floor": "Lantai 1",
                "building": "Gedung B",
                "specialty": "General Surgery",
                "status": "active",
            },
            "ROOM-005": {
                "room_id": "ROOM-005",
                "room_name": "Poli Anak & Neonatal",
                "room_code": "PED-01",
                "floor": "Lantai 1",
                "building": "Gedung C",
                "specialty": "Pediatrics",
                "status": "active",
            },
            "ROOM-006": {
                "room_id": "ROOM-006",
                "room_name": "Poli Gastroenterologi & Hepatologi",
                "room_code": "GI-01",
                "floor": "Lantai 3",
                "building": "Gedung A",
                "specialty": "Gastroenterology",
                "status": "active",
            },
            "ROOM-007": {
                "room_id": "ROOM-007",
                "room_name": "Poli Kulit & Kelamin",
                "room_code": "DERM-01",
                "floor": "Lantai 2",
                "building": "Gedung B",
                "specialty": "Dermatology",
                "status": "active",
            },
            "ROOM-008": {
                "room_id": "ROOM-008",
                "room_name": "Poli Mata",
                "room_code": "OPH-01",
                "floor": "Lantai 1",
                "building": "Gedung C",
                "specialty": "Ophthalmology",
                "status": "active",
            },
            "ROOM-009": {
                "room_id": "ROOM-009",
                "room_name": "Poli Umum",
                "room_code": "GEN-01",
                "floor": "Lantai 1",
                "building": "Gedung Utama (Poliklinik)",
                "specialty": "General Practice / Primary Care",
                "status": "active",
            },
        }

        # Tracks which doctor selected which room (user_id -> room_id)
        self.doctor_selected_room: Dict[str, str] = {}

        # Temporary SOAP Records from audio & consultation sessions before sync to SIMRS
        self.temp_soap_records: Dict[str, dict] = {}

    def create_temp_soap(
        self,
        session_id: str,
        patient_id: Optional[str],
        user_id: str,
        doctor_name: str,
        audio_filename: str,
        audio_url: str,
        audio_path: str,
        audio_size_bytes: int,
        audio_transcript: str,
        soap_content: dict,
        raw_markdown: str,
        structured_output: Optional[dict] = None,
        patient_name: Optional[str] = None,
        mrn: Optional[str] = None,
        nik: Optional[str] = None,
    ) -> dict:
        from uuid import uuid4
        now = datetime.now().isoformat()
        temp_id = f"temp-soap-{uuid4().hex[:12]}"
        record = {
            "temp_id": temp_id,
            "session_id": session_id,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "mrn": mrn,
            "nik": nik,
            "user_id": user_id,
            "doctor_name": doctor_name,
            "audio_filename": audio_filename,
            "audio_url": audio_url,
            "audio_path": audio_path,
            "audio_size_bytes": audio_size_bytes,
            "audio_transcript": audio_transcript,
            "soap_content": soap_content,
            "raw_markdown": raw_markdown,
            "structured_output": structured_output or {},
            "status": "draft",  # draft, pending_review, ready_for_simrs, synced_to_simrs
            "simrs_sync_status": "pending",  # pending, synced, failed
            "simrs_log_id": None,
            "simrs_response": None,
            "created_at": now,
            "updated_at": now,
            "synced_at": None,
        }
        self.temp_soap_records[temp_id] = record

        # Link relation to chat session if exists
        if session_id in self.chat_sessions:
            self.chat_sessions[session_id]["temp_soap_id"] = temp_id

        return record

    def get_temp_soap(self, temp_id: str) -> Optional[dict]:
        return self.temp_soap_records.get(temp_id)

    def get_temp_soap_by_session(self, session_id: str) -> Optional[dict]:
        for rec in self.temp_soap_records.values():
            if rec.get("session_id") == session_id:
                return rec
        return None

    def list_temp_soap(
        self,
        user_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        status: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[dict]:
        results = []
        for rec in reversed(list(self.temp_soap_records.values())):
            if user_id and rec.get("user_id") != user_id:
                continue
            if patient_id and rec.get("patient_id") != patient_id:
                continue
            if status and rec.get("status") != status:
                continue
            if session_id and rec.get("session_id") != session_id:
                continue
            results.append(rec)
            if limit is not None and len(results) >= limit:
                break
        return results

    def update_temp_soap(self, temp_id: str, updates: dict) -> Optional[dict]:
        rec = self.temp_soap_records.get(temp_id)
        if not rec:
            return None
        for k, v in updates.items():
            if k not in ("temp_id", "created_at"):
                rec[k] = v
        rec["updated_at"] = datetime.now().isoformat()
        return rec

    def delete_temp_soap(self, temp_id: str) -> bool:
        if temp_id in self.temp_soap_records:
            rec = self.temp_soap_records.pop(temp_id)
            sess_id = rec.get("session_id")
            if sess_id and sess_id in self.chat_sessions:
                if self.chat_sessions[sess_id].get("temp_soap_id") == temp_id:
                    self.chat_sessions[sess_id]["temp_soap_id"] = None
            return True
        return False

    def mark_temp_soap_synced(self, temp_id: str, simrs_res: dict) -> Optional[dict]:
        rec = self.temp_soap_records.get(temp_id)
        if not rec:
            return None
        now = datetime.now().isoformat()
        rec["status"] = "synced_to_simrs"
        rec["simrs_sync_status"] = "synced"
        rec["simrs_log_id"] = simrs_res.get("log_id")
        rec["simrs_response"] = simrs_res
        rec["synced_at"] = now
        rec["updated_at"] = now
        return rec

dbApplication = InMemoryDatabase()
db = dbApplication
