from datetime import datetime
from typing import Dict, Any, List

# ==============================================================================
# SIMRS EMR REPOSITORY ENGINE
# ==============================================================================
class SIMRSEMRRepository:
    """SIMRS (Sistem Informasi Manajemen Rumah Sakit) EMR Database."""
    
    def __init__(self):
        self.patient_profiles: Dict[str, Dict[str, Any]] = {
            "MRN-SIMRS-10492": {
                "mrn": "MRN-SIMRS-10492",
                "nik": "3174095408600002",
                "full_name": "Eleanor Vance",
                "gender": "Female",
                "age": 64,
                "birth_date": "1960-08-14",
                "bpjs_card_no": "0001849204921",
                "bpjs_class": "Kelas 1 (BPJS Kesehatan)",
                "blood_type": "O+",
                "phone": "+62 812-9840-2841",
                "address": "Jl. Metro Pondok Indah No. 42, Jakarta Selatan",
                "active_clinic": "Poli Penyakit Dalam (Internal Medicine Clinic)",
                "attending_physician": "Dr. Sarah Jenkins, Sp.PD"
            },
            "MRN-SIMRS-20811": {
                "mrn": "MRN-SIMRS-20811",
                "nik": "3201021504790005",
                "full_name": "Arthur Pendelton",
                "gender": "Male",
                "age": 45,
                "birth_date": "1979-04-15",
                "bpjs_card_no": "0002940182740",
                "bpjs_class": "Non-BPJS / Executive Insurance",
                "blood_type": "A+",
                "phone": "+62 811-2049-1029",
                "address": "Jl. Senopati No. 88, Jakarta Selatan",
                "active_clinic": "Poli Jantung & Pembuluh Darah (Cardiology)",
                "attending_physician": "Dr. Marcus Chen, Sp.JP"
            },
            "MRN-SIMRS-30124": {
                "mrn": "MRN-SIMRS-30124",
                "nik": "3273014502880003",
                "full_name": "Siti Rahmawati",
                "gender": "Female",
                "age": 38,
                "birth_date": "1988-02-15",
                "bpjs_card_no": "0003849102845",
                "bpjs_class": "Kelas 2 (BPJS Kesehatan)",
                "blood_type": "B+",
                "phone": "+62 813-8821-9042",
                "address": "Jl. Cihampelas No. 104, Bandung",
                "active_clinic": "Poli Gastroenterologi & Hepatologi",
                "attending_physician": "Dr. Sarah Jenkins, Sp.PD"
            },
            "MRN-SIMRS-40512": {
                "mrn": "MRN-SIMRS-40512",
                "nik": "3175031206660001",
                "full_name": "Budi Santoso",
                "gender": "Male",
                "age": 58,
                "birth_date": "1966-06-12",
                "bpjs_card_no": "0004819201948",
                "bpjs_class": "Kelas 1 (BPJS Kesehatan)",
                "blood_type": "O+",
                "phone": "+62 812-3940-1092",
                "address": "Jl. Tebet Barat Raya No. 18, Jakarta Selatan",
                "active_clinic": "Poli Neurologi",
                "attending_physician": "Dr. Aditya Pratama, Sp.N"
            },
            "MRN-SIMRS-50233": {
                "mrn": "MRN-SIMRS-50233",
                "nik": "3204121809720002",
                "full_name": "Hendrawan Wijaya",
                "gender": "Male",
                "age": 52,
                "birth_date": "1972-09-18",
                "bpjs_card_no": "0005928104829",
                "bpjs_class": "Kelas 2 (BPJS Kesehatan)",
                "blood_type": "A+",
                "phone": "+62 811-9284-0192",
                "address": "Jl. Sukajadi No. 55, Bandung",
                "active_clinic": "Poli Bedah Umum",
                "attending_physician": "Dr. Bambang Setiawan, Sp.B"
            },
            "MRN-SIMRS-60781": {
                "mrn": "MRN-SIMRS-60781",
                "nik": "3173024501190004",
                "full_name": "Ananda Rizky",
                "gender": "Male",
                "age": 7,
                "birth_date": "2019-01-05",
                "bpjs_card_no": "0006819204928",
                "bpjs_class": "Kelas 1 (BPJS Kesehatan)",
                "blood_type": "B+",
                "phone": "+62 813-1928-4091",
                "address": "Jl. Kemang Raya No. 12, Jakarta Selatan",
                "active_clinic": "Poli Anak & Neonatal",
                "attending_physician": "Dr. Ratna Dewi, Sp.A"
            },
            "MRN-SIMRS-70419": {
                "mrn": "MRN-SIMRS-70419",
                "nik": "3271016805970001",
                "full_name": "Dewi Lestari",
                "gender": "Female",
                "age": 29,
                "birth_date": "1997-05-28",
                "bpjs_card_no": "0007819204910",
                "bpjs_class": "Non-BPJS / Swasta",
                "blood_type": "AB+",
                "phone": "+62 812-9901-4820",
                "address": "Jl. Pajajaran No. 76, Bogor",
                "active_clinic": "Poli Kulit & Kelamin",
                "attending_physician": "Dr. Cindy Clarissa, Sp.DVE"
            },
            "MRN-SIMRS-80922": {
                "mrn": "MRN-SIMRS-80922",
                "nik": "3171042308650003",
                "full_name": "Rudy Hartono",
                "gender": "Male",
                "age": 61,
                "birth_date": "1965-08-23",
                "bpjs_card_no": "0008920194820",
                "bpjs_class": "Kelas 1 (BPJS Kesehatan)",
                "blood_type": "O+",
                "phone": "+62 811-3094-1920",
                "address": "Jl. Salemba Raya No. 34, Jakarta Pusat",
                "active_clinic": "Poli Mata",
                "attending_physician": "Dr. Farhan Hidayat, Sp.M"
            },           
            "MRN-SIMRS-90234": {
                "mrn": "MRN-SIMRS-90234",
                "nik": "3275015206900004",
                "full_name": "Ratna Kusuma",
                "gender": "Female",
                "age": 34,
                "birth_date": "1990-06-12",
                "bpjs_card_no": "0009283019284",
                "bpjs_class": "Kelas 2 (BPJS Kesehatan)",
                "blood_type": "B+",
                "phone": "+62 813-9028-1092",
                "address": "Jl. Juanda No. 19, Bekasi",
                "active_clinic": "Poli Umum",
                "attending_physician": "Dr. Sarah Jenkins, Sp.PD"
            },
            "MRN-SIMRS-90356": {
                "mrn": "MRN-SIMRS-90356",
                "nik": "3171051203750002",
                "full_name": "Agus Pratama",
                "gender": "Male",
                "age": 49,
                "birth_date": "1975-03-12",
                "bpjs_card_no": "0009384019283",
                "bpjs_class": "Kelas 1 (BPJS Kesehatan)",
                "blood_type": "O+",
                "phone": "+62 811-9201-9482",
                "address": "Jl. Percetakan Negara No. 80, Jakarta Pusat",
                "active_clinic": "Poli Umum",
                "attending_physician": "Dr. Sarah Jenkins, Sp.PD"
            }
        }
        
        self.medical_histories: Dict[str, Dict[str, Any]] = {
            "MRN-SIMRS-10492": {
                "mrn": "MRN-SIMRS-10492",
                "chronic_conditions": ["Hypertension (ICD-10 I10)", "Type 2 Diabetes Mellitus (ICD-10 E11.9)", "CKD Stage 3a (ICD-10 N18.31)"],
                "documented_allergies": ["Penicillin (Syok Anafilaksis)", "Sulfa Drugs (Ruam Difus)"],
                "past_admissions": [
                    {
                        "admission_date": "2025-11-10",
                        "discharge_date": "2025-11-14",
                        "diagnosis": "Hyperglycemic Hyperosmolar State (HHS)",
                        "discharge_summary": "Treated with IV hydration & Insulin infusion. Discharged on oral Metformin."
                    }
                ],
                "last_soap_progress_note": {
                    "note_date": "2026-07-01 09:30",
                    "practitioner": "Dr. Sarah Jenkins, Sp.PD (K-EMD)",
                    "clinic": "Poli Penyakit Dalam / Endokrin Metabolik",
                    "subjective": "Pasien kontrol berkala DM Tipe 2 & HT. Keluhan kesemutan berkala pada kedua ujung jari kaki. Badan lemas hilang timbul. Tidak ada nyeri dada atau sesak napas. Kepatuhan minum obat rutin teratur.",
                    "objective": "TD: 138/88 mmHg, Nadi: 76x/m, Suhu: 36.6°C, BMI: 27.2 kg/m². Lab serial: HbA1c 7.2%, eGFR 58 mL/min/1.73m² (CKD 3a), uACR 120 mg/g (Mikroalbuminuria). Monofilament test kaki: sensibilitas menurun ringan distal.",
                    "assessment": "1. Type 2 Diabetes Mellitus dengan Diabetic Peripheral Neuropathy & CKD Stage 3a (ICD-10 E11.22 / N18.31). 2. Primary Hypertension Stage 1 (ICD-10 I10).",
                    "plan": "Lanjutkan Metformin 1000mg BID + Lisinopril 20mg Daily + Atorvastatin 40mg Daily. Edukasi perawatan kaki mandiri dan pembatasan asupan garam (<2g/hari). Kontrol ulang lab profil lipid & urinalisis dalam 3 bulan."
                },
                "historical_labs": [
                    {"date": "2026-07-01", "lab": "HbA1c", "value": "7.2%", "unit": "%", "status": "Slightly Elevated"},
                    {"date": "2026-07-01", "lab": "eGFR", "value": "58", "unit": "mL/min/1.73m²", "status": "Stage 3a CKD"},
                    {"date": "2026-07-01", "lab": "Serum Creatinine", "value": "1.3", "unit": "mg/dL", "status": "Elevated"}
                ]
            },
            "MRN-SIMRS-20811": {
                "mrn": "MRN-SIMRS-20811",
                "chronic_conditions": ["Acute Coronary Syndrome (ICD-10 I24.9)", "Hyperlipidemia (ICD-10 E78.5)"],
                "documented_allergies": ["Aspirin (Dispepsia Berat & Nyeri Epigastrium)"],
                "past_admissions": [
                    {
                        "admission_date": "2026-02-18",
                        "discharge_date": "2026-02-22",
                        "diagnosis": "NSTEMI - Drug Eluting Stent (DES) placed in LAD",
                        "discharge_summary": "Successful PCI to LAD. Discharged on DAPT (Clopidogrel + Aspirin) & Statin."
                    }
                ],
                "last_soap_progress_note": {
                    "note_date": "2026-06-15 10:15",
                    "practitioner": "Dr. Maya, Sp.JP (K-Intervensi)",
                    "clinic": "Poli Jantung & Pembuluh Darah",
                    "subjective": "Kontrol pasca PCI stent DES di LAD (Bulan ke-4). Rasa berat dada ringan hanya jika jalan cepat menanjak >200m (Angina CCS II), membaik spontan dalam 2 menit istirahat. Ortopnea (-), DOE (-).",
                    "objective": "TD: 120/78 mmHg, Nadi: 68x/m reguler, SpO2: 99%. EKG: Sinus Rhythm HR 68 bpm, T-wave inversion minimal di V4-V5. Lab: Troponin T <0.01 ng/mL, CK-MB 14 U/L, LDL-C 82 mg/dL.",
                    "assessment": "1. Chronic Coronary Syndrome (CAD post-PCI DES to LAD) with Stable Angina Pectoris (CCS Class II). 2. Controlled Dyslipidemia on High-Intensity Statin.",
                    "plan": "Lanjutkan DAPT (Clopidogrel 75mg + Metoprolol 50mg + Rosuvastatin 20mg). Edukasi aktivitas fisik aerobik bertahap & hindari stres berlebih. ISDN 5mg Sublingual PRN bila nyeri dada."
                },
                "historical_labs": [
                    {"date": "2026-06-15", "lab": "Troponin T", "value": "<0.01", "unit": "ng/mL", "status": "Normal"},
                    {"date": "2026-06-15", "lab": "LDL Cholesterol", "value": "82", "unit": "mg/dL", "status": "On Target"}
                ]
            },
            "MRN-SIMRS-30124": {
                "mrn": "MRN-SIMRS-30124",
                "chronic_conditions": ["Gastritis Kronis Erosif (ICD-10 K29.1)", "Anemia Defisiensi Besi (ICD-10 D50.9)", "Dispepsia Fungsional (ICD-10 K30)"],
                "documented_allergies": ["NSAID / Ketorolac (Bronkospasme & Angioedema)", "Asam Mefenamat (Urtikaria Akut)"],
                "past_admissions": [
                    {
                        "admission_date": "2025-09-12",
                        "discharge_date": "2025-09-15",
                        "diagnosis": "Hematemesis Melena Ringan ec Gastritis Erosif",
                        "discharge_summary": "Injeksi PPI Omeprazole 40mg IV & Transfusi PRC 1 unit. Pasca rawat membaik, dilanjutkan terapi oral."
                    }
                ],
                "last_soap_progress_note": {
                    "note_date": "2026-05-10 11:00",
                    "practitioner": "Dr. Sarah Jenkins, Sp.PD",
                    "clinic": "Poli Gastroenterologi & Hepatologi",
                    "subjective": "Pasien kontrol keluhan dispepsia kambuhan dan badan sering lemas/pucat. Perih ulu hati dirasakan hilang timbul setelah minum obat anti-nyeri bebas. BAB hitam disangkal, muntah darah (-).",
                    "objective": "TD: 115/75 mmHg, Nadi: 80x/m, Konjungtiva anemis (+/+), Nyeri tekan regio epigastrium (+). Lab: Hb 10.4 g/dL, MCV 74 fL (Mikrositik hipokromik), Serum Ferritin 18 ng/mL, Benzidine test (-).",
                    "assessment": "1. Gastritis Kronis Erosif ec susp NSAID-induced gastropathy (ICD-10 K29.1). 2. Anemia Defisiensi Besi sekunder (ICD-10 D50.9).",
                    "plan": "Omeprazole 20mg BID AC, Sucralfate suspensi 3x1C AC, Tablet Tambah Darah (Ferrous Fumarate 300mg) 1x1 PC berjarak 2 jam dari antasida/sucralfate. KIE: KONTRAINDIKASI MUTLAK segala jenis NSAID (Ketorolac, Asam Mefenamat)."
                },
                "historical_labs": [
                    {"date": "2026-05-10", "lab": "Hemoglobin", "value": "10.4", "unit": "g/dL", "status": "Anemia Ringan-Sedang"},
                    {"date": "2026-05-10", "lab": "Serum Ferritin", "value": "18", "unit": "ng/mL", "status": "Cadangan Besi Rendah"},
                    {"date": "2026-05-10", "lab": "MCV", "value": "74", "unit": "fL", "status": "Mikrositik"}
                ]
            },
            "MRN-SIMRS-40512": {
                "mrn": "MRN-SIMRS-40512",
                "chronic_conditions": ["Ischemic Stroke Sequelae (ICD-10 I69.3)", "Hemiparesis Dextra (ICD-10 G81.9)", "Vascular Dementia (ICD-10 F01.5)"],
                "documented_allergies": ["Carbamazepine (Stevens-Johnson Syndrome)"],
                "past_admissions": [
                    {
                        "admission_date": "2025-10-01",
                        "discharge_date": "2025-10-08",
                        "diagnosis": "Acute Ischemic Stroke - Left MCA Infarct",
                        "discharge_summary": "Treated with antiplatelet, neuroprotectant, and motor rehabilitation."
                    }
                ],
                "last_soap_progress_note": {
                    "note_date": "2026-06-20 10:00",
                    "practitioner": "Dr. Aditya Pratama, Sp.N",
                    "clinic": "Poli Neurologi",
                    "subjective": "Kontrol rutin pasca stroke iskemik 8 bulan lalu. Kelemahan sisi tubuh kanan membaik dengan fisioterapi, bicara agak pelo berkurang.",
                    "objective": "TD: 145/92 mmHg, Nadi: 74x/m, GCS: E4M6V5, Kekuatan motorik: 4/5 dekstra, 5/5 sinistra. Refleks Babinski (+/-).",
                    "assessment": "Post Ischemic Stroke dengan Hemiparesis Dextra & Hipertensi Stage 2.",
                    "plan": "Clopidogrel 75mg 1x1, Citicoline 500mg 2x1, Amlodipine 10mg 1x1. Lanjutkan program rehabilitasi medik 2x seminggu."
                },
                "historical_labs": [
                    {"date": "2026-06-20", "lab": "GDP", "value": "110", "unit": "mg/dL", "status": "Normal"},
                    {"date": "2026-06-20", "lab": "Total Cholesterol", "value": "195", "unit": "mg/dL", "status": "Borderline"}
                ]
            },            
            "MRN-SIMRS-60781": {
                "mrn": "MRN-SIMRS-60781",
                "chronic_conditions": ["Asma Bronkial Eksaserbasi Ringan (ICD-10 J45.901)", "Rinitis Alergi (ICD-10 J30.4)"],
                "documented_allergies": ["Kacang Tanah (Anafilaksis Ringan)"],
                "past_admissions": [
                    {
                        "admission_date": "2025-12-20",
                        "discharge_date": "2025-12-22",
                        "diagnosis": "Asma Bronkial Serangan Sedang",
                        "discharge_summary": "Nebulisasi Salbutamol + Budesonide, membaik dipulangkan."
                    }
                ],
                "last_soap_progress_note": {
                    "note_date": "2026-07-12 09:00",
                    "practitioner": "Dr. Ratna Dewi, Sp.A",
                    "clinic": "Poli Anak & Neonatal",
                    "subjective": "Batuk berdahak dan mengi ringan pada malam hari terutama saat cuaca dingin. Demam (-).",
                    "objective": "TD: 95/60 mmHg, Nadi: 98x/m, RR: 22x/m, SpO2: 99% RA. Pulmo: wheezing ekspiratoar minimal bilateral.",
                    "assessment": "Asma Bronkial Intermiten - Eksaserbasi Ringan ec Paparan Suhu Dingin.",
                    "plan": "Inhaler Salbutamol 100mcg 2 puff PRN saat sesak/mengi, Cetirizine sirup 5mg 1x1 malam. KIE hindari debu dan alergen."
                },
                "historical_labs": [
                    {"date": "2026-07-12", "lab": "IgE Total", "value": "280", "unit": "IU/mL", "status": "Elevated"},
                    {"date": "2026-07-12", "lab": "Eosinofil", "value": "6.2", "unit": "%", "status": "Mild Eosinophilia"}
                ]
            },
            "MRN-SIMRS-70419": {
                "mrn": "MRN-SIMRS-70419",
                "chronic_conditions": ["Dermatitis Atopik Kronis (ICD-10 L20.9)", "Urtikaria Kronis Spontan (ICD-10 L50.8)"],
                "documented_allergies": ["Sulfonamide (Eritema Multiforme)"],
                "past_admissions": [],
                "last_soap_progress_note": {
                    "note_date": "2026-07-18 10:45",
                    "practitioner": "Dr. Cindy Clarissa, Sp.DVE",
                    "clinic": "Poli Kulit & Kelamin",
                    "subjective": "Gatal hebat pada kedua fosa antekubiti dan leher disertai bercak kemerahan menebal dan bersisik.",
                    "objective": "Status Dermatologis: Plak eritematosa batas tidak tegas dengan likenifikasi dan ekskoriasi di regio fleksural kubiti bilateral.",
                    "assessment": "Dermatitis Atopik Kronis Fase Eksaserbasi.",
                    "plan": "Desoximetasone salep 0.25% 2x sehari oles tipis selama 5 hari, Loratadine 10mg 1x1 tab. Emolien ceramide rutin setelah mandi."
                },
                "historical_labs": [
                    {"date": "2026-07-18", "lab": "IgE Spesifik Debu", "value": "Positif Kuat", "unit": "kU/L", "status": "Positive"},
                    {"date": "2026-07-18", "lab": "Eosinofil Absolut", "value": "450", "unit": "/uL", "status": "Normal-High"}
                ]
            },
            "MRN-SIMRS-80922": {
                "mrn": "MRN-SIMRS-80922",
                "chronic_conditions": ["Katarak Senilis Matur OD (ICD-10 H25.9)", "Glaukoma Sudut Terbuka OS (ICD-10 H40.11)"],
                "documented_allergies": ["Tidak ada riwayat alergi"],
                "past_admissions": [],
                "last_soap_progress_note": {
                    "note_date": "2026-07-22 08:30",
                    "practitioner": "Dr. Farhan Hidayat, Sp.M",
                    "clinic": "Poli Mata",
                    "subjective": "Penglihatan mata kanan semakin buram seperti tertutup kabut tebal sejak 6 bulan terakhir. Mata kiri terkadang pegal.",
                    "objective": "Visus OD: 1/300, OS: 6/12 dengan koreksi. Lensa OD: keruh total putih (matur), shadow test (-). TIO OD: 14 mmHg, OS: 22 mmHg.",
                    "assessment": "1. Katarak Senilis Matur Oculi Dextra. 2. Glaukoma Sudut Terbuka Primer Oculi Sinistra.",
                    "plan": "Pro Fakoemulsifikasi + IOL OD. Terapi OS: Timolol tetes mata 0.5% 2x1 tetes, Latanoprost 0.005% 1x1 tetes malam hari."
                },
                "historical_labs": [
                    {"date": "2026-07-22", "lab": "TIO OD", "value": "14", "unit": "mmHg", "status": "Normal"},
                    {"date": "2026-07-22", "lab": "TIO OS", "value": "22", "unit": "mmHg", "status": "Elevated"}
                ]
            }
        }
        
        self.patient_anamnesis: Dict[str, Dict[str, Any]] = {
            "MRN-SIMRS-10492": {
                "mrn": "MRN-SIMRS-10492",
                "patient_name": "Eleanor Vance",
                "chief_complaint": "Pusing berputar, lemas sejak 3 hari, sering kencing di malam hari (nokturia 3-4x), serta kesemutan pada kedua ujung jari kaki.",
                "history_present_illness": (
                    "Pasien perempuan 64 tahun datang untuk evaluasi berkala dengan keluhan lemas yang memberat dalam 3 hari terakhir. "
                    "Nafsu makan sedikit menurun, rasa haus meningkat (polidipsia). Tidak ada demam, mual muntah (-), nyeri dada (-), sesak napas (-). "
                    "Tekanan darah pemantauan mandiri di rumah berkisar 138-145/88-92 mmHg."
                ),
                "past_medical_history": "Hipertensi esensial (10 tahun), Diabetes Melitus Tipe 2 (8 tahun), CKD Stage 3a (1 tahun lalu).",
                "family_history": "Ayah riwayat Stroke Iskemik (usia 62 th), Ibu riwayat DM Tipe 2.",
                "medication_history": "Metformin 1000mg BID, Lisinopril 20mg Daily, Atorvastatin 40mg Daily. Kepatuhan konsumsi obat teratur.",
                "allergy_history": "Alergi berat Penisilin (riwayat syok anafilaksis) dan Sulfa Drugs (ruam makulopapular difus).",
                "lifestyle_factors": "Diet rendah garam kurang teratur, aktivitas fisik ringan jalan pagi 15 menit 2x seminggu, tidak merokok/alkohol.",
                "review_of_systems": {
                    "neurologi": "Parestesia (kesemutan) distal bilateral simetris pada kedua kaki",
                    "kardiovaskular": "Nyeri dada (-), palpitasi (-), ortopnea (-)",
                    "respirasi": "Batuk (-), sesak (-)",
                    "gastrointestinal": "Mual (-), muntah (-), nyeri ulu hati (-)",
                    "urologi": "Nokturia 3-4x/malam, disuria (-), hematuria (-)"
                }
            },
            "MRN-SIMRS-20811": {
                "mrn": "MRN-SIMRS-20811",
                "patient_name": "Arthur Pendelton",
                "chief_complaint": "Dada terasa tidak nyaman dan mudah lelah saat beraktivitas menaiki tangga.",
                "history_present_illness": (
                    "Pasien laki-laki 45 tahun pasca PCI DES LAD 6 bulan lalu mengeluhkan rasa tidak nyaman pada dada anterior "
                    "saat menaiki tangga 2 lantai. Nyeri mereda dengan istirahat dalam 5 menit. Tidak menjalar ke lengan atau rahang. Keringat dingin (-)."
                ),
                "past_medical_history": "NSTEMI post PCI DES LAD (Februari 2026), Dislipidemia.",
                "family_history": "Ayah meninggal mendadak akibat serangan jantung koroner pada usia 50 tahun.",
                "medication_history": "Clopidogrel 75mg Daily, Metoprolol Succinate 50mg Daily, Rosuvastatin 20mg Daily.",
                "allergy_history": "Aspirin (gangguan lambung / dispepsia berat).",
                "lifestyle_factors": "Mantan perokok (berhenti 6 bulan lalu), tingkat stres pekerjaan tinggi.",
                "review_of_systems": {
                    "kardiovaskular": "Angina stabil saat aktivitas (CCS Class II), palpitasi (-)",
                    "respirasi": "Sesak napas saat aktivitas berat (-)",
                    "gastrointestinal": "Dispepsia (-)"
                }
            },
            "MRN-SIMRS-30124": {
                "mrn": "MRN-SIMRS-30124",
                "patient_name": "Siti Rahmawati",
                "chief_complaint": "Nyeri ulu hati terasa perih terbakar sejak 1 minggu, mual terutama setelah makan, perut terasa kembung begah, serta lemas dan pusing saat berdiri tiba-tiba.",
                "history_present_illness": (
                    "Pasien perempuan 38 tahun datang dengan keluhan nyeri ulu hati (epigastric burning discomfort) yang kambuh dalam 1 minggu terakhir. "
                    "Nyeri memberat terutama setelah mengonsumsi makanan pedas atau asam, disertai rasa mual dan cepat kenyang. "
                    "Keluhan lemas dan pusing kunang-kunang dialami sejak 3 hari, riwayat muntah darah atau BAB hitam (melena) disangkal. "
                    "Pasien mengakui riwayat sering mengonsumsi obat anti-nyeri bebas (analgetik warung) saat sakit kepala."
                ),
                "past_medical_history": "Gastritis kronis erosif terdiagnosis via EGD (2025), riwayat Anemia Defisiensi Besi.",
                "family_history": "Ibu memiliki riwayat ulkus peptikum kronis.",
                "medication_history": "Omeprazole 20mg BID AC, Sucralfate suspensi 500mg/5mL 3x1C AC, Ferrous Fumarate 300mg Daily PC.",
                "allergy_history": "Alergi berat NSAID (Ketorolac & Asam Mefenamat) dengan manifestasi bronkospasme dan angioedema wajah.",
                "lifestyle_factors": "Jadwal makan tidak teratur, sering konsumsi kopi hitam 2 cangkir/hari, tingkat stres pekerjaan sedang.",
                "review_of_systems": {
                    "gastrointestinal": "Nyeri tekan epigastrium (+), rasa terbakar retrosternal (+), mual (+), muntah (-), melena (-)",
                    "neurologi": "Pusing ortostatik / kunang-kunang (+), parestesia (-)",
                    "kardiovaskular": "Palpitasi ringan saat lemas (+), nyeri dada tipikal (-)",
                    "respirasi": "Sesak napas (-), batuk (-)",
                    "urologi": "BAK normal lancar, hematuria (-)"
                }
            }
        }
        
        self.emr_consultation_logs: List[Dict[str, Any]] = [
            {
                "log_id": "SIMRS-LOG-001",
                "timestamp": "2026-08-01T09:30:00",
                "mrn": "MRN-SIMRS-10492",
                "doctor_name": "Dr. Sarah Jenkins, Sp.PD",
                "primary_diagnosis": "Type 2 Diabetes Mellitus with CKD Stage 3a",
                "doctor_notes": "Routine follow-up. eGFR stable at 58. Continue Lisinopril 20mg & Metformin 1000mg BID.",
                "treatment_plan": "Re-check BMP in 3 months. Advise strict glycemic & BP control.",
                "synced_status": "Committed to RME SIMRS"
            }
        ]

simrs_repo = SIMRSEMRRepository()


# ==============================================================================
# DEDICATED MCP SERVER CLASS
# ==============================================================================
class SIMRSMCPServer:
    """Standalone MCP Server implementing Model Context Protocol standard for SIMRS."""
    
    PROTOCOL_VERSION = "2024-11-05"
    SERVER_NAME = "SIMRS-EMR-MCP-Server"
    SERVER_VERSION = "1.0.0"

    def list_tools(self) -> List[Dict[str, Any]]:
        """Returns MCP registered tool declarations."""
        return [
            {
                "name": "simrs.get_patient_profile",
                "description": "Fetches SIMRS patient demographics, NIK, BPJS status, age, sex, and clinic assignment by MRN.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "mrn": {"type": "string", "description": "SIMRS Medical Record Number (e.g. MRN-SIMRS-10492)"}
                    },
                    "required": ["mrn"]
                }
            },
            {
                "name": "simrs.get_patient_history",
                "description": "Retrieves comprehensive SIMRS patient medical history, past admissions, chronic conditions, and historical lab panels.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "mrn": {"type": "string", "description": "SIMRS Medical Record Number (e.g. MRN-SIMRS-10492)"}
                    },
                    "required": ["mrn"]
                }
            },
            {
                "name": "simrs.get_patient_anamnesis",
                "description": "Retrieves comprehensive clinical anamnesis from SIMRS (Chief Complaint, History of Present Illness / RPS, Past Medical History / RPD, Family History / RPK, Allergy & Review of Systems).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "mrn": {"type": "string", "description": "SIMRS Medical Record Number (e.g. MRN-SIMRS-10492)"}
                    },
                    "required": ["mrn"]
                }
            },
            {
                "name": "simrs.get_patient_labs",
                "description": "Retrieves real-time and historical laboratory panels, urinalysis, and vital signs from SIMRS LIS/EMR system.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "mrn": {"type": "string", "description": "SIMRS Medical Record Number (e.g. MRN-SIMRS-10492)"}
                    },
                    "required": ["mrn"]
                }
            },
            {
                "name": "simrs.update_patient_record",
                "description": "Writes consultation notes, updated primary/secondary diagnoses, and treatment plan into SIMRS Electronic Medical Record (EMR/RME).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "mrn": {"type": "string", "description": "SIMRS Medical Record Number"},
                        "doctor_notes": {"type": "string", "description": "Clinical assessment notes from doctor/AI co-pilot"},
                        "primary_diagnosis": {"type": "string", "description": "Primary clinical diagnosis (with ICD-10 code)"},
                        "treatment_plan": {"type": "string", "description": "Recommended treatment plan & follow-up recommendations"}
                    },
                    "required": ["mrn", "doctor_notes", "primary_diagnosis", "treatment_plan"]
                }
            }
        ]

    def _find_profile(self, query: str) -> Optional[Dict[str, Any]]:
        """Helper to find patient profile by MRN, NIK, IHS, or Name."""
        if not query:
            return None
        q = str(query).strip().lower()
        if query in simrs_repo.patient_profiles:
            return simrs_repo.patient_profiles[query]
        for p in simrs_repo.patient_profiles.values():
            if (
                q == p.get("mrn", "").lower()
                or q in p.get("mrn", "").lower()
                or (p.get("nik") and q in p.get("nik", "").lower())
                or (p.get("full_name") and q in p.get("full_name", "").lower())
                or (q.startswith("p-") and q.replace("p-", "") in p.get("mrn", "").lower())
            ):
                return p
        return None

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes MCP tool call."""
        if tool_name == "simrs.get_patient_profile":
            mrn = arguments.get("mrn", "")
            profile = self._find_profile(mrn)
            if profile:
                return {"status": "success", "mrn": profile["mrn"], "profile": profile}
            return {"status": "error", "message": f"Patient MRN/NIK '{mrn}' not found in SIMRS Database"}

        elif tool_name == "simrs.get_patient_history":
            mrn = arguments.get("mrn", "")
            profile = self._find_profile(mrn)
            resolved_mrn = profile["mrn"] if profile else mrn
            history = simrs_repo.medical_histories.get(resolved_mrn)
            if not history:
                for h in simrs_repo.medical_histories.values():
                    if resolved_mrn in h["mrn"] or mrn in h["mrn"]:
                        history = h
                        break
            if history:
                return {"status": "success", "mrn": history["mrn"], "history": history}
            return {"status": "error", "message": f"Medical history for MRN '{mrn}' not found in SIMRS"}

        elif tool_name == "simrs.get_patient_anamnesis":
            mrn = arguments.get("mrn", "")
            profile = self._find_profile(mrn)
            resolved_mrn = profile["mrn"] if profile else mrn
            anamnesis = simrs_repo.patient_anamnesis.get(resolved_mrn)
            if not anamnesis:
                for a in simrs_repo.patient_anamnesis.values():
                    if resolved_mrn in a["mrn"] or mrn in a["mrn"]:
                        anamnesis = a
                        break
            if anamnesis:
                return {"status": "success", "mrn": anamnesis["mrn"], "anamnesis": anamnesis}
            return {
                "status": "not_found",
                "mrn": resolved_mrn,
                "anamnesis": None,
                "message": f"Data anamnesis untuk MRN '{mrn}' belum tersedia di SIMRS"
            }


        elif tool_name == "simrs.get_patient_labs":
            mrn = arguments.get("mrn", "")
            profile = self._find_profile(mrn)
            resolved_mrn = profile["mrn"] if profile else mrn
            history = simrs_repo.medical_histories.get(resolved_mrn) or {}
            historical_labs = history.get("historical_labs", [])
            
            if "20811" in mrn:
                detailed_labs = [
                    {"date": "2026-08-14", "test_name": "Troponin T Kuantitatif", "value": "<0.01", "unit": "ng/mL", "ref_range": "< 0.01 ng/mL", "status": "Normal (Tidak ada nekrosis miokard akut)"},
                    {"date": "2026-08-14", "test_name": "CK-MB Massa", "value": "14", "unit": "U/L", "ref_range": "< 25 U/L", "status": "Normal"},
                    {"date": "2026-08-14", "test_name": "Total Kolesterol", "value": "165", "unit": "mg/dL", "ref_range": "< 200 mg/dL", "status": "Optimal"},
                    {"date": "2026-08-14", "test_name": "LDL Kolesterol", "value": "82", "unit": "mg/dL", "ref_range": "< 55 mg/dL (Pasca PCI)", "status": "Perlu Penurunan Lebih Agresif (<55 mg/dL)"},
                    {"date": "2026-08-14", "test_name": "HDL Kolesterol", "value": "48", "unit": "mg/dL", "ref_range": "> 40 mg/dL", "status": "Normal"},
                    {"date": "2026-08-14", "test_name": "Trigliserida", "value": "135", "unit": "mg/dL", "ref_range": "< 150 mg/dL", "status": "Normal"},
                    {"date": "2026-08-14", "test_name": "SGPT (ALT)", "value": "24", "unit": "U/L", "ref_range": "< 41 U/L", "status": "Fungsi Hati Normal (Toleransi Statin Baik)"},
                    {"date": "2026-08-14", "test_name": "EKG 12-Lead", "value": "Sinus Rhythm HR 68", "unit": "bpm", "ref_range": "Normal Sinus", "status": "Iskemia Anterior Kronis Minimal (V4-V5)"}
                ]
                vital_signs = {
                    "blood_pressure": "120/78 mmHg (Terkontrol)",
                    "heart_rate": "68 bpm (Reguler)",
                    "respiratory_rate": "16 x/menit",
                    "temperature": "36.5 °C",
                    "spo2": "99% udara ruangan"
                }
            elif "30124" in mrn:
                detailed_labs = [
                    {"date": "2026-08-16", "test_name": "Hemoglobin (Hb)", "value": "10.4", "unit": "g/dL", "ref_range": "12.0 - 15.5 g/dL", "status": "Menurun (Anemia Ringan-Sedang)"},
                    {"date": "2026-08-16", "test_name": "Hematokrit (Ht)", "value": "32.1", "unit": "%", "ref_range": "37.0 - 48.0 %", "status": "Menurun"},
                    {"date": "2026-08-16", "test_name": "MCV (Mean Corpuscular Volume)", "value": "74", "unit": "fL", "ref_range": "80 - 100 fL", "status": "Mikrositik (Defisiensi Besi)"},
                    {"date": "2026-08-16", "test_name": "MCH (Mean Corpuscular Hb)", "value": "23", "unit": "pg", "ref_range": "27 - 33 pg", "status": "Hipokromik"},
                    {"date": "2026-08-16", "test_name": "Serum Ferritin", "value": "18", "unit": "ng/mL", "ref_range": "30 - 200 ng/mL", "status": "Cadangan Besi Rendah (Depleted Iron Stores)"},
                    {"date": "2026-08-16", "test_name": "Serum Iron (SI)", "value": "42", "unit": "ug/dL", "ref_range": "60 - 170 ug/dL", "status": "Besi Serum Rendah"},
                    {"date": "2026-08-16", "test_name": "TIBC", "value": "410", "unit": "ug/dL", "ref_range": "250 - 400 ug/dL", "status": "Kapasitas Ikat Besi Total Meningkat"},
                    {"date": "2026-08-16", "test_name": "Feses Rutin / Benzidine Darah Samar", "value": "Negatif (-)", "unit": "-", "ref_range": "Negatif (-)", "status": "Tidak Ada Perdarahan Saluran Cerna Aktif"}
                ]
                vital_signs = {
                    "blood_pressure": "115/75 mmHg (Normal)",
                    "heart_rate": "84 bpm (Reguler)",
                    "respiratory_rate": "18 x/menit",
                    "temperature": "36.7 °C",
                    "spo2": "99% udara ruangan"
                }
            else:
                detailed_labs = [
                    {"date": "2026-08-15", "test_name": "HbA1c", "value": "7.2", "unit": "%", "ref_range": "< 5.7%", "status": "Meningkat (Suboptimal Glycemic Control)"},
                    {"date": "2026-08-15", "test_name": "Glukosa Darah Puasa", "value": "142", "unit": "mg/dL", "ref_range": "70 - 100 mg/dL", "status": "Hiperglikemia Puasa"},
                    {"date": "2026-08-15", "test_name": "eGFR (CKD-EPI)", "value": "58", "unit": "mL/min/1.73m²", "ref_range": "> 90 mL/min", "status": "CKD Stage 3a (Penurunan Ringan-Sedang)"},
                    {"date": "2026-08-15", "test_name": "Serum Kreatinin", "value": "1.30", "unit": "mg/dL", "ref_range": "0.50 - 1.10 mg/dL", "status": "Meningkat di atas nilai normal"},
                    {"date": "2026-08-15", "test_name": "Kalium Serum (K+)", "value": "4.6", "unit": "mEq/L", "ref_range": "3.5 - 5.0 mEq/L", "status": "Normal Terkontrol (Dalam Batas Aman ACEi)"},
                    {"date": "2026-08-15", "test_name": "Natrium Serum (Na+)", "value": "139", "unit": "mEq/L", "ref_range": "135 - 145 mEq/L", "status": "Normal"},
                    {"date": "2026-08-15", "test_name": "Rasio Albumin/Kreatinin Urin (uACR)", "value": "120", "unit": "mg/g", "ref_range": "< 30 mg/g", "status": "Mikroalbuminuria (Nefropati Awal)"},
                    {"date": "2026-08-15", "test_name": "LDL Kolesterol", "value": "82", "unit": "mg/dL", "ref_range": "< 70 mg/dL", "status": "Mendekati Target (Statin Terkontrol)"}
                ]
                vital_signs = {
                    "blood_pressure": "140/90 mmHg (Stage 1 HT)",
                    "heart_rate": "78 bpm (Reguler)",
                    "respiratory_rate": "18 x/menit",
                    "temperature": "36.6 °C",
                    "spo2": "98% udara ruangan"
                }

            return {
                "status": "success",
                "mrn": mrn,
                "latest_labs": detailed_labs,
                "historical_labs": historical_labs,
                "vital_signs": vital_signs
            }

        elif tool_name == "simrs.update_patient_record":
            mrn = arguments.get("mrn", "")
            notes = arguments.get("doctor_notes", "")
            diag = arguments.get("primary_diagnosis", "")
            plan = arguments.get("treatment_plan", "")
            
            log_id = f"SIMRS-LOG-00{len(simrs_repo.emr_consultation_logs)+1}"
            entry = {
                "log_id": log_id,
                "timestamp": datetime.now().isoformat(),
                "mrn": mrn,
                "doctor_name": "Dr. Sarah Jenkins, Sp.PD (AI Co-Pilot Synced)",
                "primary_diagnosis": diag,
                "doctor_notes": notes,
                "treatment_plan": plan,
                "synced_status": "Committed to RME SIMRS via MCP"
            }
            simrs_repo.emr_consultation_logs.insert(0, entry)
            return {
                "status": "success",
                "log_id": log_id,
                "mrn": mrn,
                "message": f"Record updated successfully in SIMRS EMR system for {mrn}",
                "timestamp": entry["timestamp"]
            }

        else:
            return {"status": "error", "message": f"Unknown MCP Tool '{tool_name}'"}


simrs_mcp_server = SIMRSMCPServer()
