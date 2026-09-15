'use client';

import { useState } from 'react';
import { AgentService, type TempSOAPRecord, type TempSOAPContent } from '@/services/agent.service';

interface ManualSOAPModalProps {
  sessionId: string;
  patientId?: string;
  patientName?: string;
  onSaved: (soapRecord: TempSOAPRecord) => void;
  onClose: () => void;
}

const STEPS = [
  { id: 1, title: '1. Subjektif (S)', subtitle: 'Anamnesis & Keluhan Pasien', icon: '📝' },
  { id: 2, title: '2. Objektif (O)', subtitle: 'Pemeriksaan Fisik & Observasi Lab', icon: '🧪' },
];

export default function ManualSOAPModal({
  sessionId,
  patientId,
  patientName,
  onSaved,
  onClose,
}: ManualSOAPModalProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  // Step 1: Subjektif fields
  const [chiefComplaint, setChiefComplaint] = useState('');
  const [rps, setRps] = useState('');
  const [rpd, setRpd] = useState('');
  const [allergies, setAllergies] = useState('Tidak ada alergi obat/makanan (NKDA)');
  const [currentMeds, setCurrentMeds] = useState('');

  // Step 2: Objektif fields (Vitals & Physical)
  const [td, setTd] = useState('120/80');
  const [nadi, setNadi] = useState('80');
  const [rr, setRr] = useState('18');
  const [suhu, setSuhu] = useState('36.7');
  const [spo2, setSpo2] = useState('98');
  const [physicalExam, setPhysicalExam] = useState('');
  const [labResults, setLabResults] = useState('');

  // Quick preset helpers
  const applyChiefSuggestion = (val: string) => {
    setChiefComplaint(val);
    if (!rps) setRps(`Pasien datang dengan ${val.toLowerCase()}, memberat dalam beberapa hari terakhir.`);
  };

  const applyVitalsPreset = (type: 'normal' | 'ht' | 'fever') => {
    if (type === 'normal') {
      setTd('120/80');
      setNadi('78');
      setRr('18');
      setSuhu('36.6');
      setSpo2('99');
    } else if (type === 'ht') {
      setTd('150/95');
      setNadi('88');
      setRr('20');
      setSuhu('36.8');
      setSpo2('98');
    } else if (type === 'fever') {
      setTd('115/75');
      setNadi('102');
      setRr('22');
      setSuhu('38.9');
      setSpo2('97');
    }
  };

  const handleNext = () => {
    if (currentStep === 1 && !chiefComplaint.trim()) {
      setError('Mohon isi Keluhan Utama (Chief Complaint) pasien terlebih dahulu.');
      return;
    }
    setError('');
    setCurrentStep((prev) => Math.min(prev + 1, 2));
  };

  const handlePrev = () => {
    setError('');
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  const handleSaveToTempSOAP = async () => {
    if (!chiefComplaint.trim()) {
      setCurrentStep(1);
      setError('Keluhan Utama (Subjektif) wajib diisi.');
      return;
    }

    setSaving(true);
    setError('');

    // Construct full S/O text
    const subjectiveText = [
      `Keluhan Utama: ${chiefComplaint}`,
      rps ? `Riwayat Penyakit Sekarang (RPS): ${rps}` : '',
      rpd ? `Riwayat Penyakit Dahulu (RPD): ${rpd}` : '',
      allergies ? `Riwayat Alergi: ${allergies}` : '',
      currentMeds ? `Pengobatan Rutin: ${currentMeds}` : '',
    ]
      .filter(Boolean)
      .join('\n');

    const vitalsStr = `TD: ${td} mmHg | Nadi: ${nadi} x/mnt | RR: ${rr} x/mnt | Suhu: ${suhu} °C | SpO2: ${spo2}%`;
    const objectiveText = [
      `Tanda Vital: ${vitalsStr}`,
      physicalExam ? `Pemeriksaan Fisik: ${physicalExam}` : '',
      labResults ? `Hasil Lab & Penunjang: ${labResults}` : '',
    ]
      .filter(Boolean)
      .join('\n');

    const assessmentText = 'Menunggu formulasi diagnosis kerja & ICD-10 dari analisis AI Medis';
    const planText = 'Menunggu rekomendasi terapi obat & rencana tindakan dari analisis AI Medis';

    const soapContent: TempSOAPContent = {
      subjective: subjectiveText,
      objective: objectiveText,
      assessment: assessmentText,
      plan: planText,
      instructions: 'Silakan minta AI untuk menyusun rekomendasi klinis komprehensif.',
    };

    const rawMarkdown = `### 📋 Catatan Rekam SOAP Klinis (Pengisian Manual S & O)
**Subjektif (S):**
${subjectiveText}

**Objektif (O):**
${objectiveText}

**Asesmen (A):**
${assessmentText}

**Plan (P):**
${planText}`;

    try {
      const created = await AgentService.createManualTempSOAP({
        session_id: sessionId,
        patient_id: patientId || undefined,
        soap_content: soapContent,
        raw_markdown: rawMarkdown,
        structured_output: {
          vitals: { td, nadi, rr, suhu, spo2 },
          input_mode: 'manual_so_wizard',
        },
      });

      onSaved(created);
      onClose();
    } catch (e: any) {
      console.error('Failed to create manual temp soap:', e);
      setError(e?.message || 'Gagal menyimpan ke SOAP Temporary Database.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white dark:bg-slate-900 rounded-3xl max-w-2xl w-full p-6 sm:p-7 shadow-2xl border border-emerald-200 dark:border-slate-800 space-y-5 max-h-[92vh] overflow-y-auto animate-in zoom-in-95 duration-150">
        {/* Header with Patient Info */}
        <div className="flex items-center justify-between border-b border-emerald-100 dark:border-slate-800 pb-3.5">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-2xl bg-emerald-100 dark:bg-emerald-950/70 border border-emerald-200 dark:border-emerald-800 flex items-center justify-center text-lg shadow-2xs">
              ✍️
            </div>
            <div>
              <h3 className="font-bold text-base text-emerald-950 dark:text-white">
                Pengisian Manual Data Klinis (Subjektif &amp; Objektif)
              </h3>
              <p className="text-xs text-emerald-700 dark:text-slate-400">
                {patientId
                  ? `Pasien: ${patientName || patientId} (${patientId})`
                  : 'Sesi Konsultasi Medis Umum'}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-white text-lg font-bold p-1 rounded-lg"
          >
            ✕
          </button>
        </div>

        {/* Step Progress Tracker (2 Steps: Subjektif & Objektif) */}
        <div className="grid grid-cols-2 gap-3">
          {STEPS.map((s) => {
            const isActive = currentStep === s.id;
            const isDone = currentStep > s.id;

            return (
              <button
                key={s.id}
                type="button"
                onClick={() => setCurrentStep(s.id)}
                className={`p-3 rounded-2xl border text-left transition-all ${
                  isActive
                    ? 'bg-emerald-50 dark:bg-emerald-950/80 border-emerald-400 dark:border-emerald-600 shadow-2xs'
                    : isDone
                    ? 'bg-slate-50 dark:bg-slate-800/60 border-slate-200 dark:border-slate-700 opacity-90'
                    : 'bg-white dark:bg-slate-900 border-slate-100 dark:border-slate-800 opacity-50'
                }`}
              >
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="font-bold text-emerald-950 dark:text-slate-200">
                    {s.icon} {s.title}
                  </span>
                  {isDone && <span className="text-emerald-600 dark:text-emerald-400 text-xs font-bold">✓ Selesai</span>}
                </div>
                <div className="text-[11px] text-emerald-800 dark:text-slate-400">
                  {s.subtitle}
                </div>
              </button>
            );
          })}
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-xs text-red-700 dark:text-red-300">
            ⚠️ {error}
          </div>
        )}

        {/* Step 1: Subjektif (Anamnesis) */}
        {currentStep === 1 && (
          <div className="space-y-4 animate-in fade-in duration-150">
            <div>
              <label className="block text-xs font-bold text-emerald-950 dark:text-slate-200 mb-1">
                Keluhan Utama (Chief Complaint) <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                placeholder="Contoh: Nyeri dada kiri menjalar ke bahu sejak 2 jam lalu, sesak napas (+)"
                value={chiefComplaint}
                onChange={(e) => setChiefComplaint(e.target.value)}
                className="w-full px-3.5 py-2.5 text-xs rounded-xl bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 text-emerald-950 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />

              {/* Quick Suggestion Chips */}
              <div className="mt-2 flex flex-wrap gap-1.5">
                <span className="text-[10px] font-semibold text-slate-400 self-center">Pilihan cepat:</span>
                {[
                  'Nyeri ulu hati perih terbakar sejak 4 hari',
                  'Pusing berputar, lemas, nokturia',
                  'Nyeri dada tertindih beban berat',
                  'Demam tinggi menggigil 3 hari & batuk',
                  'Sesak napas saat tidur terlentang',
                ].map((sug) => (
                  <button
                    key={sug}
                    type="button"
                    onClick={() => applyChiefSuggestion(sug)}
                    className="px-2 py-0.5 rounded-lg bg-emerald-100/70 hover:bg-emerald-200/80 dark:bg-slate-800 text-emerald-900 dark:text-slate-300 text-[10px] transition-all"
                  >
                    + {sug}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-emerald-950 dark:text-slate-200 mb-1">
                Riwayat Penyakit Sekarang (RPS)
              </label>
              <textarea
                rows={2}
                placeholder="Onset, lokasi, durasi, karakteristik nyeri, faktor pemicu/pereda..."
                value={rps}
                onChange={(e) => setRps(e.target.value)}
                className="w-full px-3.5 py-2 text-xs rounded-xl bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 text-emerald-950 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-emerald-950 dark:text-slate-200 mb-1">
                  Riwayat Penyakit Dahulu (RPD)
                </label>
                <input
                  type="text"
                  placeholder="Hipertensi, DM Tipe 2, Jantung..."
                  value={rpd}
                  onChange={(e) => setRpd(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 text-emerald-950 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-emerald-950 dark:text-slate-200 mb-1">
                  Riwayat Alergi (Obat / Makanan)
                </label>
                <input
                  type="text"
                  placeholder="Tidak ada alergi / Alergi Penisilin / NSAID..."
                  value={allergies}
                  onChange={(e) => setAllergies(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 text-emerald-950 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-emerald-950 dark:text-slate-200 mb-1">
                Pengobatan Rutin yang Sedang Dikonsumsi
              </label>
              <input
                type="text"
                placeholder="Metformin 500mg, Amlodipine 10mg, dsb..."
                value={currentMeds}
                onChange={(e) => setCurrentMeds(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-xl bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 text-emerald-950 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>
        )}

        {/* Step 2: Objektif (Pemeriksaan & Observasi) */}
        {currentStep === 2 && (
          <div className="space-y-4 animate-in fade-in duration-150">
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-bold text-emerald-950 dark:text-slate-200">
                  Tanda Vital (Vital Signs)
                </label>
                <div className="flex items-center gap-1.5 text-[10px]">
                  <span className="text-slate-400">Preset:</span>
                  <button
                    type="button"
                    onClick={() => applyVitalsPreset('normal')}
                    className="px-2 py-0.5 rounded bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300"
                  >
                    Normal
                  </button>
                  <button
                    type="button"
                    onClick={() => applyVitalsPreset('ht')}
                    className="px-2 py-0.5 rounded bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300"
                  >
                    Hipertensi
                  </button>
                  <button
                    type="button"
                    onClick={() => applyVitalsPreset('fever')}
                    className="px-2 py-0.5 rounded bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300"
                  >
                    Febris
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5">
                <div>
                  <span className="text-[10px] font-semibold text-slate-500">TD (mmHg)</span>
                  <input
                    type="text"
                    value={td}
                    onChange={(e) => setTd(e.target.value)}
                    className="w-full px-2.5 py-1.5 text-xs rounded-lg bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 font-mono text-center"
                  />
                </div>
                <div>
                  <span className="text-[10px] font-semibold text-slate-500">Nadi (x/mnt)</span>
                  <input
                    type="text"
                    value={nadi}
                    onChange={(e) => setNadi(e.target.value)}
                    className="w-full px-2.5 py-1.5 text-xs rounded-lg bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 font-mono text-center"
                  />
                </div>
                <div>
                  <span className="text-[10px] font-semibold text-slate-500">RR (x/mnt)</span>
                  <input
                    type="text"
                    value={rr}
                    onChange={(e) => setRr(e.target.value)}
                    className="w-full px-2.5 py-1.5 text-xs rounded-lg bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 font-mono text-center"
                  />
                </div>
                <div>
                  <span className="text-[10px] font-semibold text-slate-500">Suhu (°C)</span>
                  <input
                    type="text"
                    value={suhu}
                    onChange={(e) => setSuhu(e.target.value)}
                    className="w-full px-2.5 py-1.5 text-xs rounded-lg bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 font-mono text-center"
                  />
                </div>
                <div>
                  <span className="text-[10px] font-semibold text-slate-500">SpO2 (%)</span>
                  <input
                    type="text"
                    value={spo2}
                    onChange={(e) => setSpo2(e.target.value)}
                    className="w-full px-2.5 py-1.5 text-xs rounded-lg bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 font-mono text-center"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-emerald-950 dark:text-slate-200 mb-1">
                Pemeriksaan Fisik Terarah (Observasi Head-to-Toe)
              </label>
              <textarea
                rows={2}
                placeholder="Konjungtiva anemis (-/-), Cor/Pulmo dalam batas normal, Nyeri tekan epigastrium (+)..."
                value={physicalExam}
                onChange={(e) => setPhysicalExam(e.target.value)}
                className="w-full px-3.5 py-2 text-xs rounded-xl bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 text-emerald-950 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-emerald-950 dark:text-slate-200 mb-1">
                Hasil Laboratorium &amp; Pemeriksaan Penunjang (Bila Ada)
              </label>
              <input
                type="text"
                placeholder="Hb: 13.2 g/dL, Leukosit: 7.800, GDS: 110 mg/dL, eGFR: 85 mL/min, EKG: Sinus rhythm..."
                value={labResults}
                onChange={(e) => setLabResults(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-xl bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 text-emerald-950 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            {/* Info note about AI generating Assessment & Plan */}
            <div className="p-3 rounded-2xl bg-emerald-50/70 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 flex items-center gap-2.5">
              <span className="text-base">💡</span>
              <p className="text-[11px] text-emerald-900 dark:text-emerald-300 leading-relaxed">
                Setelah data Subjektif &amp; Objektif disimpan, AI Medis akan langsung menganalisis dan menyusun <strong>Asesmen (Diagnosis Kerja ICD-10)</strong> serta <strong>Plan (Rencana Obat &amp; Tindakan)</strong> secara komprehensif.
              </p>
            </div>
          </div>
        )}

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-3.5 border-t border-emerald-100 dark:border-slate-800">
          <button
            type="button"
            onClick={currentStep === 1 ? onClose : handlePrev}
            className="px-4 py-2 text-xs font-semibold rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 transition-all"
          >
            {currentStep === 1 ? 'Batal' : '◀ Sebelumnya'}
          </button>

          <div className="flex items-center gap-2">
            {currentStep === 1 ? (
              <button
                type="button"
                onClick={handleNext}
                className="px-5 py-2 text-xs font-bold rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm transition-all flex items-center gap-1 active:scale-[0.98]"
              >
                <span>Lanjut ke Objektif</span>
                <span>▶</span>
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSaveToTempSOAP}
                disabled={saving}
                className="px-5 py-2 text-xs font-bold rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white shadow-md transition-all flex items-center gap-1.5 active:scale-[0.98]"
              >
                <span>💾</span>
                <span>{saving ? 'Menyimpan ke SOAP Temp...' : 'Simpan ke SOAP Temporary Database'}</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
