"""
Pre-loaded Medical Knowledge Base for Dedicated Qdrant Vector RAG Service.
Contains disease monographs, pharmacotherapy guidelines, and laboratory diagnostic definitions.
"""
from datetime import datetime
from typing import List, Dict, Any

INITIAL_KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "id": "kb-dis-001",
        "title": "Type 2 Diabetes Mellitus with CKD Stage 3a & Diabetic Neuropathy",
        "category": "disease",
        "specialty": "Endocrinology / Nephrology",
        "icd10_code": "E11.22 / N18.31 / I10 / E11.21 / E53.8",
        "rxnorm_code": None,
        "loinc_code": None,
        "synonyms": ["Type 2 Diabetes", "T2D with CKD", "Diabetic Kidney Disease", "Diabetic Nephropathy", "Diabetic Peripheral Neuropathy", "Primary Essential Hypertension", "Hipertensi Primer", "Nefropati Diabetik"],
        "keywords": ["dm tipe 2", "ckd stage 3a", "diabetic neuropathy", "mikroalbuminuria", "uacr", "egfr", "hba1c", "metformin", "lisinopril", "empagliflozin", "kesemutan ujung kaki", "hipertensi primer", "e11.22", "n18.31", "i10", "e11.21", "e53.8", "m54.16"],
        "evidence_level": "ADA Standards of Care 2025 & KDIGO 2024 (Level A)",
        "created_at": datetime.now().isoformat(),
        "content": """
### Definisi & Patofisiologi
DM Tipe 2 merupakan gangguan metabolik progresif akibat resistensi insulin perifer dan disfungsi sekresi sel beta pankreas. Hiperglikemia kronis memicu akumulasi Advanced Glycation End-products (AGEs), stres oksidatif, dan disfungsi endotel mikrovaskular ginjal (glomerulosklerosis nodular Kimmelstiel-Wilson) yang menyebabkan mikroalbuminuria persisten (uACR 30-300 mg/g) dan penurunan laju filtrasi glomerulus (eGFR 45-59 mL/min/1.73m²), serta polineuropati perifer simetris pada serabut saraf sensorik distal.

### Kriteria Diagnosis Baku
1. Glycated Hemoglobin (HbA1c) ≥ 6.5% (48 mmol/mol) atau Glukosa Darah Puasa (GDP) ≥ 126 mg/dL.
2. Penurunan laju filtrasi glomerulus persisten: eGFR 45–59 mL/min/1.73m² selama > 3 bulan (CKD Stage 3a).
3. Urin Albumin-to-Creatinine Ratio (uACR) 30–300 mg/g (Mikroalbuminuria).
4. Manifestasi Polineuropati Distal: Parestesia, rasa kesemutan, baal, dan rasa terbakar pada kedua ujung kaki secara simetris (*stocking-glove distribution*).

### Tahapan & Stadium Klinis
CKD Stage G3aA2 (Moderate Risk / Early Diabetic Kidney Disease dengan Komplikasi Neuropati Perifer).

### Komplikasi Klinis Utama
1. Progresi ke End-Stage Renal Disease (ESRD) yang memerlukan terapi pengganti ginjal (hemodialisis).
2. Diabetic Foot Ulcer (Ulkus Kaki Diabetik) dengan risiko osteomielitis dan amputasi ekstremitas bawah.
3. Penyakit Kardiovaskular Mayor (MACE: Infark Miokard Akut, Stroke Iskemik, Gagal Jantung).

### Rekomendasi Diagnosis Primer
- Type 2 Diabetes Mellitus with Diabetic Peripheral Neuropathy & CKD Stage 3a (ICD-10: E11.22 / N18.31) | Confidence: High (92%) | Justifikasi: GDS 142 mg/dL, HbA1c 7.2%, eGFR 58 mL/min/1.73m², mikroalbuminuria uACR 120 mg/g, dan nokturia/kesemutan perifer simetris.
- Primary Essential Hypertension Stage 1 (ICD-10: I10) | Confidence: High (95%) | Justifikasi: Tekanan darah serial 140/90 mmHg pada pasien riwayat hipertensi kronis dalam terapi Lisinopril.

### Diagnosis Banding & ICD-10
- Diabetic Nephropathy Stage III (Incipient) (ICD-10: E11.21) | Petunjuk Klinis: Adanya mikroalbuminuria persisten dengan uACR 120 mg/g.
- Vitamin B12 Deficiency / Lumbosacral Radiculopathy (ICD-10: E53.8 / M54.16) | Petunjuk Klinis: Dapat berkontribusi pada gejala kesemutan distal jika konsumsi Metformin jangka panjang.

### Rencana Pemeriksaan Penunjang (Workups)
- Pemeriksaan HbA1c serial per 3 bulan
- Panel Fungsi Ginjal: Serum Kreatinin, eGFR, dan Elektrolit (K+, Na+)
- Rasio Albumin-Kreatinin Urin (uACR) sewaktu kuantitatif
- Skrining Komplikasi Mikrovaskular: Funduskopi retina & tes monofilamen kaki berkala

### Kodefikasi ICD-10 Terkait
- E11.22 (Type 2 diabetes mellitus with diabetic chronic kidney disease)
- N18.31 (Chronic kidney disease, stage 3a)
- I10 (Essential primary hypertension)
- E11.21 (Type 2 diabetes mellitus with diabetic nephropathy)
- E53.8 (Deficiency of other specified B group vitamins)
- M54.16 (Radiculopathy, lumbar region)

### Rekomendasi Terapi Obat & Panduan Dosis
- Metformin 1000mg | Kelas: Biguanide | Panduan Dosis: 1000mg BID (2x sehari) bersama makanan | Penyesuaian Ginjal: Aman pada eGFR 45-59 mL/min (CKD 3a). Dosis maksimal 1000mg/hari jika eGFR 30-44 mL/min. Hentikan jika eGFR < 30. | Indikasi: Kontrol glikemik lini pertama
- Lisinopril 20mg | Kelas: ACE Inhibitor (Renoprotective) | Panduan Dosis: 20mg 1x1 tablet per hari pagi | Penyesuaian Ginjal: Renoprotektif pada mikroalbuminuria. Pantau kadar Kalium Serum & Kreatinin serial. | Indikasi: Antihipertensi & reduksi progresi nefropati diabetik
- Atorvastatin 40mg | Kelas: Statin Lipid-Lowering | Panduan Dosis: 40mg 1x1 tablet malam hari | Penyesuaian Ginjal: Tidak memerlukan penyesuaian dosis pada gangguan ginjal | Indikasi: Previnsi sekunder kardiovaskular

### Kontraindikasi Obat & Peringatan
- NSAID (potensi nefrotoksisitas akut)
- Kontras radiologi berlebih

### Titik Pemantauan Terapi (Monitoring Points)
- Ulangi lab fungsi ginjal BMP (eGFR, Kalium) dalam 3 bulan
- Pantau uACR berkala

### Tanda Bahaya Klinis & Kriteria Kegawatdaruratan (Red Flags)
- Alert: Krisis Hipertensi & Ensefalopati Hipertensif | Tingkat Keparahan: High | Kriteria Pemicu: Tekanan Darah > 180/120 mmHg disertai nyeri kepala hebat, pandangan kabur, atau penurunan kesadaran | Tindakan Darurat: Pemberian antihipertensi parenteral terkontrol di ruang rawat intensif
- Alert: Progresi Penyakit Ginjal Akut pada Kronis (AKI on CKD) | Tingkat Keparahan: High | Kriteria Pemicu: Oliguria (< 400 mL/24 jam), edema anasarka, atau hiperkalemia berat (> 6.0 mEq/L) | Tindakan Darurat: Evaluasi elektrolit cito, EKG monitoring, dan konsultasi nefrologi untuk koreksi cairan/elektrolit
- Alert: Hipoglikemia Berat Akut / Ketoasidosis Diabetik | Tingkat Keparahan: Critical | Kriteria Pemicu: Glukosa darah sewaktu < 54 mg/dL disertai keringat dingin, tremor, penurunan kesadaran, atau dehidrasi berat dengan pernapasan Kussmaul | Tindakan Darurat: Pemberian Bolus Dekstrosa 40% (D40) intravena atau resusitasi cairan kristaloid segera di IGD

### Protokol Terapi Berbasis Bukti
1. Kontrol Glikemik Lini Pertama: Metformin 1000 mg BID (dosis aman pada eGFR 45-59 mL/min; batasi 1000 mg/hari jika eGFR 30-44 mL/min).
2. Proteksi Kardiorenal: SGLT2 Inhibitor (Empagliflozin 10 mg OD) dan ACE Inhibitor (Lisinopril 20 mg OD) atau ARB (Losartan 50 mg OD) untuk supresi proteinuria.
3. Pengendalian Dislipidemia & Target Tekanan Darah: Statin intensitas sedang-tinggi (Atorvastatin 40 mg OD) dengan target tekanan darah < 130/80 mmHg.
"""
    },
    {
        "id": "kb-dis-002",
        "title": "Chronic Kidney Disease (CKD)",
        "category": "disease",
        "specialty": "Nephrology",
        "icd10_code": "N18.9",
        "rxnorm_code": None,
        "loinc_code": None,
        "synonyms": ["CKD", "Chronic Renal Failure", "Renal Impairment", "Chronic Kidney Failure"],
        "keywords": ["eGFR", "serum creatinine", "albuminuria", "KDIGO", "SGLT2 inhibitor", "Lisinopril", "nephroprotection"],
        "evidence_level": "KDIGO 2024 Clinical Practice Guideline",
        "created_at": datetime.now().isoformat(),
        "content": """
### Staging & Definition
Chronic Kidney Disease (CKD) is defined as abnormalities of kidney structure or function present for > 3 months.
- Stage 1: eGFR ≥ 90 mL/min/1.73m² with persistent kidney damage.
- Stage 2: eGFR 60–89 mL/min/1.73m².
- Stage 3a: eGFR 45–59 mL/min/1.73m² (Mild-to-moderate decline).
- Stage 3b: eGFR 30–44 mL/min/1.73m² (Moderate-to-severe decline).
- Stage 4: eGFR 15–29 mL/min/1.73m² (Severe decline).
- Stage 5: eGFR < 15 mL/min/1.73m² (Kidney Failure / End-Stage Renal Disease).

### Tanda Bahaya Klinis & Kriteria Kegawatdaruratan (Red Flags)
- Alert: Ensefalopati Uremikum & Perikarditis Uremik | Tingkat Keparahan: Critical | Kriteria Pemicu: Letargi, asteriksis, kebingungan mental, atau pericardial friction rub pada pasien CKD lanjut | Tindakan Darurat: Rujukan CITO untuk inisiasi Hemodialisis darurat (Emergent Dialysis)
- Alert: Hiperkalemia Berat Aritmogenik (K+ > 6.5 mEq/L) | Tingkat Keparahan: Critical | Kriteria Pemicu: Kadar kalium darah > 6.5 mEq/L dengan perubahan EKG gelombang T tinggi lancip (peaked T waves) atau pelebaran QRS | Tindakan Darurat: Kalsium Glukonat 10% IV, Insulin + Dekstrosa 40%, Nebulisasi Salbutamol, dan Diuretik Loop / Dialisis

### Evidence-Based Treatment Protocols
1. Renin-Angiotensin System Inhibition: ACE inhibitors (Lisinopril) or ARBs (Losartan) in diabetic/hypertensive patients with UACR ≥ 30 mg/g.
2. SGLT2 Inhibitor Therapy: Recommended for patients with eGFR ≥ 20 mL/min/1.73m² and UACR ≥ 200 mg/g to delay CKD progression.
3. Electrolyte Monitoring: Monitor serum potassium (K+) and creatinine within 2–4 weeks of initiating ACEi/ARB therapy.
"""
    },
    {
        "id": "kb-dis-003",
        "title": "Essential Hypertension (HTN)",
        "category": "disease",
        "specialty": "Cardiology",
        "icd10_code": "I10",
        "rxnorm_code": None,
        "loinc_code": None,
        "synonyms": ["HTN", "High Blood Pressure", "Primary Hypertension", "Essential HTN"],
        "keywords": ["systolic BP", "diastolic BP", "ACC/AHA", "ACE inhibitor", "thiazide", "calcium channel blocker", "amlodipine"],
        "evidence_level": "ACC/AHA 2024 Hypertension Guidelines",
        "created_at": datetime.now().isoformat(),
        "content": """
### Diagnostic Classification
- Normal BP: < 120/80 mmHg.
- Elevated BP: Systolic 120–129 AND Diastolic < 80 mmHg.
- Stage 1 HTN: Systolic 130–139 OR Diastolic 80–89 mmHg.
- Stage 2 HTN: Systolic ≥ 140 OR Diastolic ≥ 90 mmHg.

### Tanda Bahaya Klinis & Kriteria Kegawatdaruratan (Red Flags)
- Alert: Krisis Hipertensi Emergensi dengan Kerusakan Organ Target Akut | Tingkat Keparahan: Critical | Kriteria Pemicu: Tekanan darah > 180/120 mmHg disertai papiledema, nyeri dada akut, atau sesak napas akut | Tindakan Darurat: Titrasi obat antihipertensi intravena (Nicardipine / Nitroprusside) di ICU dengan target penurunan MAP 20-25% dalam 1 jam pertama
- Alert: Stroke Iskemik Akut / Pendarahan Intraserebral | Tingkat Keparahan: Critical | Kriteria Pemicu: Defisit neurologis fokal akut tiba-tiba (kelemahan satu sisi tubuh, bicara pelo, asimetri wajah) | Tindakan Darurat: Aktivasi Code Stroke, Head CT-Scan cito, dan konsultasi Neurologi emergensi

### Pharmacotherapy Guidelines
- Target BP Goal: < 130/80 mmHg for high ASCVD risk, diabetes, or CKD.
- First-Line Drug Classes: Thiazide Diuretics (Chlorthalidone), CCBs (Amlodipine), and ACEi (Lisinopril) / ARBs (Valsartan).
"""
    },
    {
        "id": "kb-dis-004",
        "title": "Acute Coronary Syndrome (ACS)",
        "category": "disease",
        "specialty": "Cardiology",
        "icd10_code": "I24.9",
        "rxnorm_code": None,
        "loinc_code": None,
        "synonyms": ["ACS", "Myocardial Infarction", "Heart Attack", "STEMI", "NSTEMI", "Unstable Angina"],
        "keywords": ["cardiac troponin T", "DAPT", "clopidogrel", "aspirin", "coronary stent", "ischemia", "chest pain"],
        "evidence_level": "ESC/ACC ACS Guidelines",
        "created_at": datetime.now().isoformat(),
        "content": """
### Clinical Spectrum & Diagnostics
Encompasses STEMI, NSTEMI, and Unstable Angina. Evaluate with serial high-sensitivity Cardiac Troponin (hs-cTnI / hs-cTnT) and 12-lead ECG.

### Tanda Bahaya Klinis & Kriteria Kegawatdaruratan (Red Flags)
- Alert: Infark Miokard Akut Luas / Aritmia Ventrikel Letal | Tingkat Keparahan: Critical | Kriteria Pemicu: Nyeri dada retrosternal berat > 20 menit disertai elevasi segmen ST, Takikardia Ventrikel (VT), atau Fibrilasi Ventrikel (VF) | Tindakan Darurat: Aktivasi Code STEMI, Primary PCI emergensi dalam waktu < 90 menit, Defibrilasi bila irama shockable
- Alert: Syok Kardiogenik Akut | Tingkat Keparahan: Critical | Kriteria Pemicu: Hipotensi persisten (TDS < 90 mmHg), oliguria, akral dingin basah, dan laktat darah meningkat | Tindakan Darurat: Support inotropik/vasopresor, monitoring hemodinamik invasif, dan revaskularisasi emergensi

### Acute Pharmacologic Management
1. Aspirin: 162–325 mg chewed immediately.
2. P2Y12 Inhibitor (DAPT): Clopidogrel (300–600 mg load) or Ticagrelor (180 mg load).
3. Post-PCI DAPT Duration: 12 months minimum post-stent placement.
"""
    },

    {
        "id": "kb-med-001",
        "title": "Metformin (Biguanide Antidiabetic)",
        "category": "medicine",
        "specialty": "Pharmacology",
        "icd10_code": None,
        "rxnorm_code": "6809",
        "loinc_code": None,
        "synonyms": ["Glucophage", "Metformin Hydrochloride", "Fortamet", "Glumetza"],
        "keywords": ["biguanide", "eGFR cutoff", "lactic acidosis", "hepatic gluconeogenesis", "t2d first-line", "vitamin b12"],
        "evidence_level": "FDA Prescribing Information & ADA 2025",
        "created_at": datetime.now().isoformat(),
        "content": """
### Mechanism & Renal Dosing Cutoffs (eGFR)
Metformin decreases hepatic gluconeogenesis and improves insulin sensitivity.
- eGFR ≥ 60 mL/min: Full therapeutic dose (up to 2000 mg/day).
- eGFR 45–59 mL/min: Safe to continue full dose; monitor renal function every 3–6 months.
- eGFR 30–44 mL/min: Max dose 1000 mg/day; do NOT initiate in new patients.
- eGFR < 30 mL/min: Absolute CONTRAINDICATION due to risk of fatal Lactic Acidosis. Hold 48 hours prior to radiocontrast procedures.
"""
    },
    {
        "id": "kb-med-002",
        "title": "Lisinopril (ACE Inhibitor)",
        "category": "medicine",
        "specialty": "Pharmacology",
        "icd10_code": None,
        "rxnorm_code": "29046",
        "loinc_code": None,
        "synonyms": ["Zestril", "Prinivil", "ACE Inhibitor", "Lisinopril-Hydrochlorothiazide"],
        "keywords": ["angiotensin converting enzyme inhibitor", "hyperkalemia", "serum potassium", "diabetic nephropathy", "dry cough", "angioedema"],
        "evidence_level": "FDA Prescribing Information & KDIGO 2024",
        "created_at": datetime.now().isoformat(),
        "content": """
### Indications & Monitoring
Inhibits ACE, decreasing Angiotensin II. Indicated for Hypertension, Heart Failure, and Diabetic Nephropathy.
- Hyperkalemia Risk: Monitor serum potassium (K+). Avoid co-administration with potassium-sparing diuretics (Spironolactone) without monitoring.
- Serum Creatinine: Up to 30% rise upon initiation is acceptable due to efferent arteriole dilation.
- Dry Cough: Switch to ARB (Losartan) if intolerable.
"""
    },
    {
        "id": "kb-med-003",
        "title": "Clopidogrel (P2Y12 Antiplatelet Agent)",
        "category": "medicine",
        "specialty": "Pharmacology",
        "icd10_code": None,
        "rxnorm_code": "32968",
        "loinc_code": None,
        "synonyms": ["Plavix", "P2Y12 Inhibitor", "Antiplatelet Agent"],
        "keywords": ["prodrug", "CYP2C19", "omeprazole interaction", "stent thrombosis", "bleeding risk", "dapt"],
        "evidence_level": "FDA Boxed Warning & ACC/AHA DAPT Guidelines",
        "created_at": datetime.now().isoformat(),
        "content": """
### Mechanism & Drug Interactions
Oral prodrug requiring CYP2C19 activation to irreversibly inhibit platelet P2Y12 receptors.
- Omeprazole Interaction: Omeprazole inhibits CYP2C19, reducing Clopidogrel active metabolite and raising stent thrombosis risk. Use Pantoprazole or Famotidine alternative.
- Hold 5 days prior to major elective surgery (CABG).
"""
    },
    {
        "id": "kb-term-001",
        "title": "Estimated Glomerular Filtration Rate (eGFR)",
        "category": "terminology",
        "specialty": "Nephrology / Lab Diagnostics",
        "icd10_code": None,
        "rxnorm_code": None,
        "loinc_code": "33914-3",
        "synonyms": ["eGFR", "Glomerular Filtration Rate", "Calculated GFR", "CKD-EPI equation"],
        "keywords": ["serum creatinine", "renal clearance", "kidney staging", "drug dosage adjustment", "renal function"],
        "evidence_level": "National Kidney Foundation (NKF)",
        "created_at": datetime.now().isoformat(),
        "content": """
### Interpretation & Cutoffs
Measures blood filtration rate (mL/min/1.73m²) calculated via CKD-EPI equation based on serum creatinine, age, and sex.
- Normal: > 90 mL/min/1.73m²
- Mild Decline: 60–89 mL/min/1.73m²
- Moderate Decline: 30–59 mL/min/1.73m² (Triggers drug renal dose adjustment)
- Severe Decline: < 30 mL/min/1.73m² (Triggers drug cutoffs)
"""
    },
    {
        "id": "kb-term-002",
        "title": "Glycated Hemoglobin (HbA1c)",
        "category": "terminology",
        "specialty": "Endocrinology / Lab Diagnostics",
        "icd10_code": None,
        "rxnorm_code": None,
        "loinc_code": "4548-4",
        "synonyms": ["HbA1c", "A1C", "Glycohemoglobin", "Hemoglobin A1c"],
        "keywords": ["average blood glucose", "glycemic control", "erythrocyte lifespan", "diabetes diagnostic threshold"],
        "evidence_level": "ADA Standards of Medical Care",
        "created_at": datetime.now().isoformat(),
        "content": """
### Diagnostic Cutoffs
Reflects 2-3 month average blood glucose (erythrocyte 120-day lifespan).
- Normal: < 5.7%
- Prediabetes: 5.7% – 6.4%
- Diabetes Mellitus: ≥ 6.5%
- Standard Goal: < 7.0% (estimated Average Glucose ~154 mg/dL).
"""
    },
    {
        "id": "kb-term-003",
        "title": "High Anion Gap Metabolic Acidosis (HAGMA)",
        "category": "terminology",
        "specialty": "Critical Care / Nephrology",
        "icd10_code": None,
        "rxnorm_code": None,
        "loinc_code": "1863-7",
        "synonyms": ["HAGMA", "Anion Gap Acidosis", "Metabolic Acidosis", "High Anion Gap"],
        "keywords": ["bicarbonate", "sodium", "chloride", "MUDPILES", "lactic acidosis", "ketoacidosis", "metformin toxicity"],
        "evidence_level": "UpToDate Clinical Consensus",
        "created_at": datetime.now().isoformat(),
        "content": """
### Formula & Etiology
Anion Gap = [Na+] - ([Cl-] + [HCO3-]). Normal range: 8–12 mEq/L. High Anion Gap > 12 mEq/L.
Differential Causes (MUDPILES): Lactic Acidosis (Metformin, sepsis), Ketoacidosis (DKA), Uremia (Renal Failure), Toxic Ingestions (Methanol, Salicylates).
"""
    },
    {
        "id": "kb-dis-005",
        "title": "Gastritis Kronis Erosif & Anemia Defisiensi Besi",
        "category": "disease",
        "specialty": "Gastroenterology",
        "icd10_code": "K29.1 / K30 / D50.9 / K25.9 / B96.81",
        "rxnorm_code": None,
        "loinc_code": None,
        "synonyms": ["Gastritis Kronis Erosif", "Erosive Gastritis", "Dispepsia Fungsional", "Ulkus Peptikum", "Gastric Erosion & Iron Deficiency Anemia", "Anemia Defisiensi Besi", "Helicobacter pylori Gastropathy"],
        "keywords": ["gastritis erosif", "anemia defisiensi besi", "nyeri ulu hati", "epigastrik", "mual muntah", "omeprazole", "sukralfat", "ferrous fumarate", "gastroprotektor", "asam lambung", "h. pylori", "perdarahan saluran cerna", "k29.1", "d50.9", "k30", "k25.9", "b96.81"],
        "evidence_level": "Konsensus Nasional Penatalaksanaan Dispepsia & PGI 2024",
        "created_at": datetime.now().isoformat(),
        "content": """
### Definisi & Patofisiologi
Gastritis erosif ditandai oleh kerusakan epitel mukosa gaster akibat ketidakseimbangan antara faktor agresif (asam lambung, pepsin, NSAID) dan faktor defensif mukosa (lendir, bikarbonat, prostaglandin). Kehilangan darah mikroskopis kronis dari erosi mukosa yang berlangsung lama menyebabkan deplesi cadangan besi tubuh (Serum Ferritin rendah) dan berkembang menjadi Anemia Defisiensi Besi mikrositik hipokromik.

### Kriteria Diagnosis Baku
1. Nyeri atau rasa terbakar di ulu hati (epigastrium) yang berkaitan dengan waktu makan, rasa cepat kenyang, kembung, dan mual.
2. Temuan Endoskopi SCBA (EGD): Eritema difus dan erosi mukosa superfisial gaster tanpa ulkus dalam.
3. Evaluasi Laboratorium: Hemoglobin rendah (Hb < 12-13 g/dL), MCV < 80 fL (mikrositik), MCH < 27 pg (hipokrom), dan Serum Ferritin < 30 ng/mL.

### Tahapan & Stadium Klinis
Gastritis Kronis Derajat Ringan-Sedang dengan Anemia Sekunder Ringan (Hb > 10 g/dL).

### Komplikasi Klinis Utama
1. Ulkus Peptikum Gaster / Duodeni dengan risiko perforasi dan striktur.
2. Perdarahan Saluran Cerna Atas Akut (Hematemesis / Melena).
3. Deplesi Cadangan Besi Berat dan Anemia Simtomatik Kronis.

### Rekomendasi Diagnosis Primer
- Gastritis Kronis Erosif & Dispepsia Fungsional (ICD-10: K29.1 / K30) | Confidence: High (94%) | Justifikasi: Nyeri epigastrium perih terbakar memberat pasca makan, mual, riwayat konsumsi analgetik bebas, dan riwayat gastritis erosif.
- Anemia Defisiensi Besi Mikrositik Hipokromik (ICD-10: D50.9) | Confidence: High (91%) | Justifikasi: Hemoglobin 10.4 g/dL, MCV 74 fL (mikrositik), Serum Ferritin 18 ng/mL (cadangan besi menurun), dan pusing/lemas.

### Diagnosis Banding & ICD-10
- Peptic Ulcer Disease (Ulkus Gaster / Duodeni) (ICD-10: K25.9 / K26.9) | Petunjuk Klinis: Waspadai tanda ulserasi mukosa jika nyeri menetap atau terjadi melena/hematemesis.
- Helicobacter pylori-associated Gastropathy (ICD-10: B96.81) | Petunjuk Klinis: Dapat dievaluasi melalui tes urea breath test (UBT) atau biopsi histopatologi.

### Rencana Pemeriksaan Penunjang (Workups)
- Pemeriksaan Darah Lengkap (CBC) & Indeks Eritrosit (MCV, MCH, RDW)
- Profil Besi Serum: Serum Ferritin, Serum Iron (SI), Total Iron Binding Capacity (TIBC)
- Urea Breath Test (UBT) / H. pylori Stool Antigen Test
- Evaluasi Endoskopi Saluran Cerna Atas (EGD) ulang bila gejala tidak merespons terapi PPI 4-8 minggu

### Kodefikasi ICD-10 Terkait
- K29.1 (Other acute gastritis / erosive gastritis)
- D50.9 (Iron deficiency anemia, unspecified)
- K30 (Functional dyspepsia)
- K25.9 (Gastric ulcer, unspecified)
- B96.81 (Helicobacter pylori as the cause of diseases classified elsewhere)

### Rekomendasi Terapi Obat & Panduan Dosis
- Omeprazole 20mg | Kelas: Proton Pump Inhibitor (PPI) | Panduan Dosis: 20mg BID (2x sehari) diminum 30-60 menit sebelum makan pagi & malam selama 14-28 hari | Penyesuaian Ginjal: Tidak memerlukan penyesuaian dosis pada gangguan ginjal | Indikasi: Supresi sekresi asam lambung & penyembuhan mukosa erosif
- Sukralfat Suspensi 500mg/5mL | Kelas: Mucosal Protective Agent | Panduan Dosis: 500mg/5mL 3x1 sendok makan (15 mL) saat perut kosong (1 jam sebelum makan) | Penyesuaian Ginjal: Gunakan hati-hati pada CKD lanjut (risiko akumulasi aluminium) | Indikasi: Pelindung sawar mukosa gaster terhadap asam dan pepsin
- Ferrous Fumarate / Sulfas Ferosus 300mg | Kelas: Oral Iron Supplementation | Panduan Dosis: 300mg 1x1 tablet per hari setelah makan, berikan jeda minimal 2 jam dari antasida/sukralfat | Penyesuaian Ginjal: Aman pada gangguan ginjal, pantau profil besi serial | Indikasi: Koreksi cadangan besi pada Anemia Defisiensi Besi

### Kontraindikasi Obat & Peringatan
- NSAID (Ketorolac, Asam Mefenamat, Ibuprofen)
- Aspirin dosis tinggi

### Titik Pemantauan Terapi (Monitoring Points)
- Evaluasi perbaikan keluhan dispepsia setelah 2 minggu
- Pemeriksaan serial Hb & Ferritin dalam 4-8 minggu

### Tanda Bahaya Klinis & Kriteria Kegawatdaruratan (Red Flags)
- Alert: Tanda Perdarahan Saluran Cerna Akut (Hematemesis / Melena) | Tingkat Keparahan: Critical | Kriteria Pemicu: Muntah darah kehitaman seperti bubuk kopi atau buang air besar hitam pekat | Tindakan Darurat: Segera rujuk ke IGD untuk resusitasi cairan, NGT dekompresi, dan injeksi PPI intravena dosis tinggi
- Alert: Anemia Simtomatik Berat & Instabilitas Hemodinamik | Tingkat Keparahan: High | Kriteria Pemicu: Hb < 8 g/dL atau penurunan drastis disertai pusing ortostatik berat, sinkop, atau takikardia | Tindakan Darurat: Evaluasi kebutuhan transfusi Packed Red Cells (PRC) dan pelacakan sumber perdarahan

### Protokol Terapi Berbasis Bukti
1. Supresi Asam Lambung: Proton Pump Inhibitor (Omeprazole 20-40mg PO BID) diminum 30-60 menit sebelum makan pagi & malam.
2. Perlindungan Sawar Mukosa: Sukralfat suspensi 500mg/5mL (3x15 mL saat perut kosong).
3. Suplementasi Zat Besi: Ferrous Fumarate / Sulfas Ferosus 300mg 1x1 setelah makan (jeda minimal 2 jam dari sukralfat).
4. Tata Laksana Non-Farmakologi: Pola makan teratur porsi kecil sering, hindari makanan pedas, asam, kafein, dan obat NSAID.
"""
    },
    {
        "id": "kb-dis-006",
        "title": "Anemia Defisiensi Besi (Iron Deficiency Anemia)",
        "category": "disease",
        "specialty": "Hematology",
        "icd10_code": "D50.9",
        "rxnorm_code": None,
        "loinc_code": None,
        "synonyms": ["Anemia Defisiensi Besi", "Iron Deficiency Anemia", "IDA", "Anemia Mikrositik Hipokrom"],
        "keywords": ["anemia", "ferritin rendah", "serum iron", "TIBC", "sulfas ferosus", "ferrous fumarate", "besi elemental", "lemas pucat", "perdarahan mikroskopis"],
        "evidence_level": "ASH & WHO Iron Deficiency Guidelines",
        "created_at": datetime.now().isoformat(),
        "content": """
### Patofisiologi & Kriteria Diagnostik
Anemia Defisiensi Besi terjadi akibat ketidakseimbangan antara asupan zat besi, penyerapan usus, dan kehilangan darah kronis (misalnya perdarahan mikroerosif saluran cerna pada gastritis kronis atau menoragia).
1. Parameter Laboratorium Karakteristik:
   - Hemoglobin: < 12 g/dL (wanita) atau < 13 g/dL (pria).
   - Indeks Eritrosit: MCV < 80 fL (mikrositik) dan MCH < 27 pg (hipokrom).
   - Profil Besi Serial: Serum Ferritin < 30 ng/mL (penanda spesifik penurunan cadangan besi), Serum Iron rendah, TIBC meningkat > 400 mcg/dL, dan Saturasi Transferin < 16%.

### Tanda Bahaya Klinis & Kriteria Kegawatdaruratan (Red Flags)
- Alert: Anemia Gravis dengan Gagal Jantung Output Tinggi (High-Output Heart Failure) | Tingkat Keparahan: High | Kriteria Pemicu: Hb < 7 g/dL disertai sesak napas berat saat istirahat, takikardia menetap, atau edema perifer | Tindakan Darurat: Transfusi Packed Red Cells (PRC) bertahap dengan premedikasi Furosemide intravena
- Alert: Sinkop Hipoksia Jaringan & Penurunan Perfusi Serebral | Tingkat Keparahan: High | Kriteria Pemicu: Hilang kesadaran tiba-tiba saat perubahan posisi tubuh disertai pucat ekstrem | Tindakan Darurat: Posisikan Trendelenburg, terapi oksigenasi, dan resusitasi cairan kristaloid

### Protokol Terapi & Suplementasi Besi
1. Suplementasi Besi Oral Lini Pertama: Ferrous Fumarate atau Sulfas Ferosus (dosis setara 100-200 mg besi elemental per hari) diminum 1-2x per hari setelah makan.
2. Edukasi Absorpsi: Minum suplemen bersama sumber Vitamin C (Jus jeruk / Asam askorbat) untuk meningkatkan absorpsi besi Fe2+.
3. PENTING (Jeda Pemberian Obat): Berikan jeda minimal 2 jam dari konsumsi antasida, sukralfat, produk kalsium/susu, teh, dan kopi karena dapat mengikat zat besi dan menghambat bioavailabilitas.
4. Pemantauan Terapi: Kenaikan Hb diharapkan 1-2 g/dL per bulan. Lanjutkan suplementasi hingga 3 bulan setelah Hb normal untuk mengisi ulang cadangan Ferritin.
"""
    },
    {
        "id": "kb-dis-007",
        "title": "Chronic Coronary Syndrome (CAD Post-PCI LAD)",
        "category": "disease",
        "specialty": "Cardiology",
        "icd10_code": "I20.8 / I25.10 / Z95.5 / T82.855A / K21.9 / E78.5",
        "rxnorm_code": None,
        "loinc_code": None,
        "synonyms": ["Chronic Coronary Syndrome", "CCS", "CAD Post-PCI", "Penyakit Jantung Koroner", "Stable Angina Pectoris LAD", "Angina Pectoris Stabil", "In-stent Restenosis", "GERD / Spasme Esofagus"],
        "keywords": ["cad post pci lad", "angina stabil", "clopidogrel", "bisoprolol", "atorvastatin", "rosuvastatin", "isdn", "stent thrombosis", "target ldl < 55", "i20.8", "i25.10", "t82.855a", "k21.9", "e78.5", "z95.5"],
        "evidence_level": "ESC 2024 Guidelines on Chronic Coronary Syndromes & PERKI",
        "created_at": datetime.now().isoformat(),
        "content": """
### Definisi & Patofisiologi
Sindrom Koroner Kronis (CCS) mencerminkan ketidaksesuaian antara suplai oksigen miokardium dan kebutuhan metabolik jantung akibat aterosklerosis koroner atau stenosis residual. Pada pasien pasca pemasangan stent (DES) pada arteri koroner utama (LAD), kepatuhan terapi antiplatelet ganda (DAPT) dan statin intensitas tinggi esensial untuk mencegah trombosis stent akut atau restenosis intraintima.

### Kriteria Diagnosis Baku
1. Angina pektoris stabil yang dapat diprediksi saat aktivitas fisik atau stres emosional (Canadian Cardiovascular Society Class II).
2. Riwayat Percutaneous Coronary Intervention (PCI) dengan Drug-Eluting Stent (DES) pada Left Anterior Descending (LAD) artery.
3. Pemeriksaan Penunjang Non-Invasif: EKG serial iskemia (gelombang T inversi / depresi ST) dan profil lipid serial.

### Tahapan & Stadium Klinis
CAD Stable Angina Pectoris (Canadian Cardiovascular Society Class II Post-PCI LAD).

### Komplikasi Klinis Utama
1. Trombosis Stent Akut / Subakut pasca-PCI.
2. Infark Miokard Akut (STEMI / NSTEMI).
3. Gagal Jantung Iskemik (Ischemic Cardiomyopathy / HFrEF).
4. Aritmia Ventrikel Letal (Ventricular Tachycardia / Fibrillation).

### Rekomendasi Diagnosis Primer
- Angina Pectoris Stabil (CAD Post-PCI LAD CCS Class II) (ICD-10: I20.8) | Confidence: High (89%) | Justifikasi: Rasa tidak nyaman di dada saat aktivitas menaiki tangga yang mereda dengan istirahat pada pasien riwayat PCI DES LAD.

### Diagnosis Banding & ICD-10
- In-stent Restenosis / De Novo Coronary Lesion (ICD-10: T82.855A / I25.10) | Petunjuk Klinis: Iskemia berulang pasca intervensi koroner perkutan.
- Gastroesophageal Reflux Disease (GERD) / Spasme Esofagus (ICD-10: K21.9) | Petunjuk Klinis: Bila ada riwayat dispepsia atau rasa panas terbakar di ulu hati.

### Rencana Pemeriksaan Penunjang (Workups)
- Elektrokardiogram (EKG) 12-lead istirahat & serial
- Enzim Jantung (Troponin I / T kuantitatif, CK-MB)
- Echocardiography Transtorakal (TTE) & Treadmill Stress Test / CT Angiografi Koroner
- Profil Lipid lengkap (Target LDL < 55 mg/dL pasca PCI)

### Kodefikasi ICD-10 Terkait
- I20.8 (Other forms of angina pectoris / stable angina)
- I25.10 (Atherosclerotic heart disease of native coronary artery)
- Z95.5 (Presence of coronary angioplasty implant and graft)
- T82.855A (Stenosis of coronary artery stent)
- K21.9 (Gastro-esophageal reflux disease without esophagitis)
- E78.5 (Hyperlipidemia, unspecified)

### Rekomendasi Terapi Obat & Panduan Dosis
- Clopidogrel 75mg | Kelas: Antiplatelet P2Y12 Inhibitor | Panduan Dosis: 75mg 1x1 tablet per hari setelah makan | Penyesuaian Ginjal: Tidak ada penyesuaian dosis khusus | Indikasi: Pencegahan trombosis stent pasca PCI DES
- Metoprolol Succinate / Bisoprolol 50mg | Kelas: Beta-Blocker Kardioselektif | Panduan Dosis: 50mg 1x1 tablet per hari pagi | Penyesuaian Ginjal: Aman pada penurunan fungsi ginjal, titrasi berdasarkan target HR 55-65 bpm | Indikasi: Anti-angina, menurunkan konsumsi oksigen miokard & kontrol denyut jantung
- Rosuvastatin 20mg / Atorvastatin 40mg | Kelas: High-Intensity Statin | Panduan Dosis: 20mg 1x1 tablet malam hari | Penyesuaian Ginjal: Pada eGFR < 30 gunakan dosis awal 5mg, pantau fungsi hepar & ginjal | Indikasi: Stabilisasi plak aterosklerosis & reduksi target LDL < 55 mg/dL

### Kontraindikasi Obat & Peringatan
- Aspirin (bila riwayat alergi berat / dispepsia berat)
- NSAID non-selektif
- Pemberian Nitrat (ISDN) bersama inhibitor PDE-5 (Sildenafil / Tadalafil)

### Titik Pemantauan Terapi (Monitoring Points)
- Pantau EKG serial dan profil lipid per 3 bulan
- Edukasi sedia ISDN sublingual PRN jika serangan angina timbul

### Tanda Bahaya Klinis & Kriteria Kegawatdaruratan (Red Flags)
- Alert: Sindrom Koroner Akut (Unstable Angina / Re-Infarction) | Tingkat Keparahan: Critical | Kriteria Pemicu: Nyeri dada retrosternal menjalar ke lengan/rahang yang berlangsung > 20 menit saat istirahat tidak mereda dengan nitrat | Tindakan Darurat: Segera aktivasi Code STEMI / transfer ke IGD terdekat untuk EKG 12-lead emergensi & biomarker troponin kuantitatif
- Alert: Syok Kardiogenik & Gagal Jantung Kiri Akut (Acute Pulmonary Edema) | Tingkat Keparahan: Critical | Kriteria Pemicu: Sesak napas hebat tiba-tiba posisi berbaring (ortopnea), ronkhi basah halus pada > 50% lapangan paru, atau tekanan darah sistolik < 90 mmHg dengan akral dingin | Tindakan Darurat: Oksigenasi aliran tinggi, Diuretik Loop IV (Furosemide), evaluasi inotropik/vasopresor, dan rujukan CITO ICCU

### Protokol Terapi Berbasis Bukti
1. Antiplatelet & Anti-Iskemik: Lanjutkan Clopidogrel 75mg OD + Aspirin 80-100mg OD (DAPT). Tambahkan Bisoprolol 2.5-5mg OD (target HR 55-65 bpm).
2. Terapi Penurun Lipid Agresif: Rosuvastatin 20mg atau Atorvastatin 40mg OD untuk mencapai target penurunan LDL > 50% atau < 55 mg/dL.
3. Manajemen Nyeri Angina Akut: ISDN 5mg Sublingual bila timbul serangan nyeri dada saat aktivitas.
"""
    },

    {
        "id": "kb-med-004",
        "title": "Omeprazole (Proton Pump Inhibitor - PPI)",
        "category": "medicine",
        "specialty": "Gastroenterology / Pharmacology",
        "icd10_code": None,
        "rxnorm_code": "7646",
        "loinc_code": None,
        "synonyms": ["Prilosec", "Omeprazole 20mg", "Losec", "Lokit", "Proton Pump Inhibitor"],
        "keywords": ["omeprazole", "ppi", "supresi asam lambung", "h+/k+ atpase", "gastritis erosif", "dispepsia", "20mg bid", "sebelum makan", "renal dosing aman", "cyp2c19 clopidogrel"],
        "evidence_level": "FDA Prescribing Information & ACG Guidelines",
        "created_at": datetime.now().isoformat(),
        "content": """
### Mekanisme Kerja & Farmakodinamik
Omeprazole adalah penghambat pompa proton (PPI) yang menghambat secara ireversibel sistem enzim H+/K+ ATPase pada sel parietal lambung, menekan sekresi asam lambung basal dan terstimulasi.

### Dosis & Panduan Pemberian
- Gastritis Erosif & Ulkus Peptikum: 20–40 mg PO BID (2 kali sehari) selama 14–28 hari.
- Dispepsia Fungsional & Pemeliharaan: 20 mg PO OD pagi.
- Aturan Minum Penting: Wajib diminum 30–60 menit sebelum makan pagi dan malam hari (kondisi lambung kosong saat pompa proton paling aktif disintesis).

### Penyesuaian Dosis Ginjal & Hati (Renal Dosing)
- Gangguan Fungsi Ginjal (CKD Stage 1-5 / ESRD): TIDAK memerlukan penyesuaian dosis. Ekskresi metabolit melalui ginjal tanpa efek nefrotoksisitas langsung pada dosis standar.
- Gangguan Hati Berat (Child-Pugh C): Batasi dosis maksimal 20 mg per hari karena bioavailabilitas meningkat.

### Interaksi Obat & Keamanan
- Interaksi CYP2C19 dengan Clopidogrel: Omeprazole menghambat enzim CYP2C19 yang memetabolisme Clopidogrel menjadi bentuk aktifnya, berpotensi menurunkan efikasi antiplatelet. Pada pasien post-PCI berisiko tinggi trombosis stent, pertimbangkan PPI alternatif seperti Pantoprazole atau Rabeprazole.
- Penggunaan Jangka Panjang (> 8 minggu): Evaluasi kadar Magnesium serum, Vitamin B12, dan risiko kolitis C. difficile.
"""
    },
    {
        "id": "kb-med-005",
        "title": "Sukralfat Suspensi (Sucralfate Mucoprotective Agent)",
        "category": "medicine",
        "specialty": "Gastroenterology / Pharmacology",
        "icd10_code": None,
        "rxnorm_code": "10156",
        "loinc_code": None,
        "synonyms": ["Sucralfate", "Carafate", "Ulsidex", "Inpepsa", "Neciblok", "Sukralfat 500mg/5mL"],
        "keywords": ["sukralfat", "sucralfate", "mukoprotektor", "sawar mukosa lambung", "suspensi 500mg/5ml", "aluminum complex", "perut kosong", "renal dosing ckd lanjut", "jeda interaksi 2 jam"],
        "evidence_level": "FDA Prescribing Information & Gastroenterology Consensus",
        "created_at": datetime.now().isoformat(),
        "content": """
### Mekanisme Kerja Sitoseluler
Sukralfat adalah kompleks sukrosa oktasulfat dengan aluminium hidroksida. Pada suasana asam lambung (pH < 4), sukralfat berpolimerisasi membentuk pasta kental bermuatan negatif yang berikatan kuat secara elektrostatis dengan protein eksudat bermuatan positif pada lesi ulkus/erosi mukosa lambung, membentuk lapisan fisik pelindung dari degradasi asam lambung, pepsin, dan garam empedu.

### Dosis & Aturan Pakai
- Suspensi 500 mg / 5 mL: 3x1 sendok makan (15 mL = 1.5 gram) per hari atau 4x10 mL.
- Waktu Konsumsi: Wajib diminum saat lambung kosong (1 jam sebelum makan atau 2 jam setelah makan, dan sebelum tidur malam).

### Peringatan Khusus Fungsi Ginjal (Renal Dosing)
- Meskipun absorpsi sistemik sangat minimal (< 3-5%), sejumlah kecil ion aluminium dapat diserap.
- Pasien CKD Stage 4-5 (eGFR < 30 mL/min): Gunakan dengan sangat hati-hati dan hindari penggunaan jangka panjang karena risiko akumulasi aluminium kronis, osteomalasia, dan ensefalopati uremik.

### Aturan Jeda Interaksi Obat (2-Hour Separation Rule)
- Sukralfat dapat mengikat dan menghambat bioavailabilitas obat oral lain melalui pembentukan khelat fisik (chelating agent).
- Berikan jeda waktu minimal 2 jam antara sukralfat dengan obat lain: Antibiotik Fluoroquinolone (Ciprofloxacin), Suplemen Besi (Ferrous Fumarate), Levothyroxine, Digoxin, Antasida, dan PPI.
"""
    },
    {
        "id": "kb-med-006",
        "title": "Ferrous Fumarate & Sulfas Ferosus (Oral Iron Therapy)",
        "category": "medicine",
        "specialty": "Hematology / Pharmacology",
        "icd10_code": None,
        "rxnorm_code": "4337",
        "loinc_code": None,
        "synonyms": ["Ferrous Fumarate", "Sulfas Ferosus", "Ferrous Sulfate", "Sangobion", "Suplemen Besi Elemental"],
        "keywords": ["ferrous fumarate", "sulfas ferosus", "zat besi", "anemia defisiensi besi", "besi elemental", "vitamin c", "absorpsi besi", "jeda antasida sukralfat", "ferritin serial"],
        "evidence_level": "WHO Guidelines on Iron Supplementation & ASH",
        "created_at": datetime.now().isoformat(),
        "content": """
### Indikasi & Farmakokinetik
Diindikasikan untuk terapi koreksi anemia defisiensi besi dan pengisian cadangan besi sumsum tulang (Ferritin). Ferrous Fumarate mengandung ~33% besi elemental (100 mg besi elemental per 300 mg tablet), sedangkan Ferrous Sulfate mengandung ~20% besi elemental.

### Panduan Dosis & Cara Pemberian
- Dosis Terapeutik Dewasa: 300 mg 1x1 tablet per hari (atau 200 mg BID pada anemia berat) dikonsumsi setelah makan untuk mengurangi efek samping iritasi lambung dan mual.
- Pengoptimalan Absorpsi: Penyerapan ion Fe2+ meningkat signifikan bila diminum bersama Vitamin C (Asam Askorbat 500 mg).
- Jeda Pemisahan Wajib: Pisahkan pemberian minimal 2 jam dari antasida, sukralfat, kalsium, teh, dan kopi yang dapat mengendapkan zat besi di usus halus.

### Profil Keamanan Ginjal & Efek Samping
- Penyesuaian Dosis Ginjal: AMAN pada seluruh derajat penurunan fungsi ginjal (CKD 1-5). Tidak memerlukan modifikasi dosis ginjal.
- Efek Samping Umum: Feses berwarna gelap/kehitaman (normal dan tidak berbahaya), konstipasi, atau rasa logam. Edukasi pasien agar tidak panik mengira melena.
- Parameter Evaluasi: Cek ulang Hb dalam 4 minggu dan profil Ferritin serum dalam 8-12 minggu.
"""
    },
    {
        "id": "kb-med-007",
        "title": "Bisoprolol & Metoprolol (Beta-1 Cardioselective Blocker)",
        "category": "medicine",
        "specialty": "Cardiology / Pharmacology",
        "icd10_code": None,
        "rxnorm_code": "161",
        "loinc_code": None,
        "synonyms": ["Bisoprolol Fumarate", "Concor", "Metoprolol Succinate", "Toprol XL", "Beta Blocker Kardioselektif"],
        "keywords": ["bisoprolol", "metoprolol", "beta-blocker", "kardioselektif", "anti-angina", "target hr 55-65 bpm", "cad post-pci", "gagal jantung", "penurunan mvo2", "titrasi dosis"],
        "evidence_level": "ACC/AHA & ESC Coronary Guidelines",
        "created_at": datetime.now().isoformat(),
        "content": """
### Mekanisme Kerja Kardioselektif
Secara selektif memblok reseptor adrenergik Beta-1 pada miokardium, memperlambat konduksi nodus SA/AV, menurunkan denyut jantung, menurunkan kontraktilitas otot jantung, dan mengurangi kebutuhan konsumsi oksigen miokard (MVO2).

### Dosis & Target Klinis
- Bisoprolol: Dosis awal 2.5 mg – 5 mg PO OD pagi, dititrasi hingga maksimal 10 mg OD.
- Target Terapeutik Anti-Angina: Denyut jantung istirahat (resting heart rate) 55–65 bpm.
- Metoprolol Succinate Lepas Lambat: 25–50 mg PO OD pagi, titrasi bertahap.

### Penyesuaian Dosis Ginjal & Hati
- eGFR ≥ 20 mL/min: Tidak ada penyesuaian dosis khusus.
- Gangguan Ginjal Berat (eGFR < 20 mL/min) atau Sirosis Hati Berat: Dosis maksimal Bisoprolol tidak boleh melebihi 10 mg per hari.

### Kontraindikasi & Monitoring
- Kontraindikasi Mutlak: Bradikardia sinus berat (HR < 50 bpm), AV Block derajat 2 atau 3 (tanpa pacemaker permanen), syok kardiogenik, dan asma bronkial berat tidak terkontrol.
- Monitoring: Pantau EKG serial, tekanan darah, dan denyut nadi pada setiap kunjungan rawat jalan.
"""
    },
    {
        "id": "kb-med-008",
        "title": "Rosuvastatin & Atorvastatin (High-Intensity Statin)",
        "category": "medicine",
        "specialty": "Cardiology / Pharmacology",
        "icd10_code": None,
        "rxnorm_code": "301542",
        "loinc_code": None,
        "synonyms": ["Rosuvastatin", "Crestor", "Atorvastatin", "Lipitor", "Statin Intensitas Tinggi"],
        "keywords": ["rosuvastatin", "atorvastatin", "statin", "hmg-coa reduktase", "target ldl < 55", "stabilisasi plak", "post-pci", "dislipidemia", "renal dosing egfr < 30", "sgot sgpt ck"],
        "evidence_level": "ACC/AHA 2024 Cholesterol Guidelines & ESC",
        "created_at": datetime.now().isoformat(),
        "content": """
### Mekanisme Kerja & Efek Pleiotropik
Menghambat enzim HMG-CoA Reduktase pada biosintesis kolesterol hepatik, meningkatkan ekspresi reseptor LDL pada membran hepatosit untuk membersihkan partikel LDL sirkulasi, serta memberikan efek pleiotropik anti-inflamasi dan stabilisasi plak aterosklerosis koroner pasca-PCI.

### Rejimen Dosis Intensitas Tinggi (High-Intensity)
- Atorvastatin: 40 mg – 80 mg PO 1x sehari malam hari.
- Rosuvastatin: 20 mg – 40 mg PO 1x sehari malam hari.
- Target LDL Kolesterol: Reduksi kadar LDL baseline ≥ 50% dan mencapai target absolut LDL < 55 mg/dL (< 1.4 mmol/L) untuk pencegahan sekunder pasien pasca-PCI / risiko ASCVD sangat tinggi.

### Panduan Dosis Ginjal (Renal Clearance Safety)
- Atorvastatin: Dieliminasi terutama melalui metabolisme hepar dan empedu (< 2% lewat urin); TIDAK memerlukan penyesuaian dosis pada gangguan fungsi ginjal derajat berapa pun.
- Rosuvastatin: Pada CKD berat (eGFR < 30 mL/min/1.73m²), mulai dengan dosis rendah 5 mg OD dan tidak melebihi 10 mg OD.

### Pemantauan Keamanan & Mialgia
- Pantau enzim transaminase hati (SGOT/SGPT) baseline dan bila timbul keluhan hepatotoksisitas.
- Periksa enzim Kreatin Kinase (CK) bila pasien mengeluhkan nyeri otot proksimal atau kelemahan (skrining miositis/rabdomiolisis).
"""
    },
    {
        "id": "kb-med-009",
        "title": "Isosorbide Dinitrate - ISDN (Nitrate Vasodilator)",
        "category": "medicine",
        "specialty": "Cardiology / Pharmacology",
        "icd10_code": None,
        "rxnorm_code": "6054",
        "loinc_code": None,
        "synonyms": ["ISDN", "Cedocard", "Fasorbid", "Isosorbide Dinitrate 5mg", "Nitrat Sublingual"],
        "keywords": ["isdn", "isosorbide dinitrate", "nitrat sublingual", "vasodilator koroner", "anti-angina prn", "penurunan preload", "jeda bebas nitrat", "kontraindikasi sildenafil pde5"],
        "evidence_level": "ESC & ACC/AHA Anti-Ischemic Guidelines",
        "created_at": datetime.now().isoformat(),
        "content": """
### Mekanisme Kerja & Hemodinamik
Diubah menjadi Nitric Oxide (NO) dalam sel otot polos pembuluh darah, menstimulasi guanylyl cyclase intraseluler, meningkatkan cGMP yang memicu relaksasi otot polos vaskular. Efek utamanya adalah venodilatasi perifer (menurunkan preload ventrikel kiri dan tekanan dinding miokard) serta vasodilatasi arteri koroner epikardial.

### Dosis & Cara Pemberian
- Serangan Nyeri Dada Akut (PRN): 1 tablet sublingual 5 mg diletakkan di bawah lidah saat serangan angina muncul. Dapat diulang 1 kali setelah 5 menit bila nyeri belum mereda. Segera cari pertolongan medis bila nyeri bertahan > 15 menit.
- Profilaksis Angina Kronis Oral: 10–20 mg PO 2-3 kali sehari, dengan jadwal asimetris (misal jam 07:00 dan jam 14:00) untuk memberikan periode bebas nitrat (nitrate-free interval) selama 10–12 jam malam hari guna mencegah toleransi nitrat.

### Kontraindikasi Mutlak & Interaksi Berbahaya
- KONTRAINDIKASI MUTLAK: Penggunaan bersama obat inhibitor Phosphodiesterase-5 (PDE-5) seperti Sildenafil (dalam 24 jam) atau Tadalafil (dalam 48 jam) karena risiko vasodilatasi masif, hipotensi refrakter fatal, dan infark miokard.
- Kondisi Lain: Hipotensi berat (TDS < 90 mmHg), syok kardiogenik, dan stenosis aorta berat.
"""
    },
    {
        "id": "kb-med-010",
        "title": "Empagliflozin & Dapagliflozin (SGLT2 Inhibitor Cardiorenal)",
        "category": "medicine",
        "specialty": "Endocrinology / Nephrology / Pharmacology",
        "icd10_code": None,
        "rxnorm_code": "1545653",
        "loinc_code": None,
        "synonyms": ["Jardiance", "Forxiga", "SGLT2 Inhibitor", "Empagliflozin 10mg", "Dapagliflozin 10mg"],
        "keywords": ["sglt2 inhibitor", "empagliflozin", "dapagliflozin", "kardiorenal proteksi", "kdigo 2024", "reduksi uacr", "egfr cutoff 20", "glukosuria", "diabetes melitus ckd", "higiene urogenital"],
        "evidence_level": "KDIGO 2024 & ADA Standards of Care 2025 (Level A)",
        "created_at": datetime.now().isoformat(),
        "content": """
### Mekanisme Renoprotektif & Kardiovaskular
Menghambat transporter Sodium-Glucose Co-Transporter 2 (SGLT2) pada tubulus kontortus proksimal ginjal, memicu ekskresi glukosa dan natrium dalam urin (glukosuria dan natriuresis). Menghambat feedback tubuloglomerular, memicu vasokonstriksi arteriol aferen, menurunkan tekanan intraglomerular (mengurangi hiperfiltrasi glomerulus), serta menurunkan albuminuria (uACR) dan memperlambat laju penurunan eGFR.

### Indikasi & Dosis
- Diabetes Mellitus Tipe 2 dengan CKD / ASCVD / Gagal Jantung: Empagliflozin 10 mg PO OD pagi atau Dapagliflozin 10 mg PO OD pagi.
- Dapat ditingkatkan hingga 25 mg OD untuk kontrol glikemik tambahan bila eGFR > 60 mL/min.

### Ambang Batas Klirens Ginjal (eGFR Cutoffs)
- Sesuai konsensus KDIGO 2024: Aman diinisiasi pada eGFR ≥ 20 mL/min/1.73m².
- Bila sudah dimulai, obat dapat dilanjutkan terus hingga pasien memerlukan terapi pengganti ginjal (dialisis).

### Edukasi Pasien & Kewaspadaan Klinis
- Edukasi hidrasi yang adekuat dan kebersihan perineal/genital untuk mencegah infeksi jamur genital (mikotik urogenital).
- Tahan sementara obat (hold) minimal 3 hari sebelum operasi mayor atau kondisi dehidrasi berat untuk mencegah Ketoasidosis Diabetik Euglikemik (euDKA).
"""
    },
    {
        "id": "kb-med-011",
        "title": "Amlodipine (Dihydropyridine CCB Antihypertensive)",
        "category": "medicine",
        "specialty": "Cardiology / Pharmacology",
        "icd10_code": None,
        "rxnorm_code": "17767",
        "loinc_code": None,
        "synonyms": ["Norvasc", "Amlodipine Besylate", "Tensivask", "CCB Dihidropiridin", "Amlodipin 5mg 10mg"],
        "keywords": ["amlodipine", "calcium channel blocker", "ccb", "antihipertensi lini pertama", "vasodilatasi perifer", "dosis 5mg 10mg", "renal dosing aman tanpa penyesuaian", "edema perifer"],
        "evidence_level": "ACC/AHA & ISH Global Hypertension Practice Guidelines",
        "created_at": datetime.now().isoformat(),
        "content": """
### Mekanisme Kerja Vaskular
Menghambat influks ion kalsium transmembran ke dalam sel otot polos vaskular dan miokardium melalui kanal kalsium tipe-L (L-type calcium channels), menyebabkan vasodilatasi arteri koroner dan perifer, menurunkan resistensi vaskular sistemik (SVR), dan menurunkan tekanan darah arterial tanpa menekan nodus SA/AV.

### Panduan Dosis & Penggunaan
- Dosis Awal Hipertensi: 5 mg PO 1x sehari, dapat dititrasi setelah 1-2 minggu hingga maksimal 10 mg PO OD.
- Dosis Lansia / Gangguan Hati: Mulai dengan dosis awal 2.5 mg PO OD.

### Profil Keamanan Ginjal (Renal Clearance Safety)
- AMAN PADA SELURUH DERAJAT GANGGUAN GINJAL (CKD Stage 1-5 / ESRD / Hemodialisis).
- Tidak memerlukan penyesuaian dosis pada penurunan fungsi ginjal karena amlodipine dimetabolisme secara ekstensif oleh hepar (> 90%) menjadi metabolit inaktif.

### Efek Samping & Kombinasi Terapi
- Efek Samping: Edema pergelangan kaki / edema perifer dependen (akibat vasodilatasi arteriol prekapiler, bukan retensi cairan ginjal).
- Sinergi Kombinasi: Kombinasi Amlodipine dengan ACE inhibitor (Lisinopril) atau ARB menyeimbangkan tekanan hidrostatik kapiler dan menurunkan insiden edema perifer secara signifikan.
"""
    }
]
