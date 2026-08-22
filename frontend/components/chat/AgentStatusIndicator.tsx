'use client';

import { useState, useEffect } from 'react';

interface StatusPhase {
  key: 'working' | 'reading' | 'searching' | 'reasoning' | 'editing';
  badge: string;
  icon: string;
  label: string;
  detail: string;
  color: string;
  darkColor: string;
}

const PHASES: StatusPhase[] = [
  {
    key: 'working',
    badge: 'Working',
    icon: '⚡',
    label: 'Menginisialisasi Agen',
    detail: 'Menghubungkan protokol MCP & merencanakan alur klinis...',
    color: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    darkColor: 'dark:bg-emerald-950/70 dark:text-emerald-300 dark:border-emerald-700',
  },
  {
    key: 'reading',
    badge: 'Reading',
    icon: '📖',
    label: 'Membaca Data SIMRS',
    detail: 'Mengambil riwayat medis, diagnosis, dan alergi pasien...',
    color: 'bg-cyan-100 text-cyan-800 border-cyan-300',
    darkColor: 'dark:bg-cyan-950/70 dark:text-cyan-300 dark:border-cyan-700',
  },
  {
    key: 'searching',
    badge: 'Searching',
    icon: '🔍',
    label: 'Mencari Pengetahuan RAG',
    detail: 'Mencocokkan embedding Gemini & pemeringkatan ulang Qdrant...',
    color: 'bg-blue-100 text-blue-800 border-blue-300',
    darkColor: 'dark:bg-blue-950/70 dark:text-blue-300 dark:border-blue-700',
  },
  {
    key: 'reasoning',
    badge: 'Reasoning',
    icon: '🧠',
    label: 'Penalaran Klinis AI',
    detail: 'Mengevaluasi kontraindikasi obat & guideline medis...',
    color: 'bg-purple-100 text-purple-800 border-purple-300',
    darkColor: 'dark:bg-purple-950/70 dark:text-purple-300 dark:border-purple-700',
  },
  {
    key: 'editing',
    badge: 'Editing',
    icon: '✍️',
    label: 'Menyusun Sintesis',
    detail: 'Memvalidasi format klinis & menyusun rekomendasi...',
    color: 'bg-amber-100 text-amber-800 border-amber-300',
    darkColor: 'dark:bg-amber-950/70 dark:text-amber-300 dark:border-amber-700',
  },
];

export default function AgentStatusIndicator({ executing }: { executing: boolean }) {
  const [phaseIndex, setPhaseIndex] = useState(0);

  useEffect(() => {
    if (!executing) {
      setPhaseIndex(0);
      return;
    }

    const interval = setInterval(() => {
      setPhaseIndex((prev) => (prev + 1) % PHASES.length);
    }, 1100);

    return () => clearInterval(interval);
  }, [executing]);

  if (!executing) return null;

  const current = PHASES[phaseIndex];

  return (
    <div className="bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 rounded-2xl rounded-bl-none p-4 shadow-md max-w-lg transition-all animate-in fade-in duration-200">
      <div className="flex items-center gap-3">
        {/* Animated Icon Avatar */}
        <div className="w-9 h-9 rounded-xl bg-emerald-50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 flex items-center justify-center text-base shadow-xs shrink-0 relative overflow-hidden">
          <span className="relative z-10 animate-pulse">{current.icon}</span>
          <div className="absolute inset-0 bg-gradient-to-t from-emerald-500/10 to-transparent animate-spin opacity-50" />
        </div>

        {/* Status Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            {/* Status Badge */}
            <span
              className={`px-2 py-0.5 rounded-md text-[10px] font-mono font-bold uppercase tracking-wider border shadow-xs transition-colors ${current.color} ${current.darkColor}`}
            >
              {current.badge}
            </span>

            {/* Pulsing Dots */}
            <div className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce [animation-delay:-0.3s]" />
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce [animation-delay:-0.15s]" />
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce" />
            </div>
          </div>

          <p className="text-xs font-semibold text-emerald-950 dark:text-slate-100 truncate">
            {current.label}
          </p>
          <p className="text-[11px] text-emerald-700 dark:text-slate-400 truncate">
            {current.detail}
          </p>
        </div>
      </div>
    </div>
  );
}
