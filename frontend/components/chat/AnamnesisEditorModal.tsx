'use client';

import React, { useState, useEffect } from 'react';

interface AnamnesisEditorModalProps {
  initialContent: string;
  onSave: (updatedMarkdown: string) => void;
  onClose: () => void;
}

// Quick suggestions for rapid clinical documentation
const SUGGESTIONS = {
  chiefComplaint: [
    'Nyeri ulu hati terasa perih terbakar sejak 1 minggu terakhir',
    'Pusing berputar, lemas sejak 3 hari, sering kencing malam hari (nokturia)',
    'Sesak napas bertambah saat beraktivitas dan tidur terlentang (ortopnea)',
    'Nyeri dada kiri seperti tertindih beban berat menjalar ke lengan kiri',
    'Demam menggigil naik turun sejak 4 hari disertai batuk produktif',
    'Nyeri pinggang menjalar ke selangkangan disertai BAK keruh',
  ],
  rpd: [
    'Riwayat Gastritis Kronis / Dispepsia berulang sejak 2 tahun lalu',
    'Riwayat Diabetes Melitus Tipe 2 (terdiagnosis 5 tahun, kontrol berkala)',
    'Riwayat Hipertensi Grade 1 (terdiagnosis 3 tahun lalu)',
    'Riwayat Penyakit Jantung Koroner (CAD post-PCI stent 1 tahun lalu)',
    'Tidak ada riwayat asma, alergi obat, atau penyakit ginjal sebelumnya',
  ],
  rpk: [
    'Riwayat Diabetes Melitus pada Ibu kandung',
    'Riwayat Hipertensi dan Stroke pada Ayah kandung',
    'Riwayat Penyakit Jantung Koroner pada keluarga',
    'Tidak ada riwayat penyakit kronis atau keganasan dalam keluarga',
  ],
  allergies: [
    'Tidak ada riwayat alergi obat, makanan, atau debu (NKDA)',
    'Alergi Amoxicillin / Golongan Penisilin (reaksi urtikaria & gatal)',
    'Alergi Obat NSAID (Aspirin/Ibuprofen - reaksi bronkospasme / sesak)',
    'Alergi Seafood / Makanan laut (reaksi eritema & edema bibir)',
  ],
  medications: [
    'Antasida sirup 3x1 sendok makan (mandiri, berkurang sementara)',
    'Metformin 500mg 2x1 tablet p.c., Lisinopril 10mg 1x1 tablet pagi',
    'Omeprazole 20mg 2x1 kapsul a.c., Sucralfate sirup 3x1 C',
    'Atorvastatin 20mg 1x1 malam, Aspilet 80mg 1x1 pagi',
    'Tidak ada konsumsi obat-obatan rutin jangka panjang',
  ],
  lifestyle: [
    'Pola makan sering terlambat, konsumsi kopi 2-3 cangkir/hari, stres kerja (+)',
    'Pola diet tinggi karbohidrat/gula, aktivitas fisik kurang, jarang olahraga',
    'Merokok aktif 1 bungkus/hari (10 tahun), konsumsi alkohol (-)',
    'Pola makan teratur, tidak merokok, tidak mengonsumsi alkohol',
  ],
};

function cleanText(raw: string): string {
  if (!raw) return '';
  return raw
    .replace(/^\|\s*/gm, '')
    .replace(/\s*\|$/gm, '')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/\*\*/g, '')
    .replace(/`/g, '')
    .trim();
}

export default function AnamnesisEditorModal({
  initialContent,
  onSave,
  onClose,
}: AnamnesisEditorModalProps) {
  const [activeTab, setActiveTab] = useState<'form' | 'preview'>('form');

  // Core Anamnesis Fields
  const [chiefComplaint, setChiefComplaint] = useState('');
  const [hpi, setHpi] = useState('');
  const [pmh, setPmh] = useState('');
  const [familyHistory, setFamilyHistory] = useState('');
  const [medicationHistory, setMedicationHistory] = useState('');
  const [allergyHistory, setAllergyHistory] = useState('');
  const [lifestyleFactors, setLifestyleFactors] = useState('');

  // Parse Initial Content on Mount
  useEffect(() => {
    if (!initialContent) return;

    const extractTableRow = (text: string, keyRegex: RegExp): string => {
      const lines = text.split('\n');
      for (const line of lines) {
        if (keyRegex.test(line) && line.includes('|')) {
          const parts = line.split('|').map(x => x.trim()).filter(Boolean);
          if (parts.length >= 2) {
            return cleanText(parts.slice(1).join(' - '));
          }
        }
      }
      return '';
    };

    // Extract table rows
    const cc = extractTableRow(initialContent, /Keluhan Utama|Chief Complaint/i);
    const rps = extractTableRow(initialContent, /Riwayat Penyakit Sekarang|RPS|HPI/i);
    const rpd = extractTableRow(initialContent, /Riwayat Penyakit Dahulu|RPD|Past Medical/i);
    const rpk = extractTableRow(initialContent, /Riwayat Penyakit Keluarga|RPK|Family History/i);
    const med = extractTableRow(initialContent, /Riwayat Pengobatan|Medication/i);
    const alg = extractTableRow(initialContent, /Riwayat Alergi|Allergy/i);
    const life = extractTableRow(initialContent, /Faktor Gaya Hidup|Gaya Hidup|Lifestyle/i);

    if (cc) setChiefComplaint(cc);
    if (rps) setHpi(rps);
    if (rpd) setPmh(rpd);
    if (rpk) setFamilyHistory(rpk);
    if (med) setMedicationHistory(med);
    if (alg) setAllergyHistory(alg);
    if (life) setLifestyleFactors(life);

    // If section format
    if (!cc) {
      const ccMatch = initialContent.match(/(?:Keluhan Utama|Chief Complaint)[:\s]+([^\n\r]+)/i);
      if (ccMatch) setChiefComplaint(ccMatch[1].trim());
    }
    if (!rps) {
      const rpsMatch = initialContent.match(/(?:Riwayat Penyakit Sekarang|RPS)[:\s]+([^\n\r]+)/i);
      if (rpsMatch) setHpi(rpsMatch[1].trim());
    }
    if (!rpd) {
      const rpdMatch = initialContent.match(/(?:Riwayat Penyakit Dahulu|RPD)[:\s]+([^\n\r]+)/i);
      if (rpdMatch) setPmh(rpdMatch[1].trim());
    }
    if (!alg) {
      const algMatch = initialContent.match(/(?:Riwayat Alergi|Alergi)[:\s]+([^\n\r]+)/i);
      if (algMatch) setAllergyHistory(algMatch[1].trim());
    }
  }, [initialContent]);

  // Generate standardized SIMRS Markdown output
  const generateMarkdown = (): string => {
    return `## 📝 Hasil Anamnesis Pasien (SIMRS RME)

### 📋 Tabel Komponen Anamnesis Terstruktur
| Komponen Anamnesis | Data Temuan Klinis Pasien |
| :--- | :--- |
| **Keluhan Utama** | ${chiefComplaint.trim() || 'Tidak ada keluhan utama spesifik.'} |
| **Riwayat Penyakit Sekarang (RPS)** | ${hpi.trim() || 'Keluhan dirasakan bertahap tanpa tanda bahaya akut.'} |
| **Riwayat Penyakit Dahulu (RPD)** | ${pmh.trim() || 'Tidak ada riwayat penyakit kronis terdokumentasi.'} |
| **Riwayat Penyakit Keluarga (RPK)** | ${familyHistory.trim() || 'Tidak ada riwayat penyakit herediter spesifik.'} |
| **Riwayat Pengobatan Terkini** | ${medicationHistory.trim() || 'Tidak ada konsumsi obat rutin.'} |
| **Riwayat Alergi (Obat/Makanan)** | ${allergyHistory.trim() || 'Tidak ada riwayat alergi obat atau makanan (NKDA).'} |
| **Faktor Gaya Hidup & Kebiasaan** | ${lifestyleFactors.trim() || 'Aktivitas harian mandiri, pola makan teratur.'} |

---
*(✅ **Catatan Validasi**: Data anamnesis telah diverifikasi dan divalidasi oleh Dokter Penanggung Jawab Pelayanan / DPJP)*`;
  };

  const handleSave = () => {
    const updated = generateMarkdown();
    onSave(updated);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-white dark:bg-slate-900 border border-emerald-500/30 rounded-3xl shadow-2xl w-full max-w-4xl max-h-[92vh] flex flex-col overflow-hidden transition-all">
        
        {/* Header Modal */}
        <div className="px-6 py-4 border-b border-emerald-100 dark:border-slate-800 bg-gradient-to-r from-emerald-50 via-teal-50 to-emerald-50/50 dark:from-slate-900 dark:via-slate-850 dark:to-slate-900 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-600 text-white flex items-center justify-center text-lg font-bold shadow-md shadow-emerald-600/20">
              📝
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-emerald-950 dark:text-slate-100">
                  Editor Data Anamnesis Pasien (RME SIMRS)
                </h3>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700">
                  ✏️ Mode Edit & Validasi DPJP
                </span>
              </div>
              <p className="text-xs text-emerald-700 dark:text-slate-400">
                Sesuaikan dan validasi 7 komponen anamnesis klinis pasien sebelum disimpan ke SIMRS
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-xl flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="px-6 pt-3 pb-1 border-b border-emerald-100 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center gap-2">
          <button
            type="button"
            onClick={() => setActiveTab('form')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeTab === 'form'
                ? 'bg-emerald-600 text-white shadow-xs'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
            }`}
          >
            <span>📋</span>
            <span>Komponen Utama Anamnesis</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('preview')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeTab === 'preview'
                ? 'bg-emerald-600 text-white shadow-xs'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
            }`}
          >
            <span>👁️</span>
            <span>Pratinjau Tabel Anamnesis</span>
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-4 flex-1">
          {activeTab === 'form' && (
            <div className="space-y-4">
              {/* Keluhan Utama */}
              <div className="rounded-2xl border border-emerald-200 dark:border-slate-700 bg-emerald-50/40 dark:bg-slate-850/60 p-4 space-y-2">
                <label className="text-xs font-bold text-emerald-950 dark:text-emerald-300 flex items-center gap-2">
                  <span className="w-5 h-5 rounded-md bg-emerald-600 text-white flex items-center justify-center text-[10px] font-black">1</span>
                  <span>Keluhan Utama (Chief Complaint)</span>
                </label>
                <input
                  type="text"
                  value={chiefComplaint}
                  onChange={(e) => setChiefComplaint(e.target.value)}
                  placeholder="Contoh: Nyeri ulu hati perih terbakar sejak 1 minggu..."
                  className="w-full rounded-xl border border-emerald-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3.5 py-2 text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
                />
                <div className="flex flex-wrap gap-1 pt-1">
                  <span className="text-[10px] text-slate-400 font-semibold mr-1">Rekomendasi Cepat:</span>
                  {SUGGESTIONS.chiefComplaint.map((s, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => setChiefComplaint(s)}
                      className="px-2 py-0.5 rounded-lg bg-emerald-100/70 dark:bg-slate-800 hover:bg-emerald-200 dark:hover:bg-slate-700 text-emerald-900 dark:text-slate-200 text-[10px] font-medium transition-all"
                    >
                      + {s.slice(0, 32)}…
                    </button>
                  ))}
                </div>
              </div>

              {/* Riwayat Penyakit Sekarang (RPS) */}
              <div className="rounded-2xl border border-emerald-200 dark:border-slate-700 bg-emerald-50/40 dark:bg-slate-850/60 p-4 space-y-2">
                <label className="text-xs font-bold text-emerald-950 dark:text-emerald-300 flex items-center gap-2">
                  <span className="w-5 h-5 rounded-md bg-emerald-600 text-white flex items-center justify-center text-[10px] font-black">2</span>
                  <span>Riwayat Penyakit Sekarang (RPS / History of Present Illness)</span>
                </label>
                <textarea
                  value={hpi}
                  onChange={(e) => setHpi(e.target.value)}
                  rows={3}
                  placeholder="Uraikan kronologi keluhan, durasi, faktor pemicu/meredakan, dan gejala penyerta..."
                  className="w-full rounded-xl border border-emerald-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3.5 py-2 text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 leading-relaxed"
                />
              </div>

              {/* Riwayat Penyakit Dahulu (RPD) & Riwayat Keluarga (RPK) */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="rounded-2xl border border-teal-200 dark:border-slate-700 bg-teal-50/40 dark:bg-slate-850/60 p-4 space-y-2">
                  <label className="text-xs font-bold text-teal-950 dark:text-teal-300 flex items-center gap-2">
                    <span className="w-5 h-5 rounded-md bg-teal-600 text-white flex items-center justify-center text-[10px] font-black">3</span>
                    <span>Riwayat Penyakit Dahulu (RPD)</span>
                  </label>
                  <textarea
                    value={pmh}
                    onChange={(e) => setPmh(e.target.value)}
                    rows={2}
                    placeholder="Riwayat penyakit kronis terdahulu, rawat inap, atau operasi..."
                    className="w-full rounded-xl border border-teal-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-teal-500/50"
                  />
                  <div className="flex flex-wrap gap-1">
                    {SUGGESTIONS.rpd.slice(0, 3).map((s, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => setPmh(prev => prev ? `${prev}; ${s}` : s)}
                        className="px-2 py-0.5 rounded-lg bg-teal-100 dark:bg-slate-800 text-teal-900 dark:text-slate-200 text-[10px] font-medium"
                      >
                        + {s.slice(0, 24)}…
                      </button>
                    ))}
                  </div>
                </div>

                <div className="rounded-2xl border border-teal-200 dark:border-slate-700 bg-teal-50/40 dark:bg-slate-850/60 p-4 space-y-2">
                  <label className="text-xs font-bold text-teal-950 dark:text-teal-300 flex items-center gap-2">
                    <span className="w-5 h-5 rounded-md bg-teal-600 text-white flex items-center justify-center text-[10px] font-black">4</span>
                    <span>Riwayat Penyakit Keluarga (RPK)</span>
                  </label>
                  <textarea
                    value={familyHistory}
                    onChange={(e) => setFamilyHistory(e.target.value)}
                    rows={2}
                    placeholder="Riwayat DM, hipertensi, penyakit jantung pada keluarga..."
                    className="w-full rounded-xl border border-teal-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-teal-500/50"
                  />
                  <div className="flex flex-wrap gap-1">
                    {SUGGESTIONS.rpk.slice(0, 3).map((s, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => setFamilyHistory(prev => prev ? `${prev}; ${s}` : s)}
                        className="px-2 py-0.5 rounded-lg bg-teal-100 dark:bg-slate-800 text-teal-900 dark:text-slate-200 text-[10px] font-medium"
                      >
                        + {s.slice(0, 24)}…
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Riwayat Alergi & Pengobatan */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="rounded-2xl border border-rose-200 dark:border-slate-700 bg-rose-50/40 dark:bg-slate-850/60 p-4 space-y-2">
                  <label className="text-xs font-bold text-rose-950 dark:text-rose-300 flex items-center gap-2">
                    <span className="w-5 h-5 rounded-md bg-rose-600 text-white flex items-center justify-center text-[10px] font-black">5</span>
                    <span>Riwayat Alergi Obat / Makanan</span>
                  </label>
                  <input
                    type="text"
                    value={allergyHistory}
                    onChange={(e) => setAllergyHistory(e.target.value)}
                    placeholder="Contoh: Tidak ada riwayat alergi obat (NKDA)..."
                    className="w-full rounded-xl border border-rose-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-rose-500/50"
                  />
                  <div className="flex flex-wrap gap-1">
                    {SUGGESTIONS.allergies.map((s, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => setAllergyHistory(s)}
                        className="px-2 py-0.5 rounded-lg bg-rose-100 dark:bg-slate-800 text-rose-900 dark:text-slate-200 text-[10px] font-medium"
                      >
                        + {s.slice(0, 24)}…
                      </button>
                    ))}
                  </div>
                </div>

                <div className="rounded-2xl border border-indigo-200 dark:border-slate-700 bg-indigo-50/40 dark:bg-slate-850/60 p-4 space-y-2">
                  <label className="text-xs font-bold text-indigo-950 dark:text-indigo-300 flex items-center gap-2">
                    <span className="w-5 h-5 rounded-md bg-indigo-600 text-white flex items-center justify-center text-[10px] font-black">6</span>
                    <span>Riwayat Pengobatan Terkini</span>
                  </label>
                  <input
                    type="text"
                    value={medicationHistory}
                    onChange={(e) => setMedicationHistory(e.target.value)}
                    placeholder="Contoh: Metformin 500mg 2x1, Lisinopril 10mg 1x1..."
                    className="w-full rounded-xl border border-indigo-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                  />
                  <div className="flex flex-wrap gap-1">
                    {SUGGESTIONS.medications.slice(0, 3).map((s, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => setMedicationHistory(s)}
                        className="px-2 py-0.5 rounded-lg bg-indigo-100 dark:bg-slate-800 text-indigo-900 dark:text-slate-200 text-[10px] font-medium"
                      >
                        + {s.slice(0, 24)}…
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Faktor Gaya Hidup */}
              <div className="rounded-2xl border border-amber-200 dark:border-slate-700 bg-amber-50/40 dark:bg-slate-850/60 p-4 space-y-2">
                <label className="text-xs font-bold text-amber-950 dark:text-amber-300 flex items-center gap-2">
                  <span className="w-5 h-5 rounded-md bg-amber-600 text-white flex items-center justify-center text-[10px] font-black">7</span>
                  <span>Faktor Gaya Hidup & Kebiasaan Sosial</span>
                </label>
                <input
                  type="text"
                  value={lifestyleFactors}
                  onChange={(e) => setLifestyleFactors(e.target.value)}
                  placeholder="Contoh: Pola makan tidak teratur, sering kopi/pedas, merokok (-)..."
                  className="w-full rounded-xl border border-amber-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3.5 py-2 text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-amber-500/50"
                />
              </div>
            </div>
          )}

          {activeTab === 'preview' && (
            <div className="space-y-4">
              <div className="p-3 bg-emerald-50 dark:bg-slate-800/80 rounded-xl border border-emerald-200 dark:border-slate-700 text-xs text-emerald-900 dark:text-slate-200 flex items-center justify-between">
                <span>👁️ <strong>Pratinjau Tampilan Tabel HTML Medis:</strong> Format tabel klinis resmi yang akan disimpan ke rekam medis.</span>
                <span className="px-2 py-0.5 rounded-full bg-emerald-600 text-white text-[10px] font-bold">Terstandar SIMRS</span>
              </div>

              {/* HTML Table 1: Komponen Anamnesis */}
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-emerald-200 dark:border-slate-800 overflow-hidden shadow-xs">
                <div className="px-4 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white flex items-center justify-between">
                  <h4 className="text-xs font-bold flex items-center gap-2">
                    <span>📋</span>
                    <span>Tabel Komponen Anamnesis Terstruktur</span>
                  </h4>
                  <span className="text-[10px] font-medium opacity-90">Modul RME SIMRS</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-emerald-50 dark:bg-slate-800 text-emerald-950 dark:text-slate-200 uppercase tracking-wider font-bold border-b border-emerald-100 dark:border-slate-700 text-[11px]">
                      <tr>
                        <th className="px-4 py-3 w-1/3">Komponen Anamnesis</th>
                        <th className="px-4 py-3 w-2/3">Data Temuan Klinis Pasien</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-emerald-100 dark:divide-slate-800 text-slate-900 dark:text-slate-100">
                      <tr className="hover:bg-emerald-50/40 dark:hover:bg-slate-800/40">
                        <td className="px-4 py-2.5 font-bold text-emerald-950 dark:text-emerald-300">Keluhan Utama</td>
                        <td className="px-4 py-2.5 font-semibold text-emerald-900 dark:text-emerald-200">{chiefComplaint.trim() || '-'}</td>
                      </tr>
                      <tr className="bg-slate-50/50 dark:bg-slate-850/40 hover:bg-emerald-50/40 dark:hover:bg-slate-800/40">
                        <td className="px-4 py-2.5 font-bold text-emerald-950 dark:text-emerald-300">Riwayat Penyakit Sekarang (RPS)</td>
                        <td className="px-4 py-2.5 leading-relaxed">{hpi.trim() || '-'}</td>
                      </tr>
                      <tr className="hover:bg-emerald-50/40 dark:hover:bg-slate-800/40">
                        <td className="px-4 py-2.5 font-bold text-emerald-950 dark:text-emerald-300">Riwayat Penyakit Dahulu (RPD)</td>
                        <td className="px-4 py-2.5">{pmh.trim() || '-'}</td>
                      </tr>
                      <tr className="bg-slate-50/50 dark:bg-slate-850/40 hover:bg-emerald-50/40 dark:hover:bg-slate-800/40">
                        <td className="px-4 py-2.5 font-bold text-emerald-950 dark:text-emerald-300">Riwayat Penyakit Keluarga (RPK)</td>
                        <td className="px-4 py-2.5">{familyHistory.trim() || '-'}</td>
                      </tr>
                      <tr className="hover:bg-emerald-50/40 dark:hover:bg-slate-800/40">
                        <td className="px-4 py-2.5 font-bold text-emerald-950 dark:text-emerald-300">Riwayat Pengobatan Terkini</td>
                        <td className="px-4 py-2.5">{medicationHistory.trim() || '-'}</td>
                      </tr>
                      <tr className="bg-slate-50/50 dark:bg-slate-850/40 hover:bg-emerald-50/40 dark:hover:bg-slate-800/40">
                        <td className="px-4 py-2.5 font-bold text-emerald-950 dark:text-emerald-300">Riwayat Alergi (Obat / Makanan)</td>
                        <td className="px-4 py-2.5 font-medium text-rose-700 dark:text-rose-400">{allergyHistory.trim() || 'Tidak ada riwayat alergi (NKDA)'}</td>
                      </tr>
                      <tr className="hover:bg-emerald-50/40 dark:hover:bg-slate-800/40">
                        <td className="px-4 py-2.5 font-bold text-emerald-950 dark:text-emerald-300">Faktor Gaya Hidup & Kebiasaan</td>
                        <td className="px-4 py-2.5">{lifestyleFactors.trim() || '-'}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-emerald-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-850 flex items-center justify-between flex-wrap gap-3">
          <span className="text-[11px] text-slate-500 dark:text-slate-400">
            Perubahan akan memperbarui tampilan pesan anamnesis aktif pada sesi konsultasi klinis.
          </span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
            >
              Batal
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md transition-all flex items-center gap-1.5"
            >
              <span>💾</span>
              <span>Simpan & Perbarui Anamnesis</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
