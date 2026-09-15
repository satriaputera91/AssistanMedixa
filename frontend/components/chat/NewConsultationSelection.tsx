'use client';

import { useState } from 'react';
import type { PatientRecord } from '@/services/agent.service';
import { AgentService } from '@/services/agent.service';

interface NewConsultationSelectionProps {
  patients: PatientRecord[];
  onSelectGeneral: () => void;
  onSelectPatient: (patientId: string) => void;
}

export default function NewConsultationSelection({
  patients,
  onSelectGeneral,
  onSelectPatient,
}: NewConsultationSelectionProps) {
  const [activeMode, setActiveMode] = useState<'selection' | 'patient_input'>('selection');
  const [searchQuery, setSearchQuery] = useState('');
  const [loadingPatient, setLoadingPatient] = useState(false);
  const [foundPatient, setFoundPatient] = useState<PatientRecord | null>(null);
  const [lookupError, setLookupError] = useState<string | null>(null);

  const handleLookup = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoadingPatient(true);
    setLookupError(null);
    setFoundPatient(null);

    try {
      // First check local list
      const q = searchQuery.trim().toLowerCase();
      const local = patients.find(
        (p) =>
          p.patient_id.toLowerCase() === q ||
          (p.nik && p.nik.toLowerCase() === q) ||
          (p.ihs_number && p.ihs_number.toLowerCase() === q) ||
          p.name.toLowerCase().includes(q)
      );

      if (local) {
        setFoundPatient(local);
      } else {
        const res = await AgentService.lookupPatient(searchQuery.trim());
        setFoundPatient(res);
      }
    } catch (err: any) {
      setLookupError(
        err.message ||
        `Data pasien dengan NIK/IHS/MRN '${searchQuery}' tidak ditemukan di server SIMRS.`
      );
    } finally {
      setLoadingPatient(false);
    }
  };

  const handleConfirmPatient = (patientId: string) => {
    onSelectPatient(patientId);
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6">
      {/* Title */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 text-2xl mb-3 shadow-xs">
          🩺
        </div>
        <h2 className="text-xl sm:text-2xl font-black text-emerald-950 dark:text-white tracking-tight">
          Mulai Sesi Konsultasi Klinis Baru
        </h2>
        <p className="text-xs sm:text-sm text-emerald-700/90 dark:text-slate-400 mt-1 max-w-lg mx-auto">
          Pilih mode konsultasi sesuai kebutuhan: diskusi medis umum atau terhubung langsung dengan rekam medis pasien di SIMRS.
        </p>
      </div>

      {activeMode === 'selection' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Option 1: General Consultation */}
          <div
            onClick={onSelectGeneral}
            className="group relative bg-white dark:bg-slate-900 border-2 border-emerald-200/80 dark:border-slate-800 hover:border-emerald-500 dark:hover:border-emerald-500 rounded-3xl p-6 sm:p-7 shadow-sm hover:shadow-xl transition-all cursor-pointer flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="w-12 h-12 rounded-2xl bg-emerald-100 dark:bg-slate-800 text-emerald-700 dark:text-emerald-400 flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
                  🌐
                </span>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-slate-800 text-emerald-800 dark:text-emerald-300">
                  Umum & Literatur
                </span>
              </div>

              <h3 className="text-base sm:text-lg font-bold text-emerald-950 dark:text-white mb-2 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
                Konsultasi Medis Umum
              </h3>
              <p className="text-xs sm:text-sm text-emerald-700/80 dark:text-slate-400 leading-relaxed">
                Tanya jawab pedoman klinis (ADA, KDIGO, AHA), farmakologi obat, batas dosis, interaksi zat, atau studi medis tanpa menghubungkan data pasien spesifik.
              </p>
            </div>

            <div className="mt-6 pt-4 border-t border-emerald-100 dark:border-slate-800 flex items-center justify-between text-xs font-bold text-emerald-700 dark:text-emerald-400 group-hover:translate-x-1 transition-transform">
              <span>Langsung Mulai Chat</span>
              <span>➔</span>
            </div>
          </div>

          {/* Option 2: Active Patient with EHR */}
          <div
            onClick={() => setActiveMode('patient_input')}
            className="group relative bg-white dark:bg-slate-900 border-2 border-emerald-200/80 dark:border-slate-800 hover:border-emerald-500 dark:hover:border-emerald-500 rounded-3xl p-6 sm:p-7 shadow-sm hover:shadow-xl transition-all cursor-pointer flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="w-12 h-12 rounded-2xl bg-emerald-600 text-white flex items-center justify-center text-2xl group-hover:scale-110 transition-transform shadow-md">
                  🏥
                </span>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-emerald-600/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30">
                  SIMRS & SATUSEHAT
                </span>
              </div>

              <h3 className="text-base sm:text-lg font-bold text-emerald-950 dark:text-white mb-2 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
                Konsultasi Pasien Aktif
              </h3>
              <p className="text-xs sm:text-sm text-emerald-700/80 dark:text-slate-400 leading-relaxed">
                Ambil riwayat rekam medis pasien di SIMRS menggunakan <strong>NIK KTP</strong> atau <strong>Nomor IHS</strong> untuk analisis kontraindikasi, alergi, dan perbaruan resume SOAP.
              </p>
            </div>

            <div className="mt-6 pt-4 border-t border-emerald-100 dark:border-slate-800 flex items-center justify-between text-xs font-bold text-emerald-700 dark:text-emerald-400 group-hover:translate-x-1 transition-transform">
              <span>Masukkan NIK / IHS Pasien</span>
              <span>➔</span>
            </div>
          </div>
        </div>
      ) : (
        /* Patient NIK / IHS Input Mode */
        <div className="bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 shadow-lg space-y-6">
          <div className="flex items-center justify-between border-b border-emerald-100 dark:border-slate-800 pb-4">
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => {
                  setActiveMode('selection');
                  setFoundPatient(null);
                  setLookupError(null);
                }}
                className="p-2 rounded-xl text-emerald-700 dark:text-slate-300 hover:bg-emerald-100 dark:hover:bg-slate-800 transition-colors text-xs font-bold flex items-center gap-1"
              >
                <span>⬅</span>
                <span>Kembali</span>
              </button>
              <h3 className="text-base font-bold text-emerald-950 dark:text-white">
                Identifikasi Pasien SIMRS
              </h3>
            </div>
            <span className="text-[11px] text-emerald-700 dark:text-slate-400 font-medium">
              Koneksi SIMRS / Satu Sehat Aktif ✅
            </span>
          </div>

          {/* Form Lookup */}
          <form onSubmit={handleLookup} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-emerald-950 dark:text-white mb-2">
                Nomor Induk Kependudukan (NIK) / Nomor IHS SATUSEHAT / No. Rekam Medis (MRN):
              </label>
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Contoh: 3201015508600002 atau IHS-100010492 atau P-10492"
                    className="w-full pl-9 pr-4 py-3 bg-emerald-50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-2xl text-xs sm:text-sm text-emerald-950 dark:text-white placeholder-emerald-600/50 dark:placeholder-slate-500 focus:outline-none focus:border-emerald-500 font-medium transition-colors"
                  />
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-emerald-600 dark:text-slate-400">
                    🔍
                  </span>
                </div>
                <button
                  type="submit"
                  disabled={loadingPatient || !searchQuery.trim()}
                  className="px-5 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-2xl text-xs sm:text-sm font-bold shadow-md transition-all shrink-0 flex items-center gap-2"
                >
                  {loadingPatient ? (
                    <>
                      <span className="animate-spin">⏳</span>
                      <span>Mencari…</span>
                    </>
                  ) : (
                    <>
                      <span>Ambil Data SIMRS</span>
                      <span>➔</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Quick Demo Patients Selection Chips */}
            <div>
              <div className="text-[11px] font-semibold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider mb-2">
                Pilih Cepat Pasien Hari Ini:
              </div>
              <div className="flex flex-wrap gap-2">
                {patients.map((p) => (
                  <button
                    key={p.patient_id}
                    type="button"
                    onClick={() => {
                      setSearchQuery(p.nik || p.patient_id);
                      setFoundPatient(p);
                      setLookupError(null);
                    }}
                    className="px-3 py-1.5 rounded-xl border border-emerald-200 dark:border-slate-700 bg-emerald-50/70 dark:bg-slate-800 text-emerald-900 dark:text-slate-200 hover:bg-emerald-100 dark:hover:bg-slate-700 text-xs font-medium transition-colors flex items-center gap-2"
                  >
                    <span>👤</span>
                    <span>{p.name}</span>
                    <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-mono">
                      ({p.patient_id})
                    </span>
                    {p.room_name && (
                      <span className="px-1.5 py-0.5 rounded bg-emerald-100 dark:bg-emerald-950 text-[9px] font-bold text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700">
                        {p.room_name}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>
          </form>

          {/* Error Notice */}
          {lookupError && (
            <div className="p-4 rounded-2xl border border-red-200 bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 text-xs flex items-center gap-3">
              <span className="text-lg shrink-0">⚠️</span>
              <p className="flex-1">{lookupError}</p>
            </div>
          )}

          {/* Found Patient EHR Card Preview */}
          {foundPatient && (
            <div className="p-5 rounded-2xl border-2 border-emerald-500/50 bg-emerald-50/40 dark:bg-slate-800/60 space-y-4 animate-in fade-in zoom-in-95 duration-150">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xl">👤</span>
                    <h4 className="text-base font-bold text-emerald-950 dark:text-white">
                      {foundPatient.name}
                    </h4>
                    <span className="px-2 py-0.5 rounded-md bg-emerald-200 dark:bg-slate-700 text-[10px] font-bold text-emerald-900 dark:text-emerald-300">
                      {foundPatient.gender}, {foundPatient.age} th
                    </span>
                    {foundPatient.room_name && (
                      <span className="px-2 py-0.5 rounded-md bg-teal-100 dark:bg-teal-950 text-teal-800 dark:text-teal-300 text-[10px] font-bold border border-teal-300 dark:border-teal-700">
                        🏥 {foundPatient.room_name}
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] font-mono text-emerald-700 dark:text-slate-400 mt-1 space-x-3">
                    <span>MRN: <strong>{foundPatient.patient_id}</strong></span>
                    {foundPatient.nik && <span>NIK: <strong>{foundPatient.nik}</strong></span>}
                    {foundPatient.ihs_number && <span>IHS: <strong>{foundPatient.ihs_number}</strong></span>}
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => handleConfirmPatient(foundPatient.patient_id)}
                  className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs sm:text-sm font-bold shadow-md transition-all flex items-center gap-2 hover:scale-[1.02] active:scale-95"
                >
                  <span>✓ Mulai Konsultasi Pasien</span>
                </button>
              </div>

              {/* Patient Details Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-xs border-t border-emerald-200/60 dark:border-slate-700">
                <div className="bg-white/80 dark:bg-slate-900/80 p-3 rounded-xl border border-emerald-100 dark:border-slate-700/70">
                  <span className="text-[10px] font-bold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider block mb-1">
                    🩺 Diagnosa Aktif
                  </span>
                  <p className="font-semibold text-emerald-950 dark:text-slate-200">
                    {foundPatient.diagnoses.join(', ') || '—'}
                  </p>
                </div>

                <div className="bg-white/80 dark:bg-slate-900/80 p-3 rounded-xl border border-emerald-100 dark:border-slate-700/70">
                  <span className="text-[10px] font-bold text-amber-700 dark:text-amber-400 uppercase tracking-wider block mb-1">
                    ⚠️ Alergi Obat
                  </span>
                  <p className="font-semibold text-amber-900 dark:text-amber-300">
                    {foundPatient.allergies.join(', ') || 'Tidak ada riwayat'}
                  </p>
                </div>

                <div className="bg-white/80 dark:bg-slate-900/80 p-3 rounded-xl border border-emerald-100 dark:border-slate-700/70">
                  <span className="text-[10px] font-bold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider block mb-1">
                    🧪 Data Lab Terakhir
                  </span>
                  <p className="font-mono text-[11px] text-emerald-900 dark:text-slate-300">
                    {Object.entries(foundPatient.recent_labs || {})
                      .slice(0, 2)
                      .map(([k, v]) => `${k}: ${v}`)
                      .join(' | ') || '—'}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
