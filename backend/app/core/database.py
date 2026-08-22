from datetime import datetime
from typing import Dict, List, Optional
from app.core.security import get_password_hash

# Mock In-Memory Database Store for modular monolith
class InMemoryDatabase:
    def __init__(self):
        # Pre-seeded users (Doctor & Admin)
        self.users: Dict[str, dict] = {
            "u1": {
                "id": "u1",
                "email": "doctor@aimedical.com",
                "name": "Dr. Sarah Jenkins, MD",
                "hashed_password": get_password_hash("doctor123"),
                "role": "doctor",
                "specialty": "Internal Medicine / Cardiology",
                "license_no": "MD-88392",
                "is_active": True,
                "created_at": datetime.now().isoformat()
            },
            "u2": {
                "id": "u2",
                "email": "admin@aimedical.com",
                "name": "System Administrator",
                "hashed_password": get_password_hash("admin123"),
                "role": "admin",
                "specialty": "System Ops",
                "license_no": "ADM-00001",
                "is_active": True,
                "created_at": datetime.now().isoformat()
            },
            "u3": {
                "id": "u3",
                "email": "dr.chen@aimedical.com",
                "name": "Dr. Marcus Chen, MD",
                "hashed_password": get_password_hash("doctor123"),
                "role": "doctor",
                "specialty": "Oncology",
                "license_no": "MD-91204",
                "is_active": True,
                "created_at": datetime.now().isoformat()
            }
        }
        
        # Pre-seeded patient Electronic Health Records (EHR) mapped to clinic rooms (Poli)
        self.patient_records: Dict[str, dict] = {
            "P-10492": {
                "patient_id": "P-10492",
                "room_id": "ROOM-001",
                "room_name": "Poli Penyakit Dalam",
                "nik": "3201015508600002",
                "ihs_number": "IHS-100010492",
                "name": "Eleanor Vance",
                "age": 64,
                "gender": "Female",
                "vitals": {"bp": "140/90 mmHg", "hr": "78 bpm", "temp": "36.6 C", "sp02": "98%"},
                "diagnoses": ["Hypertension (ICD-10 I10)", "Type 2 Diabetes Mellitus (ICD-10 E11.9)", "CKD Stage 3a (ICD-10 N18.31)"],
                "allergies": ["Penicillin (Syok Anafilaksis)", "Sulfa Drugs (Ruam Difus)"],
                "current_medications": [
                    {"name": "Metformin", "dosage": "1000mg BID"},
                    {"name": "Lisinopril", "dosage": "20mg Daily"},
                    {"name": "Atorvastatin", "dosage": "40mg Daily"}
                ],
                "recent_labs": {
                    "HbA1c": "7.2%",
                    "Fasting Blood Glucose": "142 mg/dL",
                    "eGFR (CKD-EPI)": "58 mL/min/1.73m2",
                    "Serum Creatinine": "1.30 mg/dL",
                    "Serum Potassium": "4.6 mEq/L",
                    "Serum Sodium": "139 mEq/L",
                    "uACR (Urine Albumin/Creatinine)": "120 mg/g",
                    "LDL Cholesterol": "82 mg/dL"
                }
            },
            "P-20811": {
                "patient_id": "P-20811",
                "room_id": "ROOM-002",
                "room_name": "Poli Jantung & Pembuluh Darah",
                "nik": "3174021405790001",
                "ihs_number": "IHS-100020811",
                "name": "Arthur Pendelton",
                "age": 45,
                "gender": "Male",
                "vitals": {"bp": "120/78 mmHg", "hr": "68 bpm", "temp": "36.5 C", "sp02": "99%"},
                "diagnoses": ["CAD Post PCI DES LAD (ICD-10 I25.10)", "Hyperlipidemia (ICD-10 E78.5)", "Stable Angina CCS II (ICD-10 I20.8)"],
                "allergies": ["Aspirin (Dispepsia Berat & Nyeri Epigastrium)"],
                "current_medications": [
                    {"name": "Clopidogrel", "dosage": "75mg Daily"},
                    {"name": "Metoprolol Succinate", "dosage": "50mg Daily"},
                    {"name": "Rosuvastatin", "dosage": "20mg Daily"}
                ],
                "recent_labs": {
                    "Troponin T Kuantitatif": "<0.01 ng/mL",
                    "CK-MB": "14 U/L",
                    "Total Cholesterol": "165 mg/dL",
                    "LDL Cholesterol": "82 mg/dL",
                    "HDL Cholesterol": "48 mg/dL",
                    "Triglycerides": "135 mg/dL",
                    "ALT (SGPT)": "24 U/L",
                    "AST (SGOT)": "22 U/L",
                    "EKG": "Sinus Rhythm HR 68 bpm, T-wave inversion minimal di Lead V4-V5"
                }
            },
            "P-40512": {
                "patient_id": "P-40512",
                "room_id": "ROOM-003",
                "room_name": "Poli Neurologi",
                "nik": "3175031206660001",
                "ihs_number": "IHS-100040512",
                "name": "Budi Santoso",
                "age": 58,
                "gender": "Male",
                "vitals": {"bp": "145/92 mmHg", "hr": "74 bpm", "temp": "36.6 C", "sp02": "98%"},
                "diagnoses": ["Ischemic Stroke Sequelae (ICD-10 I69.3)", "Hemiparesis Dextra (ICD-10 G81.9)", "Vascular Dementia (ICD-10 F01.5)"],
                "allergies": ["Carbamazepine (Stevens-Johnson Syndrome)"],
                "current_medications": [
                    {"name": "Clopidogrel", "dosage": "75mg Daily"},
                    {"name": "Citicoline", "dosage": "500mg BID"},
                    {"name": "Amlodipine", "dosage": "10mg Daily"}
                ],
                "recent_labs": {
                    "CT Brain": "Kronis Infark di Ganglia Basalis Sinistra",
                    "GDP": "110 mg/dL",
                    "Kolesterol Total": "195 mg/dL",
                    "Trigliserida": "160 mg/dL"
                }
            },
            "P-50233": {
                "patient_id": "P-50233",
                "room_id": "ROOM-004",
                "room_name": "Poli Bedah Umum",
                "nik": "3204121809720002",
                "ihs_number": "IHS-100050233",
                "name": "Hendrawan Wijaya",
                "age": 52,
                "gender": "Male",
                "vitals": {"bp": "125/82 mmHg", "hr": "80 bpm", "temp": "36.8 C", "sp02": "99%"},
                "diagnoses": ["Hernia Inguinalis Lateralis Dextra (ICD-10 K40.9)", "Post Cholecystectomy (ICD-10 Z90.49)"],
                "allergies": ["Cefazolin (Urtikaria Akut)"],
                "current_medications": [
                    {"name": "Paracetamol", "dosage": "500mg TID PRN"},
                    {"name": "Cefixime", "dosage": "100mg BID"}
                ],
                "recent_labs": {
                    "Leukosit": "7,400 /uL",
                    "Hemoglobin": "13.8 g/dL",
                    "Trombosit": "240,000 /uL",
                    "USG Abdomen": "Defek cincin inguinal dekstra 1.8 cm reponibilis"
                }
            },
            "P-60781": {
                "patient_id": "P-60781",
                "room_id": "ROOM-005",
                "room_name": "Poli Anak & Neonatal",
                "nik": "3173024501190004",
                "ihs_number": "IHS-100060781",
                "name": "Ananda Rizky",
                "age": 7,
                "gender": "Male",
                "vitals": {"bp": "95/60 mmHg", "hr": "98 bpm", "temp": "37.1 C", "sp02": "99%"},
                "diagnoses": ["Asma Bronkial Eksaserbasi Ringan (ICD-10 J45.901)", "Rinitis Alergi (ICD-10 J30.4)"],
                "allergies": ["Kacang Tanah (Anafilaksis Ringan)"],
                "current_medications": [
                    {"name": "Salbutamol Inhaler", "dosage": "100mcg 2 puff PRN"},
                    {"name": "Cetirizine Sirup", "dosage": "5mg Daily"}
                ],
                "recent_labs": {
                    "IgE Total": "280 IU/mL (Tinggi)",
                    "Eosinofil": "6.2%",
                    "Rontgen Thorax": "Cor dan Pulmo dalam batas normal"
                }
            },
            "P-30124": {
                "patient_id": "P-30124",
                "room_id": "ROOM-006",
                "room_name": "Poli Gastroenterologi & Hepatologi",
                "nik": "3273014502880003",
                "ihs_number": "IHS-100030124",
                "name": "Siti Rahmawati",
                "age": 38,
                "gender": "Female",
                "vitals": {"bp": "115/75 mmHg", "hr": "84 bpm", "temp": "36.7 C", "sp02": "99%"},
                "diagnoses": ["Gastritis Kronis Erosif (ICD-10 K29.1)", "Anemia Defisiensi Besi (ICD-10 D50.9)", "Dispepsia Fungsional (ICD-10 K30)"],
                "allergies": ["NSAID / Ketorolac (Bronkospasme & Angioedema)"],
                "current_medications": [
                    {"name": "Omeprazole", "dosage": "20mg BID AC"},
                    {"name": "Sucralfate Suspensi", "dosage": "500mg/5mL 3x1C AC"},
                    {"name": "Ferrous Fumarate", "dosage": "300mg Daily PC"}
                ],
                "recent_labs": {
                    "Hemoglobin": "10.4 g/dL",
                    "Hematokrit": "32.1%",
                    "Eritrosit": "3.80 x 10^6/uL",
                    "MCV": "74 fL (Mikrositik)",
                    "MCH": "23 pg (Hipokromik)",
                    "Serum Ferritin": "18 ng/mL (Menurun)",
                    "Serum Iron (SI)": "42 ug/dL",
                    "TIBC": "410 ug/dL (Meningkat)",
                    "Leukosit": "6,800 /uL",
                    "Trombosit": "285,000 /uL",
                    "Feses Rutin / Darah Samar": "Negatif (-)"
                }
            },
            "P-70419": {
                "patient_id": "P-70419",
                "room_id": "ROOM-007",
                "room_name": "Poli Kulit & Kelamin",
                "nik": "3271016805970001",
                "ihs_number": "IHS-100070419",
                "name": "Dewi Lestari",
                "age": 29,
                "gender": "Female",
                "vitals": {"bp": "110/70 mmHg", "hr": "72 bpm", "temp": "36.5 C", "sp02": "99%"},
                "diagnoses": ["Dermatitis Atopik Kronis (ICD-10 L20.9)", "Urtikaria Kronis Spontan (ICD-10 L50.8)"],
                "allergies": ["Sulfonamide (Eritema Multiforme)"],
                "current_medications": [
                    {"name": "Desoximetasone Salep 0.25%", "dosage": "2x sehari oles tipis"},
                    {"name": "Loratadine", "dosage": "10mg Daily"}
                ],
                "recent_labs": {
                    "Skin Prick Test": "Sensitisasi debu rumah (+3)",
                    "IgE Spesifik": "Positif Kuat",
                    "Eosinofil Absolut": "450 /uL"
                }
            },
            "P-80922": {
                "patient_id": "P-80922",
                "room_id": "ROOM-008",
                "room_name": "Poli Mata",
                "nik": "3171042308650003",
                "ihs_number": "IHS-100080922",
                "name": "Rudy Hartono",
                "age": 61,
                "gender": "Male",
                "vitals": {"bp": "130/85 mmHg", "hr": "76 bpm", "temp": "36.5 C", "sp02": "98%"},
                "diagnoses": ["Katarak Senilis Matur OD (ICD-10 H25.9)", "Glaukoma Sudut Terbuka OS (ICD-10 H40.11)"],
                "allergies": ["Tidak ada riwayat alergi"],
                "current_medications": [
                    {"name": "Timolol Tetes Mata 0.5%", "dosage": "1 tetes OS BID"},
                    {"name": "Latanoprost 0.005%", "dosage": "1 tetes OS Malam"}
                ],
                "recent_labs": {
                    "Tonometri TIO OD": "14 mmHg",
                    "Tonometri TIO OS": "22 mmHg (Meningkat)",
                    "Visus OD": "1/300",
                    "Visus OS": "6/12"
                }
            },
            "P-90112": {
                "patient_id": "P-90112",
                "room_id": "ROOM-009",
                "room_name": "Poli Umum",
                "nik": "3172051908820005",
                "ihs_number": "IHS-100090112",
                "name": "Bambang Sudarsono",
                "age": 42,
                "gender": "Male",
                "vitals": {"bp": "128/84 mmHg", "hr": "82 bpm", "temp": "37.8 C", "sp02": "99%"},
                "diagnoses": [],
                "allergies": [],
                "current_medications": [
                ],
                "recent_labs": {
                    "Leukosit": "9,800 /uL",
                    "Hemoglobin": "14.2 g/dL",
                    "Trombosit": "265,000 /uL",
                    "Rapid Antigen SARS-CoV-2": "Negatif (-)",
                    "Rapid Test Influenza A/B": "Negatif (-)"
                }
            },
            "P-90234": {
                "patient_id": "P-90234",
                "room_id": "ROOM-009",
                "room_name": "Poli Umum",
                "nik": "3275015206900004",
                "ihs_number": "IHS-100090234",
                "name": "Ratna Kusuma",
                "age": 34,
                "gender": "Female",
                "vitals": {"bp": "118/76 mmHg", "hr": "78 bpm", "temp": "36.6 C", "sp02": "99%"},
                "diagnoses": ["Dispepsia Sindrom / Maag Akut (ICD-10 K30)", "Tension-Type Headache (ICD-10 G44.2)", "Fatigue & Malaise (ICD-10 R53.83)"],
                "allergies": ["Tidak ada riwayat alergi obat (NKDA)"],
                "current_medications": [
                    {"name": "Antasida DOEN Suspensi", "dosage": "3x1 sendok makan AC"},
                    {"name": "Lansoprazole", "dosage": "30mg 1x1 kapsul pagi AC"},
                    {"name": "Vitamin B Complex", "dosage": "1x1 tablet PC"}
                ],
                "recent_labs": {
                    "Gula Darah Sewaktu (GDS)": "104 mg/dL",
                    "Hemoglobin": "12.6 g/dL",
                    "Ureum": "22 mg/dL",
                    "Kreatinin": "0.85 mg/dL",
                    "SGOT": "20 U/L",
                    "SGPT": "18 U/L"
                }
            },
            "P-90356": {
                "patient_id": "P-90356",
                "room_id": "ROOM-009",
                "room_name": "Poli Umum",
                "nik": "3171051203750002",
                "ihs_number": "IHS-100090356",
                "name": "Agus Pratama",
                "age": 49,
                "gender": "Male",
                "vitals": {"bp": "138/88 mmHg", "hr": "80 bpm", "temp": "36.5 C", "sp02": "98%"},
                "diagnoses": ["Hipertensi Pre-Stage 1 (ICD-10 I10)", "Hiperurisemia Asimtomatik (ICD-10 E79.0)", "Kelebihan Berat Badan / Overweight (ICD-10 E66.3)"],
                "allergies": ["Allopurinol (Ruam Makulopapular)"],
                "current_medications": [
                    {"name": "Febuxostat", "dosage": "40mg 1x1 tablet pagi"},
                    {"name": "Amlodipine", "dosage": "5mg 1x1 tablet pagi"}
                ],
                "recent_labs": {
                    "Asam Urat Serum": "8.4 mg/dL (Tinggi)",
                    "Kolesterol Total": "210 mg/dL",
                    "Trigliserida": "175 mg/dL",
                    "GDP": "108 mg/dL",
                    "eGFR": "88 mL/min/1.73m2"
                }
            }
        }

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
        self.soa_notes: Dict[str, dict] = {}

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

db = InMemoryDatabase()
