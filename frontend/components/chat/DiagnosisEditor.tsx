'use client';

import React, { useState, useMemo } from 'react';

export interface DiagnosisItem {
  id: string;
  type: 'primary' | 'differential';
  diagnosis: string;
  icd10: string;
  confidence?: string;
  justification?: string;
  clinicalClues?: string;
}

interface DiagnosisEditorProps {
  initialContent: string;
  onSave: (updatedMarkdown: string) => void;
  onClose: () => void;
}

// Comprehensive ICD-10 Clinical Database
export const ICD10_DATABASE = [
  // Endokrin & Metabolik
  { code: 'E11.9', name: 'Type 2 Diabetes Mellitus without complications', indonesian: 'Diabetes Melitus Tipe 2 Tanpa Komplikasi', category: 'Endokrin' },
  { code: 'E11.40', name: 'Type 2 Diabetes Mellitus with diabetic neuropathy, unspecified', indonesian: 'Diabetes Melitus Tipe 2 dengan Neuropati Diabetik', category: 'Endokrin' },
  { code: 'E11.22', name: 'Type 2 Diabetes Mellitus with diabetic chronic kidney disease', indonesian: 'Diabetes Melitus Tipe 2 dengan Nefropati Diabetik / CKD', category: 'Endokrin' },
  { code: 'E11.65', name: 'Type 2 Diabetes Mellitus with hyperglycemia', indonesian: 'Diabetes Melitus Tipe 2 dengan Hiperglikemia Tidak Terkontrol', category: 'Endokrin' },
  { code: 'E10.9', name: 'Type 1 Diabetes Mellitus without complications', indonesian: 'Diabetes Melitus Tipe 1 Tanpa Komplikasi', category: 'Endokrin' },
  { code: 'E78.5', name: 'Hyperlipidemia, unspecified', indonesian: 'Hiperlipidemia / Dislipidemia', category: 'Metabolik' },
  { code: 'E78.0', name: 'Pure Hypercholesterolemia', indonesian: 'Hiperkolesterolemia Murni', category: 'Metabolik' },
  { code: 'E03.9', name: 'Hypothyroidism, unspecified', indonesian: 'Hipotiroidisme', category: 'Endokrin' },
  { code: 'E05.90', name: 'Thyrotoxicosis / Hyperthyroidism', indonesian: 'Tirotoksikosis / Hipertiroidisme', category: 'Endokrin' },
  
  // Kardiovaskular
  { code: 'I10', name: 'Essential (primary) hypertension', indonesian: 'Hipertensi Primer / Esensial', category: 'Kardiovaskular' },
  { code: 'I11.9', name: 'Hypertensive heart disease without heart failure', indonesian: 'Penyakit Jantung Hipertensi (HHD)', category: 'Kardiovaskular' },
  { code: 'I12.9', name: 'Hypertensive chronic kidney disease with stage 1-4 CKD', indonesian: 'Penyakit Ginjal Hipertensi', category: 'Kardiovaskular' },
  { code: 'I20.0', name: 'Unstable Angina Pectoris (UAP)', indonesian: 'Angina Pektoris Tidak Stabil', category: 'Kardiovaskular' },
  { code: 'I20.8', name: 'Other forms of Angina Pectoris / Stable Angina (CCS II)', indonesian: 'Angina Pektoris Stabil / Chronic Coronary Syndrome', category: 'Kardiovaskular' },
  { code: 'I24.9', name: 'Acute ischemic heart disease, unspecified', indonesian: 'Sindrom Koroner Akut (SKA)', category: 'Kardiovaskular' },
  { code: 'I25.10', name: 'Atherosclerotic heart disease of native coronary artery (CAD)', indonesian: 'Penyakit Jantung Koroner (CAD post-PCI)', category: 'Kardiovaskular' },
  { code: 'I50.9', name: 'Heart Failure, unspecified', indonesian: 'Gagal Jantung Kongestif (CHF)', category: 'Kardiovaskular' },
  { code: 'I48.91', name: 'Unspecified Atrial Fibrillation', indonesian: 'Fibrilasi Atrium (AF)', category: 'Kardiovaskular' },
  { code: 'T82.855A', name: 'Stenosis of coronary artery stent (In-stent restenosis)', indonesian: 'Restenosis Stent Koroner (In-Stent Restenosis)', category: 'Kardiovaskular' },

  // Gastrointestinal
  { code: 'K29.1', name: 'Other acute gastritis / Chronic Erosive Gastritis', indonesian: 'Gastritis Kronis Erosif', category: 'Gastrointestinal' },
  { code: 'K29.7', name: 'Gastritis, unspecified', indonesian: 'Gastritis Akut / Dispepsia', category: 'Gastrointestinal' },
  { code: 'K30', name: 'Functional Dyspepsia', indonesian: 'Dispepsia Fungsional', category: 'Gastrointestinal' },
  { code: 'K21.9', name: 'Gastroesophageal Reflux Disease without esophagitis', indonesian: 'Penyakit Refluks Gastroesofagus (GERD)', category: 'Gastrointestinal' },
  { code: 'K25.9', name: 'Gastric Ulcer, unspecified', indonesian: 'Ulkus Gaster / Tukak Lambung', category: 'Gastrointestinal' },
  { code: 'K26.9', name: 'Duodenal Ulcer, unspecified', indonesian: 'Ulkus Duodeni / Tukak Duodenum', category: 'Gastrointestinal' },
  { code: 'B96.81', name: 'Helicobacter pylori as the cause of diseases classified elsewhere', indonesian: 'Gastropati Terkait Infeksi Helicobacter pylori', category: 'Infeksi/GI' },
  { code: 'K92.0', name: 'Hematemesis', indonesian: 'Hematemesis (Muntah Darah)', category: 'Gastrointestinal' },
  { code: 'K92.1', name: 'Melena', indonesian: 'Melena (BAB Hitam)', category: 'Gastrointestinal' },
  { code: 'K76.0', name: 'Fatty (change of) liver, not elsewhere classified (NAFLD)', indonesian: 'Perlemakan Hati Non-Alkoholik (NAFLD)', category: 'Hepatologi' },

  // Ginjal & Saluran Kemih
  { code: 'N18.31', name: 'Chronic Kidney Disease, stage 3a', indonesian: 'Penyakit Ginjal Kronis (CKD) Stadium 3a (eGFR 45-59)', category: 'Nefrologi' },
  { code: 'N18.32', name: 'Chronic Kidney Disease, stage 3b', indonesian: 'Penyakit Ginjal Kronis (CKD) Stadium 3b (eGFR 30-44)', category: 'Nefrologi' },
  { code: 'N18.4', name: 'Chronic Kidney Disease, stage 4 (severe)', indonesian: 'Penyakit Ginjal Kronis (CKD) Stadium 4 (eGFR 15-29)', category: 'Nefrologi' },
  { code: 'N18.5', name: 'Chronic Kidney Disease, stage 5 (ESRD)', indonesian: 'Penyakit Ginjal Kronis Stadium Akhir (Gagal Ginjal Terminal)', category: 'Nefrologi' },
  { code: 'N18.9', name: 'Chronic Kidney Disease, unspecified', indonesian: 'Penyakit Ginjal Kronik (CKD)', category: 'Nefrologi' },
  { code: 'N17.9', name: 'Acute Kidney Injury, unspecified', indonesian: 'Gangguan Ginjal Akut (AKI)', category: 'Nefrologi' },
  { code: 'N39.0', name: 'Urinary Tract Infection, site not specified', indonesian: 'Infeksi Saluran Kemih (ISK)', category: 'Nefrologi' },

  // Hematologi & Sistemik
  { code: 'D50.9', name: 'Iron Deficiency Anemia, unspecified', indonesian: 'Anemia Defisiensi Besi (Mikrositik Hipokromik)', category: 'Hematologi' },
  { code: 'D50.0', name: 'Iron Deficiency Anemia secondary to blood loss (chronic)', indonesian: 'Anemia Defisiensi Besi ec Perdarahan Kronis', category: 'Hematologi' },
  { code: 'D64.9', name: 'Anemia, unspecified', indonesian: 'Anemia', category: 'Hematologi' },

  // Respirasi
  { code: 'J18.9', name: 'Pneumonia, unspecified organism', indonesian: 'Pneumonia Komunitas / CAP', category: 'Respirasi' },
  { code: 'J44.9', name: 'Chronic Obstructive Pulmonary Disease, unspecified', indonesian: 'Penyakit Paru Obstruktif Kronik (PPOK)', category: 'Respirasi' },
  { code: 'J45.909', name: 'Unspecified asthma, uncomplicated', indonesian: 'Asma Bronkial', category: 'Respirasi' },
  { code: 'J06.9', name: 'Acute upper respiratory infection, unspecified', indonesian: 'Infeksi Saluran Pernapasan Atas (ISPA)', category: 'Respirasi' },

  // Saraf
  { code: 'I63.9', name: 'Cerebral infarction, unspecified (Ischemic Stroke)', indonesian: 'Stroke Iskemik Akut / Infark Serebri', category: 'Neurologi' },
  { code: 'G45.9', name: 'Transient Cerebral Ischemic Attack, unspecified (TIA)', indonesian: 'Serangan Iskemik Transien (TIA)', category: 'Neurologi' },
  { code: 'G44.209', name: 'Tension-type headache, unspecified', indonesian: 'Tension Type Headache (TTH)', category: 'Neurologi' },
  { code: 'M54.50', name: 'Low Back Pain, unspecified', indonesian: 'Nyeri Punggung Bawah (LBP)', category: 'Muskuloskeletal' },
  { code: 'M54.16', name: 'Radiculopathy, lumbar region', indonesian: 'Radikulopati Lumbal / HNP', category: 'Muskuloskeletal' }
];

export default function DiagnosisEditor({
  initialContent,
  onSave,
  onClose
}: DiagnosisEditorProps) {
  // Parse initial primary & differentials from content or supply defaults
  const [items, setItems] = useState<DiagnosisItem[]>(() => {
    const list: DiagnosisItem[] = [];
    
    // Check if content matches Gastritis
    if (initialContent.toLowerCase().includes('gastritis') || initialContent.toLowerCase().includes('k29')) {
      list.push({
        id: '1',
        type: 'primary',
        diagnosis: 'Gastritis Kronis Erosif & Dispepsia Fungsional',
        icd10: 'K29.1 / K30',
        confidence: 'High (94%)',
        justification: 'Nyeri epigastrium perih terbakar, mual, riwayat analgetik bebas, dan riwayat perdarahan ringan.'
      });
      list.push({
        id: '2',
        type: 'primary',
        diagnosis: 'Anemia Defisiensi Besi Mikrositik Hipokromik',
        icd10: 'D50.9',
        confidence: 'High (91%)',
        justification: 'Hemoglobin 10.4 g/dL, MCV 74 fL, Serum Ferritin 18 ng/mL, dan konjungtiva anemis.'
      });
      list.push({
        id: '3',
        type: 'differential',
        diagnosis: 'Peptic Ulcer Disease (Ulkus Gaster / Duodeni)',
        icd10: 'K25.9 / K26.9',
        clinicalClues: 'Waspadai tanda ulserasi mukosa jika nyeri menetap atau terjadi melena/hematemesis.'
      });
      list.push({
        id: '4',
        type: 'differential',
        diagnosis: 'Helicobacter pylori-associated Gastropathy',
        icd10: 'B96.81',
        clinicalClues: 'Dapat dievaluasi melalui urea breath test (UBT) atau biopsi endoskopi.'
      });
    } else if (initialContent.toLowerCase().includes('angina') || initialContent.toLowerCase().includes('i20') || initialContent.toLowerCase().includes('jantung')) {
      list.push({
        id: '1',
        type: 'primary',
        diagnosis: 'Angina Pectoris Stabil (CAD Post-PCI LAD CCS Class II)',
        icd10: 'I20.8',
        confidence: 'High (89%)',
        justification: 'Rasa berat di dada saat menaiki tangga cepat yang mereda spontan dengan istirahat.'
      });
      list.push({
        id: '2',
        type: 'differential',
        diagnosis: 'In-stent Restenosis / De Novo Coronary Lesion',
        icd10: 'T82.855A / I25.10',
        clinicalClues: 'Iskemia berulang pasca intervensi koroner perkutan (PCI DES).'
      });
      list.push({
        id: '3',
        type: 'differential',
        diagnosis: 'Gastroesophageal Reflux Disease (GERD)',
        icd10: 'K21.9',
        clinicalClues: 'Rasa panas terbakar di epigastrium menjalar ke retrosternal.'
      });
    } else {
      // Default / DM2 Vance
      list.push({
        id: '1',
        type: 'primary',
        diagnosis: 'Type 2 Diabetes Mellitus with Diabetic Neuropathy & Nephropathy',
        icd10: 'E11.40 / E11.22',
        confidence: 'High (92%)',
        justification: 'Keluhan nokturia, polidipsia, kesemutan parestesia bilateral distal, dan HbA1c 7.2%.'
      });
      list.push({
        id: '2',
        type: 'differential',
        diagnosis: 'Chronic Kidney Disease Stage 3a (progression risk)',
        icd10: 'N18.31',
        clinicalClues: 'Penurunan eGFR 58 mL/min/1.73m² dan mikroalbuminuria uACR 120 mg/g.'
      });
      list.push({
        id: '3',
        type: 'differential',
        diagnosis: 'Essential (primary) Hypertension Stage 1',
        icd10: 'I10',
        clinicalClues: 'Tekanan darah 140/90 mmHg pada evaluasi klinis berkala.'
      });
    }
    return list;
  });

  const [searchTerm, setSearchTerm] = useState('');
  const [activeTargetId, setActiveTargetId] = useState<string | null>(null);
  const [workups, setWorkups] = useState<string>(
    '1. Pemeriksaan Darah Lengkap (CBC) & Profil Besi Serum (Ferritin, SI, TIBC)\n2. Urea Breath Test (UBT) / H. pylori Antigen\n3. EGD Endoskopi Saluran Cerna Atas berkala'
  );

  // Search Results
  const filteredICDCodes = useMemo(() => {
    if (!searchTerm.trim()) return ICD10_DATABASE.slice(0, 8);
    const q = searchTerm.toLowerCase();
    return ICD10_DATABASE.filter(
      item =>
        item.code.toLowerCase().includes(q) ||
        item.name.toLowerCase().includes(q) ||
        item.indonesian.toLowerCase().includes(q) ||
        item.category.toLowerCase().includes(q)
    );
  }, [searchTerm]);

  const handleSelectICD = (item: typeof ICD10_DATABASE[0]) => {
    if (!activeTargetId) return;
    setItems(prev =>
      prev.map(dx => {
        if (dx.id === activeTargetId) {
          return {
            ...dx,
            diagnosis: item.indonesian || item.name,
            icd10: item.code
          };
        }
        return dx;
      })
    );
    setActiveTargetId(null);
    setSearchTerm('');
  };

  // Prepend new items so they are ALWAYS placed at the very top of the list
  const handleAddItem = (type: 'primary' | 'differential') => {
    const newItemId = Date.now().toString();
    const newItem: DiagnosisItem = {
      id: newItemId,
      type,
      diagnosis: type === 'primary' ? 'Diagnosis Primer Baru' : 'Diagnosis Banding Baru',
      icd10: 'Z00.00',
      confidence: type === 'primary' ? 'High (90%)' : undefined,
      justification: type === 'primary' ? 'Justifikasi klinis dari evaluasi DPJP.' : undefined,
      clinicalClues: type === 'differential' ? 'Petunjuk pembanding klinis.' : undefined
    };
    setItems(prev => [newItem, ...prev]);
    setActiveTargetId(newItemId);
  };

  const handleRemoveItem = (id: string) => {
    setItems(prev => prev.filter(dx => dx.id !== id));
    if (activeTargetId === id) setActiveTargetId(null);
  };

  const handleGenerateAndSave = () => {
    const primaries = items.filter(d => d.type === 'primary');
    const differentials = items.filter(d => d.type === 'differential');

    let md = `## 🎯 Rekomendasi Diagnosis Klinis & ICD-10 (Telah Divalidasi Dokter)\n\n`;
    md += `> ✅ **Status:** Diagnosis kerja telah ditinjau dan diperbarui oleh DPJP pada ${new Date().toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}\n\n`;

    if (primaries.length > 0) {
      md += `### 📌 Diagnosis Kerja (Primer) Terpilih\n`;
      md += `| Diagnosis Kerja | Kode ICD-10 | Keyakinan Klinis | Justifikasi Medis Dokter |\n`;
      md += `| :--- | :--- | :--- | :--- |\n`;
      for (const p of primaries) {
        md += `| **${p.diagnosis}** | \`${p.icd10}\` | **${p.confidence || 'Tinggi (Terkonfirmasi)'}** | ${p.justification || '-'} |\n`;
      }
      md += `\n`;
    }

    if (differentials.length > 0) {
      md += `### ⚖️ Diagnosis Banding (Differential Diagnoses)\n`;
      md += `| Diagnosis Banding | Kode ICD-10 | Petunjuk Klinis / Indikator Pembanding |\n`;
      md += `| :--- | :--- | :--- |\n`;
      for (const d of differentials) {
        md += `| **${d.diagnosis}** | \`${d.icd10}\` | ${d.clinicalClues || '-'} |\n`;
      }
      md += `\n`;
    }

    if (workups.trim()) {
      md += `### 🔬 Rencana Pemeriksaan Penunjang Lanjutan (Workup)\n`;
      md += `${workups.trim()}\n\n`;
    }

    md += `---\n*(⚠️ **Clinical Disclaimer**: Validasi kode ICD-10 telah disetujui dokter penanggung jawab untuk pencatatan RME SIMRS.)*`;

    onSave(md);
  };

  const primaryItems = items.filter(d => d.type === 'primary');
  const differentialItems = items.filter(d => d.type === 'differential');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-black/60 backdrop-blur-xs animate-in fade-in duration-150">
      <div className="bg-white dark:bg-slate-900 border border-emerald-300 dark:border-slate-700 rounded-3xl w-full max-w-6xl max-h-[92vh] shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-emerald-200 dark:border-slate-800 bg-emerald-50/90 dark:bg-slate-800/90">
          <div className="flex items-center gap-2.5">
            <span className="text-2xl">🎯</span>
            <div>
              <h2 className="text-base font-bold text-emerald-950 dark:text-white">
                Editor Diagnosis & Pencarian Kode ICD-10
              </h2>
              <p className="text-xs text-emerald-700 dark:text-slate-400">
                Sesuaikan diagnosis primer dan banding berdampingan (2 Kolom). Penambahan baru akan otomatis berada di paling atas.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-xl hover:bg-emerald-200/50 dark:hover:bg-slate-700 text-emerald-800 dark:text-slate-300 text-sm font-bold"
          >
            ✕
          </button>
        </div>

        {/* Body Content */}
        <div className="p-5 sm:p-6 overflow-y-auto space-y-6 text-xs flex-1">
          {/* ICD-10 Search Bar Component */}
          <div className="p-4 rounded-2xl bg-emerald-100/60 dark:bg-slate-800/60 border border-emerald-200 dark:border-slate-700 space-y-3">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <label className="text-xs font-bold text-emerald-900 dark:text-emerald-300 flex items-center gap-1.5">
                <span>🔍</span>
                <span>Pencarian Master Kode ICD-10 Real-Time:</span>
              </label>
              {activeTargetId ? (
                <span className="px-3 py-1 rounded-full bg-amber-500 text-white font-bold text-[10px] animate-pulse flex items-center gap-1">
                  <span>🎯</span>
                  <span>Kolom Target Aktif: Klik salah satu kode di bawah untuk mengisi</span>
                </span>
              ) : (
                <span className="text-[10px] text-emerald-700 dark:text-slate-400 italic">
                  💡 Klik ikon 🔎 pada baris diagnosis untuk memilih target pengisian kode ICD-10
                </span>
              )}
            </div>

            <div className="relative">
              <input
                type="text"
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                placeholder="Cari nama penyakit atau kode ICD (contoh: Gastritis, E11, Hipertensi, K29, Anemia, Jantung, CKD)..."
                className="w-full pl-9 pr-8 py-2 rounded-xl bg-white dark:bg-slate-900 border border-emerald-300 dark:border-slate-700 text-xs font-medium text-emerald-950 dark:text-slate-100 placeholder:text-emerald-600/60 dark:placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-2xs"
              />
              <span className="absolute left-3 top-2.5 text-emerald-600 dark:text-slate-400">🔎</span>
              {searchTerm && (
                <button
                  type="button"
                  onClick={() => setSearchTerm('')}
                  className="absolute right-2.5 top-2 text-slate-400 hover:text-slate-600 font-bold text-xs"
                >
                  ✕
                </button>
              )}
            </div>

            {/* Quick Result Chips */}
            <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2">
                {filteredICDCodes.map(icd => (
                  <div
                    key={icd.code}
                    onClick={() => handleSelectICD(icd)}
                    className={`p-2 rounded-xl border transition-all cursor-pointer flex flex-col justify-between ${
                      activeTargetId
                        ? 'bg-white dark:bg-slate-900 border-emerald-400 hover:border-emerald-600 hover:bg-emerald-50 dark:hover:bg-slate-800 shadow-2xs'
                        : 'bg-white/70 dark:bg-slate-900/70 border-emerald-100 dark:border-slate-800 opacity-90'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1 mb-1">
                      <span className="font-mono font-bold text-emerald-700 dark:text-emerald-400 text-xs px-1.5 py-0.5 rounded bg-emerald-100 dark:bg-slate-800">
                        {icd.code}
                      </span>
                      <span className="text-[9px] text-slate-500 dark:text-slate-400 font-medium truncate">
                        {icd.category}
                      </span>
                    </div>
                    <p className="font-semibold text-emerald-950 dark:text-slate-200 text-[11px] line-clamp-1">
                      {icd.indonesian}
                    </p>
                    <p className="text-[9px] text-slate-500 dark:text-slate-400 italic line-clamp-1">
                      {icd.name}
                    </p>
                    {activeTargetId && (
                      <span className="mt-1 text-[9px] font-bold text-emerald-600 dark:text-emerald-400 underline">
                        ➕ Terapkan
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 2-COLUMN LAYOUT: Left = Primary Diagnoses, Right = Differential Diagnoses */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* COLUMN 1: Primary Diagnoses (Kiri) */}
            <div className="space-y-3 bg-emerald-50/40 dark:bg-slate-900/40 p-4 rounded-2xl border border-emerald-200/80 dark:border-slate-800 flex flex-col">
              <div className="flex items-center justify-between pb-2 border-b border-emerald-200/60 dark:border-slate-800">
                <div className="flex items-center gap-2">
                  <span className="text-base">📌</span>
                  <h3 className="font-bold text-emerald-950 dark:text-emerald-300 text-xs">
                    Diagnosis Kerja (Primer)
                  </h3>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-200/80 dark:bg-emerald-900/60 text-emerald-900 dark:text-emerald-200 font-bold text-[10px]">
                    {primaryItems.length}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => handleAddItem('primary')}
                  className="px-3 py-1 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[11px] shadow-2xs flex items-center gap-1 transition-all"
                >
                  <span>➕</span>
                  <span>Tambah Primer</span>
                </button>
              </div>

              {primaryItems.length === 0 ? (
                <p className="text-center py-6 text-emerald-600/70 dark:text-slate-500 italic text-[11px]">
                  Belum ada diagnosis primer. Klik tombol di atas untuk menambahkan.
                </p>
              ) : (
                <div className="space-y-3 max-h-[480px] overflow-y-auto pr-1">
                  {primaryItems.map(item => (
                    <div
                      key={item.id}
                      className={`p-3.5 rounded-2xl border transition-all ${
                        activeTargetId === item.id
                          ? 'border-emerald-500 ring-2 ring-emerald-500/20 bg-emerald-50/80 dark:bg-slate-800/90 shadow-md'
                          : 'border-emerald-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-2xs'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 dark:text-emerald-400">
                          📌 Diagnosis Primer
                        </span>
                        <button
                          type="button"
                          onClick={() => handleRemoveItem(item.id)}
                          title="Hapus baris ini"
                          className="p-1 text-rose-500 hover:bg-rose-100 dark:hover:bg-slate-800 rounded-lg text-xs"
                        >
                          🗑️
                        </button>
                      </div>

                      <div className="space-y-2">
                        <div>
                          <label className="block text-[10px] font-bold text-emerald-900 dark:text-slate-300 mb-0.5">
                            Nama Diagnosis:
                          </label>
                          <input
                            type="text"
                            value={item.diagnosis}
                            onChange={e =>
                              setItems(prev =>
                                prev.map(d => (d.id === item.id ? { ...d, diagnosis: e.target.value } : d))
                              )
                            }
                            className="w-full px-2.5 py-1.5 rounded-xl border border-emerald-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-semibold text-emerald-950 dark:text-slate-100 focus:outline-none focus:border-emerald-500"
                          />
                        </div>

                        <div className="grid grid-cols-12 gap-2">
                          <div className="col-span-7">
                            <label className="block text-[10px] font-bold text-emerald-900 dark:text-slate-300 mb-0.5">
                              Kode ICD-10:
                            </label>
                            <div className="flex gap-1">
                              <input
                                type="text"
                                value={item.icd10}
                                onChange={e =>
                                  setItems(prev =>
                                    prev.map(d => (d.id === item.id ? { ...d, icd10: e.target.value } : d))
                                  )
                                }
                                className="w-full px-2.5 py-1.5 rounded-xl font-mono border border-emerald-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-bold text-emerald-800 dark:text-emerald-300 focus:outline-none focus:border-emerald-500"
                              />
                              <button
                                type="button"
                                onClick={() => setActiveTargetId(activeTargetId === item.id ? null : item.id)}
                                title="Pilih target pencarian ICD-10"
                                className={`px-2 rounded-xl text-xs font-bold transition-colors ${
                                  activeTargetId === item.id
                                    ? 'bg-amber-500 text-white'
                                    : 'bg-emerald-100 dark:bg-slate-800 text-emerald-800 dark:text-slate-200 hover:bg-emerald-200'
                                }`}
                              >
                                🔎
                              </button>
                            </div>
                          </div>

                          <div className="col-span-5">
                            <label className="block text-[10px] font-bold text-emerald-900 dark:text-slate-300 mb-0.5">
                              Keyakinan AI:
                            </label>
                            <input
                              type="text"
                              value={item.confidence || 'High (90%)'}
                              onChange={e =>
                                setItems(prev =>
                                  prev.map(d => (d.id === item.id ? { ...d, confidence: e.target.value } : d))
                                )
                              }
                              className="w-full px-2.5 py-1.5 rounded-xl border border-emerald-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs text-emerald-950 dark:text-slate-100 focus:outline-none focus:border-emerald-500"
                            />
                          </div>
                        </div>

                        <div>
                          <label className="block text-[10px] font-bold text-emerald-900 dark:text-slate-300 mb-0.5">
                            Justifikasi Klinis Terpadu:
                          </label>
                          <textarea
                            rows={2}
                            value={item.justification || ''}
                            onChange={e =>
                              setItems(prev =>
                                prev.map(d => (d.id === item.id ? { ...d, justification: e.target.value } : d))
                              )
                            }
                            className="w-full px-2.5 py-1.5 rounded-xl border border-emerald-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs text-emerald-950 dark:text-slate-100 focus:outline-none focus:border-emerald-500"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* COLUMN 2: Differential Diagnoses (Kanan) */}
            <div className="space-y-3 bg-slate-50/50 dark:bg-slate-900/40 p-4 rounded-2xl border border-emerald-200/80 dark:border-slate-800 flex flex-col">
              <div className="flex items-center justify-between pb-2 border-b border-emerald-200/60 dark:border-slate-800">
                <div className="flex items-center gap-2">
                  <span className="text-base">⚖️</span>
                  <h3 className="font-bold text-emerald-950 dark:text-emerald-300 text-xs">
                    Diagnosis Banding (Differentials)
                  </h3>
                  <span className="px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-800 dark:text-slate-300 font-bold text-[10px]">
                    {differentialItems.length}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => handleAddItem('differential')}
                  className="px-3 py-1 rounded-xl bg-slate-700 hover:bg-slate-600 dark:bg-slate-700 dark:hover:bg-slate-600 text-white font-bold text-[11px] shadow-2xs flex items-center gap-1 transition-all"
                >
                  <span>➕</span>
                  <span>Tambah Banding</span>
                </button>
              </div>

              {differentialItems.length === 0 ? (
                <p className="text-center py-6 text-slate-500 italic text-[11px]">
                  Belum ada diagnosis banding. Klik tombol di atas untuk menambahkan.
                </p>
              ) : (
                <div className="space-y-3 max-h-[480px] overflow-y-auto pr-1">
                  {differentialItems.map(item => (
                    <div
                      key={item.id}
                      className={`p-3.5 rounded-2xl border transition-all ${
                        activeTargetId === item.id
                          ? 'border-emerald-500 ring-2 ring-emerald-500/20 bg-emerald-50/80 dark:bg-slate-800/90 shadow-md'
                          : 'border-emerald-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-2xs'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400">
                          ⚖️ Diagnosis Banding
                        </span>
                        <button
                          type="button"
                          onClick={() => handleRemoveItem(item.id)}
                          title="Hapus baris ini"
                          className="p-1 text-rose-500 hover:bg-rose-100 dark:hover:bg-slate-800 rounded-lg text-xs"
                        >
                          🗑️
                        </button>
                      </div>

                      <div className="space-y-2">
                        <div>
                          <label className="block text-[10px] font-bold text-slate-700 dark:text-slate-300 mb-0.5">
                            Nama Diagnosis Banding:
                          </label>
                          <input
                            type="text"
                            value={item.diagnosis}
                            onChange={e =>
                              setItems(prev =>
                                prev.map(d => (d.id === item.id ? { ...d, diagnosis: e.target.value } : d))
                              )
                            }
                            className="w-full px-2.5 py-1.5 rounded-xl border border-emerald-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-semibold text-emerald-950 dark:text-slate-100 focus:outline-none focus:border-emerald-500"
                          />
                        </div>

                        <div>
                          <label className="block text-[10px] font-bold text-slate-700 dark:text-slate-300 mb-0.5">
                            Kode ICD-10:
                          </label>
                          <div className="flex gap-1">
                            <input
                              type="text"
                              value={item.icd10}
                              onChange={e =>
                                setItems(prev =>
                                  prev.map(d => (d.id === item.id ? { ...d, icd10: e.target.value } : d))
                                )
                              }
                              className="w-full px-2.5 py-1.5 rounded-xl font-mono border border-emerald-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-bold text-emerald-800 dark:text-emerald-300 focus:outline-none focus:border-emerald-500"
                            />
                            <button
                              type="button"
                              onClick={() => setActiveTargetId(activeTargetId === item.id ? null : item.id)}
                              title="Pilih target pencarian ICD-10"
                              className={`px-2 rounded-xl text-xs font-bold transition-colors ${
                                activeTargetId === item.id
                                  ? 'bg-amber-500 text-white'
                                  : 'bg-emerald-100 dark:bg-slate-800 text-emerald-800 dark:text-slate-200 hover:bg-emerald-200'
                              }`}
                            >
                              🔎
                            </button>
                          </div>
                        </div>

                        <div>
                          <label className="block text-[10px] font-bold text-slate-700 dark:text-slate-300 mb-0.5">
                            Petunjuk Klinis / Indikator Pembanding:
                          </label>
                          <textarea
                            rows={2}
                            value={item.clinicalClues || ''}
                            onChange={e =>
                              setItems(prev =>
                                prev.map(d => (d.id === item.id ? { ...d, clinicalClues: e.target.value } : d))
                              )
                            }
                            className="w-full px-2.5 py-1.5 rounded-xl border border-emerald-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs text-emerald-950 dark:text-slate-100 focus:outline-none focus:border-emerald-500"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Section: Workup Instructions */}
          <div>
            <label className="block text-[11px] font-bold text-emerald-900 dark:text-emerald-300 mb-1">
              🔬 Rencana Pemeriksaan Penunjang Lanjutan (Workup):
            </label>
            <textarea
              rows={3}
              value={workups}
              onChange={e => setWorkups(e.target.value)}
              className="w-full px-3.5 py-2 rounded-xl border border-emerald-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs leading-relaxed text-emerald-950 dark:text-slate-100 focus:outline-none focus:border-emerald-500 font-mono"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-emerald-200 dark:border-slate-800 bg-emerald-50/50 dark:bg-slate-800/50">
          <p className="text-[10px] text-emerald-700 dark:text-slate-400 font-medium">
            💡 Perubahan diagnosis dan kode ICD-10 akan diperbarui pada pesan konsultasi setelah disimpan.
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl border border-emerald-300 dark:border-slate-700 text-emerald-900 dark:text-slate-200 hover:bg-emerald-100 dark:hover:bg-slate-700 font-semibold text-xs"
            >
              Batal
            </button>
            <button
              type="button"
              onClick={handleGenerateAndSave}
              className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <span>📤</span>
              <span>Kirim ke SIMRS</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
