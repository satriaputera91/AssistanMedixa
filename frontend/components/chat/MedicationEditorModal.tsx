'use client';

import React, { useState, useMemo } from 'react';

export interface MedicationItem {
  id: string;
  drug_name: string;
  class: string;
  dosage: string;
  frequency: string;
  route: string;
  timing: string;
  indication: string;
  renal_dosing: string;
  guideline_basis?: string;
  special_instructions?: string;
  category?: string;
}

interface MedicationEditorModalProps {
  initialContent: string;
  onSave: (updatedMarkdown: string) => void;
  onClose: () => void;
}

// Comprehensive Formulary and Evidence-Based Drug Database
export const MEDICATION_DATABASE = [
  // Gastrointestinal & Ulkus
  {
    drug_name: 'Omeprazole',
    class: 'Proton Pump Inhibitor (PPI)',
    category: 'Gastrointestinal',
    standard_dosage: '20 mg',
    standard_frequency: '2x sehari',
    route: 'Oral',
    timing: '30-60 menit sebelum makan (Pagi & Malam)',
    indication: 'Supresi asam lambung pada Gastritis Kronis Erosif, Dispepsia, & GERD',
    renal_dosing: 'Tidak memerlukan penyesuaian dosis pada gangguan ginjal (eGFR < 60 mL/min).',
    guideline_basis: 'ACG Guidelines on Ulcer Disease & PAPDI 2023',
    special_instructions: 'Minum utuh dengan air putih, jangan dikunyah atau digerus.'
  },
  {
    drug_name: 'Lansoprazole',
    class: 'Proton Pump Inhibitor (PPI)',
    category: 'Gastrointestinal',
    standard_dosage: '30 mg',
    standard_frequency: '1-2x sehari',
    route: 'Oral',
    timing: 'Sebelum makan pagi',
    indication: 'Tukak lambung/duodenum dan refluks gastroesofagus',
    renal_dosing: 'Aman pada gagal ginjal, tidak perlu reduksi dosis.',
    guideline_basis: 'ACG Clinical Guidelines',
    special_instructions: 'Konsumsi sebelum makan pagi.'
  },
  {
    drug_name: 'Sucralfate Suspensi',
    class: 'Mucoprotective / Gastroprotective Agent',
    category: 'Gastrointestinal',
    standard_dosage: '500 mg / 5 mL (1 sendok makan / 15 mL)',
    standard_frequency: '3-4x sehari',
    route: 'Oral',
    timing: '1 jam sebelum makan atau 2 jam setelah makan (perut kosong) & sebelum tidur',
    indication: 'Sitoproteksi mukosa lambung dan epitelisasi erosi lambung',
    renal_dosing: 'Absorpsi sistemik minimal (<5%). Hati-hati pada CKD stage 4-5 karena risiko akumulasi aluminium.',
    guideline_basis: 'Gastroenterology Consensus 2024',
    special_instructions: 'Kocok dahulu sebelum diminum. Beri jeda 2 jam dengan obat lain.'
  },
  {
    drug_name: 'Rebamipide',
    class: 'Mucosal Protective / Prostaglandin Inducer',
    category: 'Gastrointestinal',
    standard_dosage: '100 mg',
    standard_frequency: '3x sehari',
    route: 'Oral',
    timing: 'Bersama atau sesudah makan',
    indication: 'Penyembuhan mukosa gaster pada gastritis dan pencegahan cedera mukosa NSAID',
    renal_dosing: 'Tidak memerlukan penyesuaian dosis pada gangguan ginjal ringan-sedang.',
    guideline_basis: 'Asian Pacific Association of Gastroenterology',
    special_instructions: 'Dapat dikombinasi aman dengan PPI.'
  },
  {
    drug_name: 'Domperidone',
    class: 'Dopamine D2 Receptor Antagonist (Prokinetik)',
    category: 'Gastrointestinal',
    standard_dosage: '10 mg',
    standard_frequency: '3x sehari',
    route: 'Oral',
    timing: '15-30 menit sebelum makan',
    indication: 'Mual, muntah, dan rasa kembung/begah (dispepsia dismotilitas)',
    renal_dosing: 'Frekuensi dikurangi menjadi 1-2x/hari pada gangguan ginjal berat.',
    guideline_basis: 'Konsensus Nasional Dispepsia 2023',
    special_instructions: 'Gunakan durasi singkat (<7 hari). Hindari pada riwayat perpanjangan interval QTc.'
  },
  {
    drug_name: 'Ondansetron',
    class: '5-HT3 Receptor Antagonist (Antiemetik)',
    category: 'Gastrointestinal',
    standard_dosage: '4-8 mg',
    standard_frequency: '2-3x sehari',
    route: 'Oral / IV',
    timing: 'Bila mual atau sebelum terapi pencetus mual',
    indication: 'Antiemetik mual-muntah akut dan refrakter',
    renal_dosing: 'Tidak memerlukan penyesuaian dosis pada gangguan ginjal.',
    guideline_basis: 'NCCN / MASCC Antiemetic Guidelines',
    special_instructions: 'Maksimal 8 mg/hari pada gangguan hepar berat (Child-Pugh C).'
  },

  // Kardiovaskular & Antihipertensi
  {
    drug_name: 'Lisinopril',
    class: 'ACE Inhibitor (ACEi)',
    category: 'Kardiovaskular',
    standard_dosage: '10 mg',
    standard_frequency: '1x sehari',
    route: 'Oral',
    timing: 'Pagi hari setelah sarapan',
    indication: 'Antihipertensi primer, nefroproteksi proteinuria, & reduksi risiko kardiovaskular',
    renal_dosing: 'eGFR 30-59: Awal 2.5-5 mg/hari. Pantau ketat kalium dan kreatinin dalam 1-2 minggu.',
    guideline_basis: 'KDIGO 2024 & ACC/AHA 2023 Hypertension Guidelines',
    special_instructions: 'Hentikan bila terjadi batuk kering persisten atau angioedema. Hindari kombinasi dengan ARB.'
  },
  {
    drug_name: 'Candesartan Cilexetil',
    class: 'Angiotensin II Receptor Blocker (ARB)',
    category: 'Kardiovaskular',
    standard_dosage: '8-16 mg',
    standard_frequency: '1x sehari',
    route: 'Oral',
    timing: 'Pagi atau malam hari',
    indication: 'Antihipertensi lini pertama pada intoleransi ACEi (batuk) & renoproteksi CKD',
    renal_dosing: 'Dosis awal 4 mg pada eGFR < 30 mL/min/1.73m². Pantau kalium serum berkala.',
    guideline_basis: 'KDIGO 2024 & PERKI 2023',
    special_instructions: 'Pilihan utama pengganti ACE inhibitor bila timbul batuk kering.'
  },
  {
    drug_name: 'Amlodipine Besylate',
    class: 'Dihydropyridine Calcium Channel Blocker (CCB)',
    category: 'Kardiovaskular',
    standard_dosage: '5-10 mg',
    standard_frequency: '1x sehari',
    route: 'Oral',
    timing: 'Pagi atau malam hari',
    indication: 'Hipertensi esensial dan profilaksis angina pektoris stabil',
    renal_dosing: 'Tidak memerlukan penyesuaian dosis pada gangguan ginjal (klirens hepatik).',
    guideline_basis: 'AHA/ACC 2023 & ESH 2023 Guidelines',
    special_instructions: 'Pantau tanda edema perifer pretibial pada penggunaan jangka panjang.'
  },
  {
    drug_name: 'Bisoprolol Fumarate',
    class: 'Cardioselective Beta-1 Blocker',
    category: 'Kardiovaskular',
    standard_dosage: '2.5-5 mg',
    standard_frequency: '1x sehari',
    route: 'Oral',
    timing: 'Pagi hari',
    indication: 'Penyakit Jantung Koroner (CAD), Angina Stabil, Gagal Jantung, & Hipertensi',
    renal_dosing: 'Maksimal 10 mg/hari pada eGFR < 20 mL/min/1.73m².',
    guideline_basis: 'ESC 2024 Chronic Coronary Syndrome Guidelines',
    special_instructions: 'Pantau laju denyut jantung (HR target 55-65 bpm pada angina stabil).'
  },
  {
    drug_name: 'Furosemide',
    class: 'Loop Diuretic',
    category: 'Kardiovaskular',
    standard_dosage: '20-40 mg',
    standard_frequency: '1x sehari (Pagi)',
    route: 'Oral / IV',
    timing: 'Pagi hari setelah sarapan',
    indication: 'Edema akibat gagal jantung, sirosis hepatis, atau penyakit ginjal',
    renal_dosing: 'Membutuhkan titrasi dosis lebih tinggi pada CKD lanjut untuk mencapai efek diuresis.',
    guideline_basis: 'KDIGO 2024 & ESC Heart Failure Guidelines',
    special_instructions: 'Hindari pemberian malam hari untuk mencegah nokturia. Pantau elektrolit & fungsi ginjal.'
  },
  {
    drug_name: 'Spironolactone',
    class: 'Mineralocorticoid Receptor Antagonist (MRA)',
    category: 'Kardiovaskular',
    standard_dosage: '25 mg',
    standard_frequency: '1x sehari',
    route: 'Oral',
    timing: 'Pagi hari',
    indication: 'Hipertensi resisten, Gagal Jantung HFrEF, & Asites Sirosis Hepatis',
    renal_dosing: 'Kontraindikasi jika eGFR < 30 mL/min/1.73m² atau Kalium > 5.0 mEq/L.',
    guideline_basis: 'ESC 2024 Heart Failure & KDIGO Guidelines',
    special_instructions: 'Wajib pantau kalium serum dan kreatinin 1 minggu pasca inisiasi.'
  },

  // Antiplatelet & Antikoagulan
  {
    drug_name: 'Clopidogrel',
    class: 'P2Y12 Platelet Inhibitor (Antiplatelet)',
    category: 'Kardiovaskular',
    standard_dosage: '75 mg',
    standard_frequency: '1x sehari',
    route: 'Oral',
    timing: 'Pagi setelah makan',
    indication: 'Dual Antiplatelet Therapy (DAPT) pasca PCI stenting & pencegahan sekunder stroke iskemik',
    renal_dosing: 'Aman pada gangguan ginjal, tidak memerlukan penyesuaian dosis.',
    guideline_basis: 'ACC/AHA DAPT Guidelines & ESC 2024',
    special_instructions: 'Kombinasikan dengan gastroprotektor PPI bila berisiko tinggi perdarahan GI.'
  },
  {
    drug_name: 'Aspilet / Asam Asetilsalisilat (Aspirin)',
    class: 'COX-1 Inhibitor / Antiplatelet',
    category: 'Kardiovaskular',
    standard_dosage: '80-100 mg',
    standard_frequency: '1x sehari',
    route: 'Oral',
    timing: 'Sesudah makan',
    indication: 'Pencegahan sekunder infark miokard, stroke iskemik, dan DAPT pasca PCI',
    renal_dosing: 'Gunakan dosis rendah (80-100 mg). Hindari pada CKD stage 5 jika ada koagulopati.',
    guideline_basis: 'AHA/ACC 2023 Secondary Prevention Guidelines',
    special_instructions: 'Wajib diminum sesudah makan untuk meminimalkan iritasi lambung.'
  },

  // Endokrin & Antidiabetes
  {
    drug_name: 'Metformin XR (Extended Release)',
    class: 'Biguanide',
    category: 'Endokrin',
    standard_dosage: '500-1000 mg',
    standard_frequency: '1x sehari (Malam)',
    route: 'Oral',
    timing: 'Bersama makan malam / segera setelah makan malam',
    indication: 'Terapi farmakologis lini pertama Diabetes Melitus Tipe 2',
    renal_dosing: 'eGFR 30-44: Maks 1000 mg/hari. eGFR < 30: Kontraindikasi (risiko asidosis laktat).',
    guideline_basis: 'ADA Standards of Care 2025 & PERKENI 2023',
    special_instructions: 'Formulasi XR meminimalkan efek samping gastrointestinal (mual/diare).'
  },
  {
    drug_name: 'Empagliflozin',
    class: 'SGLT2 Inhibitor',
    category: 'Endokrin',
    standard_dosage: '10-25 mg',
    standard_frequency: '1x sehari',
    route: 'Oral',
    timing: 'Pagi hari (sebelum atau sesudah makan)',
    indication: 'Kardio-renoproteksi pada DMT2 dengan CKD/HFrEF dan kontrol glikemik',
    renal_dosing: 'Dapat diinisiasi hingga eGFR 20 mL/min/1.73m² untuk nefroproteksi.',
    guideline_basis: 'ADA 2025 & KDIGO 2024 Diabetes Management in CKD',
    special_instructions: 'Edukasi hidrasi adekuat dan higiene perineal untuk cegah infeksi mikotik genital.'
  },
  {
    drug_name: 'Dapagliflozin',
    class: 'SGLT2 Inhibitor',
    category: 'Endokrin',
    standard_dosage: '10 mg',
    standard_frequency: '1x sehari',
    route: 'Oral',
    timing: 'Pagi hari',
    indication: 'Gagal Jantung (semua LVEF), CKD dengan albuminuria, dan DMT2',
    renal_dosing: 'Bermanfaat untuk memperlambat laju penurunan eGFR hingga eGFR 25 mL/min.',
    guideline_basis: 'DAPA-CKD Trial & KDIGO 2024',
    special_instructions: 'Pertahankan asupan cairan cukup.'
  },
  {
    drug_name: 'Sitagliptin',
    class: 'DPP-4 Inhibitor',
    category: 'Endokrin',
    standard_dosage: '100 mg',
    standard_frequency: '1x sehari',
    route: 'Oral',
    timing: 'Sebelum atau sesudah makan',
    indication: 'Kontrol glikemik DMT2 dengan risiko hipoglikemia sangat rendah',
    renal_dosing: 'eGFR 30-44: 50 mg/hari; eGFR < 30: 25 mg/hari.',
    guideline_basis: 'ADA 2025 & PERKENI 2023',
    special_instructions: 'Pilihan aman pada lansia dan pasien CKD.'
  },
  {
    drug_name: 'Insulin Glargine (Lantus)',
    class: 'Long-acting Basal Insulin Analog',
    category: 'Endokrin',
    standard_dosage: '10-14 IU (0.1-0.2 IU/kgBB)',
    standard_frequency: '1x sehari',
    route: 'Subkutan (SC)',
    timing: 'Malam hari pada jam yang sama setiap hari',
    indication: 'Regulasi glukosa basal pada DMT2 yang tidak terkontrol OAD atau dengan komplikasi CKD lanjut',
    renal_dosing: 'Reduksi dosis 25-50% pada CKD stage 4-5 karena klirens insulin menurun.',
    guideline_basis: 'ADA 2025 & PERKENI 2023',
    special_instructions: 'Rotasi lokasi injeksi (abdomen, paha, lengan atas). Simpan insulin aktif pada suhu ruang.'
  },

  // Lipid & Dislipidemia
  {
    drug_name: 'Atorvastatin',
    class: 'HMG-CoA Reductase Inhibitor (High-Intensity Statin)',
    category: 'Kardiovaskular',
    standard_dosage: '20-40 mg',
    standard_frequency: '1x sehari',
    route: 'Oral',
    timing: 'Malam hari sebelum tidur',
    indication: 'Pencegahan sekunder ASCVD, dislipidemia, dan stabilisasi plak aterosklerosis',
    renal_dosing: 'Tidak memerlukan penyesuaian dosis pada gangguan ginjal (eliminasi hepar).',
    guideline_basis: 'ACC/AHA 2023 Lipid Guidelines & KDIGO 2024',
    special_instructions: 'Pantau keluhan mialgia atau nyeri otot. Evaluasi profil lipid dalam 6-12 minggu.'
  },
  {
    drug_name: 'Rosuvastatin',
    class: 'HMG-CoA Reductase Inhibitor (High-Intensity Statin)',
    category: 'Kardiovaskular',
    standard_dosage: '10-20 mg',
    standard_frequency: '1x sehari',
    route: 'Oral',
    timing: 'Malam hari',
    indication: 'Reduksi LDL-C intensif pada risiko kardiovaskular sangat tinggi',
    renal_dosing: 'Dosis awal 5 mg pada eGFR < 30 mL/min/1.73m² (maksimal 10 mg/hari).',
    guideline_basis: 'ESC 2023 Dyslipidemia Guidelines',
    special_instructions: 'Efektifitas penurunan LDL sangat tinggi (>50%).'
  },
  {
    drug_name: 'Fenofibrate',
    class: 'Fibric Acid Derivative (Fibrat)',
    category: 'Kardiovaskular',
    standard_dosage: '145-160 mg',
    standard_frequency: '1x sehari',
    route: 'Oral',
    timing: 'Bersama makanan',
    indication: 'Hipertrigliseridemia berat (Trigliserida > 500 mg/dL) untuk mencegah pankreatitis',
    renal_dosing: 'eGFR 30-59: Maks 54 mg/hari; eGFR < 30: Kontraindikasi.',
    guideline_basis: 'Endocrine Society Guidelines 2024',
    special_instructions: 'Hindari kombinasi dengan statin dosis tinggi tanpa pemantauan CK.'
  },

  // Neurologi & Analgesik
  {
    drug_name: 'Pregabalin',
    class: 'Gabapentinoid / Alpha-2-Delta Ligand',
    category: 'Neurologi',
    standard_dosage: '75 mg',
    standard_frequency: '2x sehari (atau 1x malam hari)',
    route: 'Oral',
    timing: 'Malam hari sebelum tidur',
    indication: 'Nyeri neuropatik perifer diabetik (DPN) & radikulopati',
    renal_dosing: 'eGFR 30-59: 25-75 mg/hari (dosis tunggal/terbagi); eGFR 15-29: 25-50 mg/hari.',
    guideline_basis: 'IASP 2023 & ADA Standards of Care',
    special_instructions: 'Edukasi risiko rasa kantuk/pusing pada awal terapi. Titrasi dosis bertahap.'
  },
  {
    drug_name: 'Gabapentin',
    class: 'GABA Analog / Antikonvulsan',
    category: 'Neurologi',
    standard_dosage: '100-300 mg',
    standard_frequency: '1-3x sehari',
    route: 'Oral',
    timing: 'Sesudah makan',
    indication: 'Nyeri neuropatik, neuralgia pasca herpetik, parestesia diabetik',
    renal_dosing: 'eGFR 30-59: 200-700 mg/hari; eGFR 15-29: 100-300 mg/hari.',
    guideline_basis: 'Neuropathic Pain Guidelines 2023',
    special_instructions: 'Titrasi dari dosis malam hari untuk meminimalkan sedasi.'
  },
  {
    drug_name: 'Paracetamol (Acetaminophen)',
    class: 'Non-Opioid Analgesic / Antipyretic',
    category: 'Analgesik',
    standard_dosage: '500-1000 mg',
    standard_frequency: '3-4x sehari (bila perlu)',
    route: 'Oral',
    timing: 'Sesudah makan / bila nyeri',
    indication: 'Analgesik lini pertama aman untuk nyeri somatik ringan-sedang',
    renal_dosing: 'Aman pada penyakit ginjal; interval diperpanjang (tiap 6-8 jam) pada eGFR < 10 mL/min.',
    guideline_basis: 'WHO Pain Ladder & KDIGO Analgesia Consensus',
    special_instructions: 'Dosis maksimal 3000 mg/24 jam. Pilihan analgetik paling aman untuk pasien gastritis & CKD.'
  }
];

export default function MedicationEditorModal({
  initialContent,
  onSave,
  onClose
}: MedicationEditorModalProps) {
  // Parse initial recommendations from message content or generate default clinical regimens
  const [items, setItems] = useState<MedicationItem[]>(() => {
    const list: MedicationItem[] = [];
    const lower = initialContent.toLowerCase();

    if (lower.includes('gastritis') || lower.includes('omeprazole') || lower.includes('sukralfat') || lower.includes('sucralfate') || lower.includes('k29')) {
      list.push({
        id: '1',
        drug_name: 'Omeprazole',
        class: 'Proton Pump Inhibitor (PPI)',
        dosage: '20 mg',
        frequency: '2x sehari',
        route: 'Oral',
        timing: '30-60 menit sebelum makan (Pagi & Malam)',
        indication: 'Supresi sekresi asam lambung dan penyembuhan erosi mukosa gaster',
        renal_dosing: 'Aman pada gangguan ginjal ringan-sedang, tidak perlu penyesuaian dosis.',
        guideline_basis: 'ACG Guidelines on Ulcer Disease & PAPDI 2023'
      });
      list.push({
        id: '2',
        drug_name: 'Sucralfate Suspensi',
        class: 'Mucoprotective / Gastroprotective Agent',
        dosage: '500 mg / 5 mL (15 mL)',
        frequency: '3x sehari',
        route: 'Oral',
        timing: '1 jam sebelum makan atau 2 jam setelah makan (perut kosong)',
        indication: 'Sitoproteksi mukosa lambung dan pembentukan lapisan pelindung ulkus',
        renal_dosing: 'Absorpsi sistemik minimal (<5%), aman pada CKD stage 1-3.',
        guideline_basis: 'Gastroenterology Consensus 2024'
      });
      list.push({
        id: '3',
        drug_name: 'Rebamipide',
        class: 'Mucosal Protective / Prostaglandin Inducer',
        dosage: '100 mg',
        frequency: '3x sehari',
        route: 'Oral',
        timing: 'Bersama makan',
        indication: 'Mempercepat epitelisasi mukosa lambung dan menghambat inflamasi gaster',
        renal_dosing: 'Tidak memerlukan penyesuaian dosis ginjal.',
        guideline_basis: 'Asian Pacific Association of Gastroenterology'
      });
      list.push({
        id: '4',
        drug_name: 'Paracetamol',
        class: 'Non-Opioid Analgesic',
        dosage: '500 mg',
        frequency: '3x sehari (Bila nyeri/demam)',
        route: 'Oral',
        timing: 'Sesudah makan',
        indication: 'Analgetik lini pertama pengganti NSAID (bebas iritasi lambung)',
        renal_dosing: 'Aman pada fungsi ginjal saat ini, maksimal 3000 mg/hari.',
        guideline_basis: 'WHO Pain Ladder & KDIGO Safety'
      });
    } else if (lower.includes('angina') || lower.includes('clopidogrel') || lower.includes('bisoprolol') || lower.includes('i20')) {
      list.push({
        id: '1',
        drug_name: 'Clopidogrel',
        class: 'Antiplatelet (P2Y12 Inhibitor)',
        dosage: '75 mg',
        frequency: '1x sehari',
        route: 'Oral',
        timing: 'Pagi sesudah makan',
        indication: 'Dual Antiplatelet Therapy (DAPT) pencegahan restenosis stent koroner',
        renal_dosing: 'Aman pada gangguan ginjal, tidak perlu reduksi dosis.',
        guideline_basis: 'ACC/AHA DAPT Guidelines & ESC 2024'
      });
      list.push({
        id: '2',
        drug_name: 'Aspilet (Aspirin)',
        class: 'Antiplatelet (COX-1 Inhibitor)',
        dosage: '80 mg',
        frequency: '1x sehari',
        route: 'Oral',
        timing: 'Sesudah makan',
        indication: 'Pencegahan sekunder infark miokard & trombosis koroner',
        renal_dosing: 'Dosis rendah aman; pantau perdarahan.',
        guideline_basis: 'AHA/ACC 2023 Secondary Prevention'
      });
      list.push({
        id: '3',
        drug_name: 'Bisoprolol Fumarate',
        class: 'Cardioselective Beta-1 Blocker',
        dosage: '2.5 mg',
        frequency: '1x sehari (Pagi)',
        route: 'Oral',
        timing: 'Pagi hari',
        indication: 'Anti-iskemik miokard dan kontrol frekuensi denyut jantung (target HR 55-65 bpm)',
        renal_dosing: 'Aman pada eGFR > 20 mL/min/1.73m².',
        guideline_basis: 'ESC 2024 Chronic Coronary Syndrome'
      });
      list.push({
        id: '4',
        drug_name: 'Atorvastatin',
        class: 'High-Intensity Statin',
        dosage: '40 mg',
        frequency: '1x sehari',
        route: 'Oral',
        timing: 'Malam sebelum tidur',
        indication: 'Penurunan agresif LDL-C (<55 mg/dL) dan stabilisasi plak aterom koroner',
        renal_dosing: 'Tidak memerlukan penyesuaian dosis pada gangguan ginjal.',
        guideline_basis: 'ACC/AHA 2023 Lipid Guidelines'
      });
    } else {
      // Default: DM2 Vance / Komprehensif
      list.push({
        id: '1',
        drug_name: 'Lisinopril',
        class: 'ACE Inhibitor (ACEi)',
        dosage: '10 mg',
        frequency: '1x sehari',
        route: 'Oral',
        timing: 'Pagi hari',
        indication: 'Kontrol tekanan darah dan nefroproteksi (penurunan albuminuria)',
        renal_dosing: 'eGFR 30-59: Dosis awal 2.5-5 mg/hari, titrasi bertahap. Pantau kalium & kreatinin.',
        guideline_basis: 'KDIGO 2024 & ADA Standards of Care 2025'
      });
      list.push({
        id: '2',
        drug_name: 'Metformin XR',
        class: 'Biguanide',
        dosage: '500 mg',
        frequency: '1x sehari',
        route: 'Oral',
        timing: 'Bersama makan malam',
        indication: 'Kontrol glikemik lini pertama Diabetes Melitus Tipe 2',
        renal_dosing: 'eGFR 30-44: Maks 1000 mg/hari; Kontraindikasi jika eGFR < 30 mL/min.',
        guideline_basis: 'ADA 2025 & PERKENI 2023'
      });
      list.push({
        id: '3',
        drug_name: 'Empagliflozin',
        class: 'SGLT2 Inhibitor',
        dosage: '10 mg',
        frequency: '1x sehari',
        route: 'Oral',
        timing: 'Pagi hari',
        indication: 'Kardio-renoproteksi progresifitas CKD & penurunan risiko kardiovaskular',
        renal_dosing: 'Dapat dipertahankan hingga eGFR 20 mL/min/1.73m² untuk renoproteksi.',
        guideline_basis: 'KDIGO 2024 & ADA 2025'
      });
      list.push({
        id: '4',
        drug_name: 'Pregabalin',
        class: 'Alpha-2-Delta Ligand',
        dosage: '75 mg',
        frequency: '1x sehari (Malam)',
        route: 'Oral',
        timing: 'Malam sebelum tidur',
        indication: 'Analgesik neuropati diabetik perifer (DPN) & perbaikan kualitas tidur',
        renal_dosing: 'eGFR 30-59: Dosis awal 25-50 mg/hari, maksimal 150 mg/hari.',
        guideline_basis: 'ADA 2025 & IASP Neuropathic Pain Guidelines'
      });
    }

    return list;
  });

  const [activeTab, setActiveTab] = useState<'regimen' | 'database' | 'preview'>('regimen');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [editingItemId, setEditingItemId] = useState<string | null>(items[0]?.id || null);
  const [clinicalGuidelineNote, setClinicalGuidelineNote] = useState<string>(
    '1. Evaluasi berkala fungsi ginjal (eGFR, Serum Kreatinin) dan elektrolit serum (Kalium, Natrium) dalam 2-4 minggu pasca inisiasi terapi.\n2. Edukasi kepatuhan minum obat secara teratur dan pemantauan efek samping obat.\n3. Jangan menghentikan obat antihipertensi atau antidiabetes secara mendadak tanpa konfirmasi DPJP.'
  );

  // Categories list
  const categories = useMemo(() => {
    const set = new Set<string>();
    MEDICATION_DATABASE.forEach(m => set.add(m.category));
    return ['All', ...Array.from(set)];
  }, []);

  // Filtered Formulary Drugs
  const filteredDrugs = useMemo(() => {
    let result = MEDICATION_DATABASE;
    if (selectedCategory !== 'All') {
      result = result.filter(d => d.category === selectedCategory);
    }
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      result = result.filter(
        d =>
          d.drug_name.toLowerCase().includes(q) ||
          d.class.toLowerCase().includes(q) ||
          d.indication.toLowerCase().includes(q) ||
          d.category.toLowerCase().includes(q)
      );
    }
    return result;
  }, [searchTerm, selectedCategory]);

  // Add medication from Database
  const handleAddFromDatabase = (drug: typeof MEDICATION_DATABASE[0]) => {
    const newItem: MedicationItem = {
      id: Date.now().toString(),
      drug_name: drug.drug_name,
      class: drug.class,
      dosage: drug.standard_dosage,
      frequency: drug.standard_frequency,
      route: drug.route,
      timing: drug.timing,
      indication: drug.indication,
      renal_dosing: drug.renal_dosing,
      guideline_basis: drug.guideline_basis,
      special_instructions: drug.special_instructions,
      category: drug.category
    };
    setItems(prev => [...prev, newItem]);
    setEditingItemId(newItem.id);
    setActiveTab('regimen');
  };

  // Add custom medication
  const handleAddCustom = () => {
    const newItem: MedicationItem = {
      id: Date.now().toString(),
      drug_name: 'Nama Obat Baru',
      class: 'Golongan Obat',
      dosage: 'Dosis (mis. 500 mg)',
      frequency: '1x sehari',
      route: 'Oral',
      timing: 'Sesudah makan',
      indication: 'Indikasi klinis terapi',
      renal_dosing: 'Aman pada fungsi ginjal saat ini',
      guideline_basis: 'Pedoman Klinis Terkini'
    };
    setItems(prev => [...prev, newItem]);
    setEditingItemId(newItem.id);
  };

  // Delete medication
  const handleDeleteItem = (id: string) => {
    setItems(prev => prev.filter(item => item.id !== id));
    if (editingItemId === id) {
      setEditingItemId(null);
    }
  };

  // Update field
  const handleUpdateItem = (id: string, field: keyof MedicationItem, value: string) => {
    setItems(prev =>
      prev.map(item => (item.id === id ? { ...item, [field]: value } : item))
    );
  };

  // Generate Markdown table
  const generatedMarkdown = useMemo(() => {
    let md = `## 💊 Rekomendasi Terapi Obat & Dosis Berbasis Bukti (Knowledge Management)\n\n`;
    md += `*Pedoman Konsensus & Panduan Klinis Terkini (KDIGO 2024 / ADA 2025 / ACG / ESC 2024)*\n\n`;
    md += `### 📋 Tabel Rejimen Farmakoterapi Rekomendasi Terpilih\n\n`;
    md += `| Nama Obat & Golongan | Dosis & Frekuensi | Rute & Waktu Pemberian | Indikasi Klinis | Penyesuaian Dosis (Ginjal/Hepar) |\n`;
    md += `| :--- | :--- | :--- | :--- | :--- |\n`;

    items.forEach(item => {
      const nameAndClass = `**${item.drug_name}**<br><span class="text-xs text-slate-500">(${item.class})</span>`;
      const doseFreq = `**${item.dosage}**<br>${item.frequency}`;
      const routeTiming = `${item.route}<br>*${item.timing}*`;
      const ind = item.indication;
      const renal = item.renal_dosing || 'Sesuai fungsi ginjal saat ini.';
      md += `| ${nameAndClass} | ${doseFreq} | ${routeTiming} | ${ind} | ${renal} |\n`;
    });

    md += `\n### 🛡️ Pertimbangan Keamanan & Rekomendasi Monitoring Lanjutan\n`;
    md += clinicalGuidelineNote.trim() ? `${clinicalGuidelineNote}\n\n` : '';
    md += `---\n`;
    md += `*(⚠️ **Clinical Disclaimer**: Rekomendasi terapi obat dan penyesuaian dosis bersumber dari Knowledge Management medis untuk mendukung keputusan klinis Dokter Penanggung Jawab Pasien / DPJP.)*`;

    return md;
  }, [items, clinicalGuidelineNote]);

  const handleSave = () => {
    onSave(generatedMarkdown);
    onClose();
  };

  const currentEditingItem = items.find(i => i.id === editingItemId);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white dark:bg-slate-900 border border-emerald-300 dark:border-slate-800 rounded-2xl shadow-2xl w-full max-w-5xl max-h-[92vh] flex flex-col overflow-hidden">
        {/* Header Modal */}
        <div className="px-6 py-4 bg-gradient-to-r from-teal-700 via-emerald-700 to-teal-800 text-white flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white/15 flex items-center justify-center text-xl shadow-inner border border-white/20">
              💊
            </div>
            <div>
              <h2 className="text-base font-bold flex items-center gap-2">
                <span>Editor Rekomendasi Terapi Obat & Dosis Klinis</span>
                <span className="px-2 py-0.5 rounded-full bg-white/20 text-white text-[10px] font-bold">
                  Evidence-Based Formulary
                </span>
              </h2>
              <p className="text-xs text-teal-100/90 font-medium">
                Sesuaikan rejimen obat, dosis nefroprotektif, aturan minum, dan verifikasi keamanan farmakologis.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/20 text-white flex items-center justify-center transition-colors text-sm font-bold"
            title="Tutup Modal"
          >
            ✕
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-emerald-100 dark:border-slate-800 bg-emerald-50/50 dark:bg-slate-900/60 px-6 pt-3 gap-2">
          <button
            onClick={() => setActiveTab('regimen')}
            className={`px-4 py-2 text-xs font-bold rounded-t-xl transition-all border-t border-x ${
              activeTab === 'regimen'
                ? 'bg-white dark:bg-slate-900 text-teal-700 dark:text-teal-400 border-emerald-200 dark:border-slate-700 shadow-xs'
                : 'bg-transparent text-slate-600 dark:text-slate-400 border-transparent hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            📋 Rejimen Obat Aktif ({items.length})
          </button>
          <button
            onClick={() => setActiveTab('database')}
            className={`px-4 py-2 text-xs font-bold rounded-t-xl transition-all border-t border-x ${
              activeTab === 'database'
                ? 'bg-white dark:bg-slate-900 text-teal-700 dark:text-teal-400 border-emerald-200 dark:border-slate-700 shadow-xs'
                : 'bg-transparent text-slate-600 dark:text-slate-400 border-transparent hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            🔍 Cari Formularium Medis ({MEDICATION_DATABASE.length})
          </button>
          <button
            onClick={() => setActiveTab('preview')}
            className={`px-4 py-2 text-xs font-bold rounded-t-xl transition-all border-t border-x ${
              activeTab === 'preview'
                ? 'bg-white dark:bg-slate-900 text-teal-700 dark:text-teal-400 border-emerald-200 dark:border-slate-700 shadow-xs'
                : 'bg-transparent text-slate-600 dark:text-slate-400 border-transparent hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            👁️ Preview Output Markdown
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 bg-slate-50/50 dark:bg-slate-950">
          {/* TAB 1: REGIMEN EDITOR */}
          {activeTab === 'regimen' && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Left Column: List of Medications */}
              <div className="lg:col-span-5 flex flex-col gap-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                    Daftar Obat Terpilih
                  </span>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => setActiveTab('database')}
                      className="px-2.5 py-1 rounded-lg bg-teal-50 dark:bg-teal-950/60 border border-teal-300 dark:border-teal-700 text-teal-700 dark:text-teal-300 text-[11px] font-bold hover:bg-teal-100 transition-colors flex items-center gap-1"
                    >
                      <span>+ Formularium</span>
                    </button>
                    <button
                      type="button"
                      onClick={handleAddCustom}
                      className="px-2.5 py-1 rounded-lg bg-emerald-600 text-white text-[11px] font-bold hover:bg-emerald-500 transition-colors flex items-center gap-1 shadow-xs"
                    >
                      <span>+ Obat Kustom</span>
                    </button>
                  </div>
                </div>

                <div className="flex flex-col gap-2 max-h-[480px] overflow-y-auto pr-1">
                  {items.length === 0 ? (
                    <div className="p-8 text-center bg-white dark:bg-slate-900 rounded-xl border border-dashed border-slate-300 dark:border-slate-800 text-slate-400 text-xs">
                      Belum ada obat dalam rejimen. Klik "+ Formularium" untuk memilih obat.
                    </div>
                  ) : (
                    items.map((item, idx) => (
                      <div
                        key={item.id}
                        onClick={() => setEditingItemId(item.id)}
                        className={`p-3.5 rounded-xl border transition-all cursor-pointer relative ${
                          editingItemId === item.id
                            ? 'bg-teal-50/90 dark:bg-teal-950/40 border-teal-500 dark:border-teal-500 shadow-sm ring-1 ring-teal-500/30'
                            : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <span className="w-5 h-5 rounded-full bg-teal-100 dark:bg-teal-900 text-teal-800 dark:text-teal-200 text-[10px] font-bold flex items-center justify-center">
                              {idx + 1}
                            </span>
                            <div>
                              <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">
                                {item.drug_name || 'Obat Baru'}
                              </h4>
                              <p className="text-[11px] text-teal-600 dark:text-teal-400 font-semibold">
                                {item.dosage} • {item.frequency}
                              </p>
                            </div>
                          </div>

                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteItem(item.id);
                            }}
                            className="text-slate-400 hover:text-red-500 text-xs p-1 rounded-md transition-colors"
                            title="Hapus Obat"
                          >
                            🗑️
                          </button>
                        </div>

                        <div className="mt-2 text-[10px] text-slate-500 dark:text-slate-400 line-clamp-1">
                          <span className="font-medium text-slate-700 dark:text-slate-300">Indikasi:</span> {item.indication}
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Additional Clinical Notes */}
                <div className="mt-2">
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                    Catatan Monitoring & Edukasi Terapi (DPJP):
                  </label>
                  <textarea
                    rows={3}
                    value={clinicalGuidelineNote}
                    onChange={(e) => setClinicalGuidelineNote(e.target.value)}
                    className="w-full text-xs p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-hidden focus:ring-2 focus:ring-teal-500 resize-none"
                    placeholder="Masukkan instruksi pemantauan lab, efek samping, dan edukasi kepatuhan obat..."
                  />
                </div>
              </div>

              {/* Right Column: Detail Editor for Selected Drug */}
              <div className="lg:col-span-7 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 shadow-xs flex flex-col justify-between">
                {currentEditingItem ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                      <div>
                        <span className="text-[10px] font-bold text-teal-600 dark:text-teal-400 uppercase tracking-wider">
                          Detail Parameter Obat
                        </span>
                        <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                          {currentEditingItem.drug_name || 'Edit Obat'}
                        </h3>
                      </div>
                      <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-semibold">
                        {currentEditingItem.class}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">
                          Nama Obat (Generik / Dagang):
                        </label>
                        <input
                          type="text"
                          value={currentEditingItem.drug_name}
                          onChange={(e) => handleUpdateItem(currentEditingItem.id, 'drug_name', e.target.value)}
                          className="w-full text-xs p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950 text-slate-800 dark:text-slate-200 font-semibold focus:outline-hidden focus:ring-2 focus:ring-teal-500"
                        />
                      </div>

                      <div>
                        <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">
                          Golongan Farmakologi:
                        </label>
                        <input
                          type="text"
                          value={currentEditingItem.class}
                          onChange={(e) => handleUpdateItem(currentEditingItem.id, 'class', e.target.value)}
                          className="w-full text-xs p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950 text-slate-800 dark:text-slate-200 focus:outline-hidden focus:ring-2 focus:ring-teal-500"
                        />
                      </div>

                      <div>
                        <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">
                          Dosis Obat:
                        </label>
                        <input
                          type="text"
                          value={currentEditingItem.dosage}
                          onChange={(e) => handleUpdateItem(currentEditingItem.id, 'dosage', e.target.value)}
                          className="w-full text-xs p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950 text-slate-800 dark:text-slate-200 font-semibold focus:outline-hidden focus:ring-2 focus:ring-teal-500"
                          placeholder="Contoh: 20 mg, 500 mg, 10 IU"
                        />
                      </div>

                      <div>
                        <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">
                          Frekuensi Pemberian:
                        </label>
                        <input
                          type="text"
                          value={currentEditingItem.frequency}
                          onChange={(e) => handleUpdateItem(currentEditingItem.id, 'frequency', e.target.value)}
                          className="w-full text-xs p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950 text-slate-800 dark:text-slate-200 focus:outline-hidden focus:ring-2 focus:ring-teal-500"
                          placeholder="Contoh: 1x sehari, 2x sehari, 3x sehari"
                        />
                      </div>

                      <div>
                        <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">
                          Rute Pemberian:
                        </label>
                        <select
                          value={currentEditingItem.route}
                          onChange={(e) => handleUpdateItem(currentEditingItem.id, 'route', e.target.value)}
                          className="w-full text-xs p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950 text-slate-800 dark:text-slate-200 focus:outline-hidden focus:ring-2 focus:ring-teal-500"
                        >
                          <option value="Oral">Oral (Per Oral / PO)</option>
                          <option value="Subkutan (SC)">Subkutan (SC)</option>
                          <option value="Intravena (IV)">Intravena (IV)</option>
                          <option value="Inhalasi">Inhalasi</option>
                          <option value="Topikal">Topikal</option>
                          <option value="Sublingual">Sublingual</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">
                          Waktu Minum / Timing:
                        </label>
                        <input
                          type="text"
                          value={currentEditingItem.timing}
                          onChange={(e) => handleUpdateItem(currentEditingItem.id, 'timing', e.target.value)}
                          className="w-full text-xs p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950 text-slate-800 dark:text-slate-200 focus:outline-hidden focus:ring-2 focus:ring-teal-500"
                          placeholder="Contoh: 30 menit sebelum makan pagi"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">
                        Indikasi Klinis Spesifik:
                      </label>
                      <input
                        type="text"
                        value={currentEditingItem.indication}
                        onChange={(e) => handleUpdateItem(currentEditingItem.id, 'indication', e.target.value)}
                        className="w-full text-xs p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950 text-slate-800 dark:text-slate-200 focus:outline-hidden focus:ring-2 focus:ring-teal-500"
                        placeholder="Contoh: Supresi sekresi asam lambung pada gastritis kronis"
                      />
                    </div>

                    <div>
                      <label className="block text-[11px] font-bold text-amber-700 dark:text-amber-400 mb-1 flex items-center gap-1">
                        <span>🛡️</span>
                        <span>Panduan Penyesuaian Dosis Ginjal / Hepar (Renal & Hepatic Dosing):</span>
                      </label>
                      <textarea
                        rows={2}
                        value={currentEditingItem.renal_dosing}
                        onChange={(e) => handleUpdateItem(currentEditingItem.id, 'renal_dosing', e.target.value)}
                        className="w-full text-xs p-2.5 rounded-xl border border-amber-200 dark:border-amber-900/50 bg-amber-50/50 dark:bg-amber-950/20 text-slate-800 dark:text-slate-200 focus:outline-hidden focus:ring-2 focus:ring-amber-500 resize-none"
                        placeholder="Contoh: Aman pada eGFR > 30 mL/min; reduksi dosis 50% jika eGFR < 30 mL/min"
                      />
                    </div>
                  </div>
                ) : (
                  <div className="p-12 text-center text-slate-400 text-xs">
                    Pilih salah satu obat di sebelah kiri untuk mengedit rincian dosis dan instruksi klinis.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 2: DRUG DATABASE FORMULARY */}
          {activeTab === 'database' && (
            <div className="space-y-4">
              {/* Search and Category Filter */}
              <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
                <div className="relative flex-1">
                  <span className="absolute left-3 top-2.5 text-sm text-slate-400">🔍</span>
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Cari nama obat generik, golongan (PPI, ACEi, Statin), atau indikasi klinis..."
                    className="w-full pl-9 pr-4 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-200 focus:outline-hidden focus:ring-2 focus:ring-teal-500"
                  />
                </div>

                {/* Category Chips */}
                <div className="flex gap-1.5 overflow-x-auto pb-1 md:pb-0">
                  {categories.map((cat) => (
                    <button
                      key={cat}
                      type="button"
                      onClick={() => setSelectedCategory(cat)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition-colors ${
                        selectedCategory === cat
                          ? 'bg-teal-600 text-white shadow-xs'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
                      }`}
                    >
                      {cat}
                    </button>
                  ))}
                </div>
              </div>

              {/* Grid of Available Drugs in Database */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5 max-h-[500px] overflow-y-auto pr-1">
                {filteredDrugs.map((drug, i) => {
                  const isAlreadyAdded = items.some(item => item.drug_name.toLowerCase() === drug.drug_name.toLowerCase());
                  return (
                    <div
                      key={i}
                      className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 hover:border-teal-400 dark:hover:border-teal-600 transition-all flex flex-col justify-between shadow-xs hover:shadow-md"
                    >
                      <div>
                        <div className="flex items-start justify-between gap-2 mb-1.5">
                          <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">
                            {drug.drug_name}
                          </h4>
                          <span className="px-2 py-0.5 rounded-md bg-teal-50 dark:bg-teal-950 text-teal-700 dark:text-teal-300 text-[10px] font-bold border border-teal-200 dark:border-teal-800">
                            {drug.category}
                          </span>
                        </div>

                        <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium mb-2">
                          {drug.class}
                        </p>

                        <div className="bg-slate-50 dark:bg-slate-950 p-2.5 rounded-lg text-[10px] text-slate-600 dark:text-slate-300 space-y-1 border border-slate-100 dark:border-slate-850">
                          <div>
                            <span className="font-bold text-slate-800 dark:text-slate-200">Dosis Baku:</span> {drug.standard_dosage} ({drug.standard_frequency})
                          </div>
                          <div>
                            <span className="font-bold text-slate-800 dark:text-slate-200">Waktu:</span> {drug.timing}
                          </div>
                          <div className="text-amber-600 dark:text-amber-400 line-clamp-2">
                            <span className="font-bold">Ginjal:</span> {drug.renal_dosing}
                          </div>
                        </div>
                      </div>

                      <button
                        type="button"
                        onClick={() => handleAddFromDatabase(drug)}
                        className={`mt-3 w-full py-1.5 rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-colors ${
                          isAlreadyAdded
                            ? 'bg-slate-100 dark:bg-slate-800 text-teal-700 dark:text-teal-400 hover:bg-teal-50 border border-teal-300 dark:border-teal-700'
                            : 'bg-teal-600 hover:bg-teal-500 text-white shadow-xs'
                        }`}
                      >
                        {isAlreadyAdded ? '✓ Tambahkan Lagi' : '+ Pilih Obat Ini'}
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 3: LIVE HTML TABLE PREVIEW */}
          {activeTab === 'preview' && (
            <div className="space-y-4">
              <div className="p-3.5 bg-teal-50 dark:bg-slate-800/80 rounded-2xl border border-teal-200 dark:border-slate-700 text-xs text-teal-950 dark:text-slate-200 flex items-center justify-between">
                <span>👁️ <strong>Pratinjau Tabel HTML Rejimen Terapi Obat:</strong> Format klinis berbasis bukti (Evidence-Based Guidelines).</span>
                <span className="px-2.5 py-0.5 rounded-full bg-teal-600 text-white text-[10px] font-bold">KDIGO 2024 / ADA 2025</span>
              </div>

              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-teal-200 dark:border-slate-800 overflow-hidden shadow-xs">
                <div className="px-4 py-3 bg-gradient-to-r from-teal-600 to-emerald-600 text-white flex items-center justify-between">
                  <h4 className="text-xs font-bold flex items-center gap-2">
                    <span>💊</span>
                    <span>Tabel Rejimen Farmakoterapi Rekomendasi Terpilih</span>
                  </h4>
                  <span className="text-[10px] font-medium opacity-90">{items.length} Obat Terdaftar</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-teal-50 dark:bg-slate-800 text-teal-950 dark:text-slate-200 uppercase tracking-wider font-bold border-b border-teal-100 dark:border-slate-700 text-[11px]">
                      <tr>
                        <th className="px-4 py-3">Nama Obat & Golongan</th>
                        <th className="px-4 py-3">Dosis & Frekuensi</th>
                        <th className="px-4 py-3">Rute & Waktu</th>
                        <th className="px-4 py-3">Indikasi Klinis</th>
                        <th className="px-4 py-3">Penyesuaian Dosis Ginjal/Hepar</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-teal-100 dark:divide-slate-800 text-slate-900 dark:text-slate-100">
                      {items.map((item, idx) => (
                        <tr key={item.id} className={idx % 2 === 1 ? 'bg-slate-50/50 dark:bg-slate-850/40' : 'hover:bg-teal-50/40 dark:hover:bg-slate-800/40'}>
                          <td className="px-4 py-3 font-bold text-teal-950 dark:text-teal-300">
                            <div>{item.drug_name}</div>
                            <div className="text-[10px] font-normal text-slate-500 dark:text-slate-400">({item.class})</div>
                          </td>
                          <td className="px-4 py-3">
                            <span className="font-bold text-slate-900 dark:text-slate-100">{item.dosage}</span>
                            <div className="text-[11px] text-slate-500 dark:text-slate-400">{item.frequency}</div>
                          </td>
                          <td className="px-4 py-3">
                            <div>{item.route}</div>
                            <div className="text-[10px] italic text-slate-500 dark:text-slate-400">{item.timing}</div>
                          </td>
                          <td className="px-4 py-3 max-w-xs">{item.indication}</td>
                          <td className="px-4 py-3 max-w-xs">
                            <span className="px-2 py-0.5 rounded-md bg-amber-50 dark:bg-amber-950 text-amber-800 dark:text-amber-300 text-[10px] font-medium border border-amber-200 dark:border-amber-800">
                              {item.renal_dosing || 'Sesuai fungsi ginjal'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {clinicalGuidelineNote && (
                <div className="p-4 rounded-2xl bg-amber-50/80 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-700 text-xs text-amber-900 dark:text-amber-200 space-y-1">
                  <div className="font-bold flex items-center gap-1.5">
                    <span>🛡️</span>
                    <span>Pertimbangan Keamanan & Catatan Monitoring DPJP:</span>
                  </div>
                  <p className="leading-relaxed whitespace-pre-wrap">{clinicalGuidelineNote}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 bg-white dark:bg-slate-900 border-t border-emerald-100 dark:border-slate-800 flex items-center justify-between">
          <div className="text-xs text-slate-500 dark:text-slate-400">
            Total <strong className="text-slate-900 dark:text-slate-100">{items.length}</strong> jenis obat siap divalidasi ke dalam rekam medis & resume CPPT.
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-bold transition-colors"
            >
              Batal
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="px-5 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold flex items-center gap-1.5 transition-all shadow-md hover:shadow-lg"
            >
              <span>💾</span>
              <span>Simpan & Perbarui Rekomendasi Terapi</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
