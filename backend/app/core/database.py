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
                "description": "Layanan rawat jalan umum dan skrining primer",
                "operational_hours": "07:30 - 20:00 WIB",
                "created_at": "2026-01-01T08:00:00",
                "updated_at": "2026-01-01T08:00:00",
            },
        }

        # Initialize existing rooms with default descriptions and timestamps if missing
        now_iso = datetime.now().isoformat()
        for room in self.clinic_rooms.values():
            if "description" not in room:
                room["description"] = f"Layanan spesialis dan rawat jalan {room.get('room_name', '')}"
            if "operational_hours" not in room:
                room["operational_hours"] = "08:00 - 16:00 WIB"
            if "created_at" not in room:
                room["created_at"] = now_iso
            if "updated_at" not in room:
                room["updated_at"] = now_iso

        # Tracks which doctor selected which room (user_id -> room_id)
        self.doctor_selected_room: Dict[str, str] = {}

        # Temporary SOAP Records from audio & consultation sessions before sync to SIMRS
        self.temp_soap_records: Dict[str, dict] = {}

        # MCP (Model Context Protocol) Server & Dynamic Tools Configuration
        self.mcp_config: dict = {
            "server_name": "simrs-hospital-emr-bridge",
            "protocol_version": "2024-11-05",
            "mode": "mock",  # "mock" | "live" | "hybrid"
            "endpoint_url": "https://simrs.hospital.id/api/v1/mcp",
            "auth_type": "bearer",  # "bearer" | "api_key" | "none"
            "auth_token": "",
            "timeout_seconds": 10,
            "retry_attempts": 3,
            "enable_audit_logging": True,
            "auto_sync_enabled": True,
            "custom_headers": {},
            "status": "connected",
            "latency_ms": 12,
            "last_health_check": now_iso,
            "updated_at": now_iso,
        }

        self.mcp_tools: Dict[str, dict] = {
            "simrs.get_patient_profile": {
                "name": "simrs.get_patient_profile",
                "display_name": "Ambil Profil Pasien SIMRS",
                "description": "Retrieves verified demographic information, BPJS card details, and emergency contacts from SIMRS database.",
                "category": "patient_data",
                "is_enabled": True,
                "is_builtin": True,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "mrn": {"type": "string", "description": "SIMRS Medical Record Number (e.g. MRN-SIMRS-10492 or P-10492)"}
                    },
                    "required": ["mrn"]
                },
                "execution_count": 0,
                "last_executed_at": None,
                "created_at": now_iso,
                "updated_at": now_iso,
            },
            "simrs.get_patient_history": {
                "name": "simrs.get_patient_history",
                "display_name": "Ambil Riwayat Medis SIMRS",
                "description": "Retrieves complete inpatient and outpatient visit history, previous discharge summaries, and ongoing chronic disease monitoring notes from SIMRS.",
                "category": "medical_history",
                "is_enabled": True,
                "is_builtin": True,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "mrn": {"type": "string", "description": "SIMRS Medical Record Number"}
                    },
                    "required": ["mrn"]
                },
                "execution_count": 0,
                "last_executed_at": None,
                "created_at": now_iso,
                "updated_at": now_iso,
            },
            "simrs.get_patient_anamnesis": {
                "name": "simrs.get_patient_anamnesis",
                "display_name": "Ambil Anamnesis Klinis SIMRS",
                "description": "Retrieves comprehensive clinical anamnesis from SIMRS (Chief Complaint, RPS, RPD, RPK, Allergy & Review of Systems).",
                "category": "anamnesis",
                "is_enabled": True,
                "is_builtin": True,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "mrn": {"type": "string", "description": "SIMRS Medical Record Number"}
                    },
                    "required": ["mrn"]
                },
                "execution_count": 0,
                "last_executed_at": None,
                "created_at": now_iso,
                "updated_at": now_iso,
            },
            "simrs.get_patient_labs": {
                "name": "simrs.get_patient_labs",
                "display_name": "Evaluasi Hasil Lab & TTV SIMRS",
                "description": "Retrieves real-time and historical laboratory panels, urinalysis, and vital signs from SIMRS LIS/EMR system.",
                "category": "laboratory",
                "is_enabled": True,
                "is_builtin": True,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "mrn": {"type": "string", "description": "SIMRS Medical Record Number"}
                    },
                    "required": ["mrn"]
                },
                "execution_count": 0,
                "last_executed_at": None,
                "created_at": now_iso,
                "updated_at": now_iso,
            },
            "simrs.update_patient_record": {
                "name": "simrs.update_patient_record",
                "display_name": "Kirim & Commit CPPT ke SIMRS",
                "description": "Writes consultation notes, updated primary/secondary diagnoses, and treatment plan into SIMRS Electronic Medical Record (EMR/RME).",
                "category": "transaction",
                "is_enabled": True,
                "is_builtin": True,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "mrn": {"type": "string", "description": "SIMRS Medical Record Number"},
                        "doctor_notes": {"type": "string", "description": "Clinical assessment notes from doctor/AI co-pilot"},
                        "primary_diagnosis": {"type": "string", "description": "Primary clinical diagnosis (with ICD-10 code)"},
                        "treatment_plan": {"type": "string", "description": "Recommended treatment plan & follow-up recommendations"}
                    },
                    "required": ["mrn", "doctor_notes", "primary_diagnosis", "treatment_plan"]
                },
                "execution_count": 0,
                "last_executed_at": None,
                "created_at": now_iso,
                "updated_at": now_iso,
            },
        }

    def get_assigned_doctors_for_room(self, room_id: str) -> List[dict]:
        """Get list of active doctors assigned to a specific room."""
        assigned = []
        for user_id, assigned_room_id in self.doctor_selected_room.items():
            if assigned_room_id == room_id:
                user = self.users.get(user_id)
                if user:
                    assigned.append({
                        "id": user.get("id"),
                        "name": user.get("name"),
                        "email": user.get("email"),
                        "specialty": user.get("specialty"),
                        "license_no": user.get("license_no"),
                    })
        return assigned

    def get_all_clinic_rooms(self, include_assigned_doctors: bool = True) -> List[dict]:
        """Returns all clinic rooms with assigned doctors metadata."""
        rooms = []
        for room in self.clinic_rooms.values():
            room_data = dict(room)
            if include_assigned_doctors:
                room_data["assigned_doctors"] = self.get_assigned_doctors_for_room(room.get("room_id", ""))
            rooms.append(room_data)
        return rooms

    def get_clinic_room(self, room_id: str) -> Optional[dict]:
        """Get clinic room by ID with assigned doctors."""
        room = self.clinic_rooms.get(room_id)
        if not room:
            return None
        room_data = dict(room)
        room_data["assigned_doctors"] = self.get_assigned_doctors_for_room(room_id)
        return room_data

    def create_clinic_room(self, data: dict) -> dict:
        """Create a new clinic room."""
        from uuid import uuid4
        now_iso = datetime.now().isoformat()
        
        # Check if code already exists
        room_code = data.get("room_code", "").strip()
        for r in self.clinic_rooms.values():
            if r.get("room_code", "").lower() == room_code.lower():
                raise ValueError(f"Kode ruangan '{room_code}' sudah digunakan.")
        
        room_id = data.get("room_id")
        if not room_id or room_id in self.clinic_rooms:
            # Generate sequential or UUID-based room ID
            next_num = len(self.clinic_rooms) + 1
            room_id = f"ROOM-{next_num:03d}"
            while room_id in self.clinic_rooms:
                next_num += 1
                room_id = f"ROOM-{next_num:03d}"

        new_room = {
            "room_id": room_id,
            "room_name": data.get("room_name", "").strip(),
            "room_code": room_code,
            "floor": data.get("floor", "Lantai 1").strip(),
            "building": data.get("building", "Gedung A").strip(),
            "specialty": data.get("specialty", "General Medicine").strip(),
            "status": data.get("status", "active"),
            "description": data.get("description", "").strip() or f"Layanan spesialis {data.get('room_name', '')}",
            "operational_hours": data.get("operational_hours", "08:00 - 16:00 WIB").strip(),
            "created_at": now_iso,
            "updated_at": now_iso,
        }
        self.clinic_rooms[room_id] = new_room
        return self.get_clinic_room(room_id)

    def update_clinic_room(self, room_id: str, updates: dict) -> Optional[dict]:
        """Update an existing clinic room."""
        room = self.clinic_rooms.get(room_id)
        if not room:
            return None
        
        new_code = updates.get("room_code")
        if new_code:
            new_code = new_code.strip()
            for rid, r in self.clinic_rooms.items():
                if rid != room_id and r.get("room_code", "").lower() == new_code.lower():
                    raise ValueError(f"Kode ruangan '{new_code}' sudah digunakan oleh ruangan lain.")
            room["room_code"] = new_code

        for key in ["room_name", "floor", "building", "specialty", "status", "description", "operational_hours"]:
            if key in updates and updates[key] is not None:
                room[key] = updates[key].strip() if isinstance(updates[key], str) else updates[key]

        room["updated_at"] = datetime.now().isoformat()
        return self.get_clinic_room(room_id)

    def delete_clinic_room(self, room_id: str) -> bool:
        """Delete clinic room and remove doctor assignments."""
        if room_id not in self.clinic_rooms:
            return False
        
        self.clinic_rooms.pop(room_id)
        # Unassign doctors assigned to this room
        doctors_to_unassign = [uid for uid, rid in self.doctor_selected_room.items() if rid == room_id]
        for uid in doctors_to_unassign:
            self.doctor_selected_room.pop(uid, None)
        return True

    def toggle_clinic_room_status(self, room_id: str) -> Optional[dict]:
        """Toggle clinic room status between active and inactive."""
        room = self.clinic_rooms.get(room_id)
        if not room:
            return None
        
        current_status = room.get("status", "active")
        room["status"] = "inactive" if current_status == "active" else "active"
        room["updated_at"] = datetime.now().isoformat()
        
        # If deactivated, unassign active doctors
        if room["status"] != "active":
            doctors_to_unassign = [uid for uid, rid in self.doctor_selected_room.items() if rid == room_id]
            for uid in doctors_to_unassign:
                self.doctor_selected_room.pop(uid, None)
                
        return self.get_clinic_room(room_id)

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

    # ── Dynamic MCP Configuration & Tool Methods ────────────────────

    def get_mcp_config(self) -> dict:
        """Get current MCP server configuration."""
        return dict(self.mcp_config)

    def update_mcp_config(self, updates: dict) -> dict:
        """Update MCP server configuration."""
        for k, v in updates.items():
            if v is not None:
                self.mcp_config[k] = v
        self.mcp_config["updated_at"] = datetime.now().isoformat()
        return dict(self.mcp_config)

    def get_all_mcp_tools(self, active_only: bool = False) -> List[dict]:
        """Get all configured MCP tools, optionally filtering active ones."""
        tools = []
        for t in self.mcp_tools.values():
            if active_only and not t.get("is_enabled", True):
                continue
            tools.append(dict(t))
        return tools

    def get_mcp_tool(self, tool_name: str) -> Optional[dict]:
        """Get detail of a single MCP tool."""
        tool = self.mcp_tools.get(tool_name)
        return dict(tool) if tool else None

    def create_custom_mcp_tool(self, tool_data: dict) -> dict:
        """Register a new custom MCP tool."""
        name = (tool_data.get("name") or "").strip()
        if not name:
            raise ValueError("Nama tool MCP tidak boleh kosong.")
        if name in self.mcp_tools:
            raise ValueError(f"Tool MCP dengan nama '{name}' sudah terdaftar.")

        now_iso = datetime.now().isoformat()
        new_tool = {
            "name": name,
            "display_name": tool_data.get("display_name") or name,
            "description": tool_data.get("description") or f"Custom MCP Tool: {name}",
            "category": tool_data.get("category") or "custom",
            "is_enabled": tool_data.get("is_enabled", True),
            "is_builtin": False,
            "input_schema": tool_data.get("input_schema") or {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Parameter kueri / pencarian"}},
            },
            "custom_endpoint": tool_data.get("custom_endpoint"),
            "mock_response": tool_data.get("mock_response"),
            "execution_count": 0,
            "last_executed_at": None,
            "created_at": now_iso,
            "updated_at": now_iso,
        }
        self.mcp_tools[name] = new_tool
        return dict(new_tool)

    def update_mcp_tool(self, tool_name: str, updates: dict) -> Optional[dict]:
        """Update metadata, description, or schema of an existing MCP tool."""
        tool = self.mcp_tools.get(tool_name)
        if not tool:
            return None
        for k, v in updates.items():
            if k not in ("name", "is_builtin", "created_at") and v is not None:
                tool[k] = v
        tool["updated_at"] = datetime.now().isoformat()
        return dict(tool)

    def toggle_mcp_tool_status(self, tool_name: str) -> Optional[dict]:
        """Toggle active/inactive status of an MCP tool."""
        tool = self.mcp_tools.get(tool_name)
        if not tool:
            return None
        tool["is_enabled"] = not tool.get("is_enabled", True)
        tool["updated_at"] = datetime.now().isoformat()
        return dict(tool)

    def delete_mcp_tool(self, tool_name: str) -> bool:
        """Delete a custom MCP tool (builtin tools cannot be deleted)."""
        tool = self.mcp_tools.get(tool_name)
        if not tool:
            return False
        if tool.get("is_builtin", False):
            raise ValueError(f"Tool bawaan '{tool_name}' tidak dapat dihapus. Anda dapat menonaktifkannya.")
        del self.mcp_tools[tool_name]
        return True

    def record_mcp_tool_execution(self, tool_name: str):
        """Increment tool execution count and record execution timestamp."""
        tool = self.mcp_tools.get(tool_name)
        if tool:
            tool["execution_count"] = tool.get("execution_count", 0) + 1
            tool["last_executed_at"] = datetime.now().isoformat()


dbApplication = InMemoryDatabase()
db = dbApplication
