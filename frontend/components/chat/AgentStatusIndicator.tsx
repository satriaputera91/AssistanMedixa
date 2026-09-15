'use client';

import { useState, useEffect } from 'react';

interface StatusPhaseConfig {
  key: string;
  badge: string;
  icon: string;
  label: string;
  detail: string;
  color: string;
  darkColor: string;
}

const DEFAULT_NODE_PHASES: Record<string, StatusPhaseConfig> = {
  started: {
    key: 'started',
    badge: 'Initiating',
    icon: '🚀',
    label: 'Menginisialisasi Alur Kerja AI',
    detail: 'Menghubungkan protokol MCP SIMRS & menyiapkan konteks konsultasi...',
    color: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    darkColor: 'dark:bg-emerald-950/70 dark:text-emerald-300 dark:border-emerald-700',
  },
  planner: {
    key: 'planner',
    badge: 'Planning',
    icon: '🧠',
    label: 'Klasifikasi Niat & Perencanaan Alur',
    detail: 'Menentukan jalur eksekusi klinis & domain spesialisasi medis...',
    color: 'bg-indigo-100 text-indigo-800 border-indigo-300',
    darkColor: 'dark:bg-indigo-950/70 dark:text-indigo-300 dark:border-indigo-700',
  },
  fetch_patient_history: {
    key: 'fetch_patient_history',
    badge: 'Reading SIMRS',
    icon: '👤',
    label: 'Membaca Rekam Medis SIMRS',
    detail: 'Mengambil profil demografi, riwayat kunjungan, dan diagnosis terdahulu...',
    color: 'bg-cyan-100 text-cyan-800 border-cyan-300',
    darkColor: 'dark:bg-cyan-950/70 dark:text-cyan-300 dark:border-cyan-700',
  },
  fetch_patient_anamnesis: {
    key: 'fetch_patient_anamnesis',
    badge: 'Anamnesis',
    icon: '📝',
    label: 'Mengambil Anamnesis RME',
    detail: 'Mengevaluasi keluhan utama, RPS, RPD, dan faktor risiko pasien...',
    color: 'bg-sky-100 text-sky-800 border-sky-300',
    darkColor: 'dark:bg-sky-950/70 dark:text-sky-300 dark:border-sky-700',
  },
  eval_simrs_labs: {
    key: 'eval_simrs_labs',
    badge: 'Lab & Vitals',
    icon: '🧪',
    label: 'Evaluasi Lab & Tanda Vital',
    detail: 'Menganalisis hasil biomarker laboratorium serial, eGFR, dan tanda vital...',
    color: 'bg-blue-100 text-blue-800 border-blue-300',
    darkColor: 'dark:bg-blue-950/70 dark:text-blue-300 dark:border-blue-700',
  },
  diagnostic_recommendation: {
    key: 'diagnostic_recommendation',
    badge: 'Differential Dx',
    icon: '🎯',
    label: 'Analisis Diagnosis Banding & ICD-10',
    detail: 'Menyusun hipotesis diagnosis kerja dan diagnosis banding terbobot...',
    color: 'bg-violet-100 text-violet-800 border-violet-300',
    darkColor: 'dark:bg-violet-950/70 dark:text-violet-300 dark:border-violet-700',
  },
  km_disease_explanations: {
    key: 'km_disease_explanations',
    badge: 'Guidelines',
    icon: '📖',
    label: 'Meninjau Panduan Klinis',
    detail: 'Mencocokkan kriteria diagnostik baku dan patofisiologi klinis...',
    color: 'bg-teal-100 text-teal-800 border-teal-300',
    darkColor: 'dark:bg-teal-950/70 dark:text-teal-300 dark:border-teal-700',
  },
  km_red_flag_detection: {
    key: 'km_red_flag_detection',
    badge: 'Red Flags',
    icon: '🚨',
    label: 'Deteksi Tanda Bahaya & Kedaruratan',
    detail: 'Skrining tanda bahaya klinis, ambang kedaruratan, dan risiko komplikasi...',
    color: 'bg-rose-100 text-rose-800 border-rose-300',
    darkColor: 'dark:bg-rose-950/70 dark:text-rose-300 dark:border-rose-700',
  },
  km_medication_recommendation: {
    key: 'km_medication_recommendation',
    badge: 'Medication',
    icon: '💊',
    label: 'Rekomendasi Terapi Farmakologi',
    detail: 'Menentukan rejimen obat lini pertama dan panduan penyesuaian dosis ginjal/hepar...',
    color: 'bg-purple-100 text-purple-800 border-purple-300',
    darkColor: 'dark:bg-purple-950/70 dark:text-purple-300 dark:border-purple-700',
  },
  patient_drug_safety: {
    key: 'patient_drug_safety',
    badge: 'Drug Safety',
    icon: '🛡️',
    label: 'Skrining Interaksi Obat & Alergi',
    detail: 'Memeriksa kontraindikasi, alergi silang, dan interaksi obat berbahaya...',
    color: 'bg-amber-100 text-amber-800 border-amber-300',
    darkColor: 'dark:bg-amber-950/70 dark:text-amber-300 dark:border-amber-700',
  },
  tools: {
    key: 'tools',
    badge: 'MCP & RAG',
    icon: '🛠️',
    label: 'Pencarian Qdrant & Transaksi SIMRS',
    detail: 'Menjalankan pencarian vektor RAG dan transaksi MCP SIMRS...',
    color: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    darkColor: 'dark:bg-emerald-950/70 dark:text-emerald-300 dark:border-emerald-700',
  },
  synthesis: {
    key: 'synthesis',
    badge: 'Reasoning',
    icon: '🩺',
    label: 'Penalaran Klinis & Sintesis',
    detail: 'Menyusun catatan perkembangan terintegrasi (S-O-A-P) komprehensif...',
    color: 'bg-fuchsia-100 text-fuchsia-800 border-fuchsia-300',
    darkColor: 'dark:bg-fuchsia-950/70 dark:text-fuchsia-300 dark:border-fuchsia-700',
  },
  validate_output: {
    key: 'validate_output',
    badge: 'Guardrails',
    icon: '🛡️',
    label: 'Validasi Standar & Guardrails',
    detail: 'Memverifikasi keamanan data medis, disclaimer, dan format respon...',
    color: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    darkColor: 'dark:bg-emerald-950/70 dark:text-emerald-300 dark:border-emerald-700',
  },
  audio_transcription: {
    key: 'audio_transcription',
    badge: 'Transcribing',
    icon: '🎙️',
    label: 'Transkripsi Audio Konsultasi',
    detail: 'Menerjemahkan rekaman suara konsultasi dokter-pasien via Generative AI Multimodal...',
    color: 'bg-cyan-100 text-cyan-800 border-cyan-300',
    darkColor: 'dark:bg-cyan-950/70 dark:text-cyan-300 dark:border-cyan-700',
  },
  audio_soap_summary: {
    key: 'audio_soap_summary',
    badge: 'SOAP Drafting',
    icon: '📋',
    label: 'Menyusun Resume SOAP Klinis',
    detail: 'Mengekstrak keluhan Subjektif, Objektif, Asesmen, dan Plan dari transkrip audio...',
    color: 'bg-teal-100 text-teal-800 border-teal-300',
    darkColor: 'dark:bg-teal-950/70 dark:text-teal-300 dark:border-teal-700',
  },
};

const FALLBACK_PROGRESSION_KEYS = [
  'planner',
  'fetch_patient_history',
  'eval_simrs_labs',
  'diagnostic_recommendation',
  'km_medication_recommendation',
  'patient_drug_safety',
  'tools',
  'synthesis',
  'validate_output',
];

interface AgentStatusIndicatorProps {
  executing: boolean;
  activeNode?: string | null;
  latestSummary?: string;
  sessionId?: string | null;
}

export default function AgentStatusIndicator({
  executing,
  activeNode,
  latestSummary,
}: AgentStatusIndicatorProps) {
  const [fallbackIndex, setFallbackIndex] = useState(0);

  useEffect(() => {
    if (!executing) {
      setFallbackIndex(0);
      return;
    }

    const fallbackTimer = setInterval(() => {
      setFallbackIndex((prev) => (prev + 1) % FALLBACK_PROGRESSION_KEYS.length);
    }, 1200);

    return () => {
      clearInterval(fallbackTimer);
    };
  }, [executing]);

  if (!executing) return null;

  let currentPhase: StatusPhaseConfig;

  if (activeNode && DEFAULT_NODE_PHASES[activeNode]) {
    const baseConfig = DEFAULT_NODE_PHASES[activeNode];
    currentPhase = {
      ...baseConfig,
      detail: latestSummary || baseConfig.detail,
    };
  } else {
    const fallbackKey = FALLBACK_PROGRESSION_KEYS[fallbackIndex] || 'planner';
    currentPhase = DEFAULT_NODE_PHASES[fallbackKey] || DEFAULT_NODE_PHASES.planner;
  }

  return (
    <div className="bg-white dark:bg-slate-900 border border-emerald-300/80 dark:border-slate-800 rounded-2xl rounded-bl-none p-4 shadow-lg max-w-lg transition-all animate-in fade-in slide-in-from-bottom-2 duration-200">
      <div className="flex items-center gap-3">
        {/* Animated Icon Avatar */}
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-slate-800 dark:to-slate-800/80 border border-emerald-200 dark:border-slate-700 flex items-center justify-center text-lg shadow-xs shrink-0 relative overflow-hidden">
          <span className="relative z-10 animate-pulse">{currentPhase.icon}</span>
          <div className="absolute inset-0 bg-gradient-to-t from-emerald-500/20 to-transparent animate-spin opacity-60" />
        </div>

        {/* Status Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            {/* Status Phase Badge */}
            <span
              className={`px-2 py-0.5 rounded-md text-[10px] font-mono font-bold uppercase tracking-wider border shadow-2xs transition-all ${currentPhase.color} ${currentPhase.darkColor}`}
            >
              {currentPhase.badge}
            </span>

            {/* Live SSE Stream Indicator Badge */}
            <div className="flex items-center gap-1 px-1.5 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200/60 dark:border-emerald-800/60 text-[9px] font-mono text-emerald-800 dark:text-emerald-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
              <span>SSE Stream Live</span>
            </div>

            {/* Pulsing Dots */}
            <div className="flex items-center gap-1 ml-auto">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce [animation-delay:-0.3s]" />
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce [animation-delay:-0.15s]" />
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce" />
            </div>
          </div>

          <p className="text-xs font-bold text-emerald-950 dark:text-slate-100 truncate">
            {currentPhase.label}
          </p>
          <p className="text-[11px] text-emerald-700 dark:text-slate-400 truncate leading-relaxed">
            {currentPhase.detail}
          </p>

          {/* Node Execution Name if available */}
          {activeNode && (
            <div className="mt-1 flex items-center gap-1.5 text-[9px] font-mono text-emerald-600 dark:text-slate-500">
              <span className="text-emerald-500">⚡ Node:</span>
              <span className="font-semibold text-emerald-900 dark:text-slate-300 bg-emerald-100/60 dark:bg-slate-800 px-1 py-0.2 rounded">
                {activeNode}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
