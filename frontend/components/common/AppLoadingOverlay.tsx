'use client';

import { useEffect, useState } from 'react';

interface AppLoadingOverlayProps {
  message?: string;
  subMessage?: string;
  onRetry?: () => void;
  isRetrying?: boolean;
}

const LOADING_STEPS = [
  '1. Verifikasi Sesi & Kredensial Dokter',
  '2. Menghubungkan RME SIMRS & Basis Pengetahuan',
  '3. Inisialisasi Model AI & Ruang Poliklinik',
];

export default function AppLoadingOverlay({
  message = 'Mempersiapkan Ruang Kerja Medis & Layanan AI...',
  subMessage = 'Menghubungkan ke server backend klinis...',
  onRetry,
  isRetrying = false,
}: AppLoadingOverlayProps) {
  const [currentStepIdx, setCurrentStepIdx] = useState(0);
  const [showDelayedHelp, setShowDelayedHelp] = useState(false);

  useEffect(() => {
    const stepInterval = setInterval(() => {
      setCurrentStepIdx((prev) => (prev + 1) % LOADING_STEPS.length);
    }, 1400);

    const helpTimer = setTimeout(() => {
      setShowDelayedHelp(true);
    }, 4500);

    return () => {
      clearInterval(stepInterval);
      clearTimeout(helpTimer);
    };
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-emerald-50 via-teal-50/50 to-cyan-50 dark:from-slate-950 dark:via-slate-900 dark:to-emerald-950/40 p-4 transition-colors">
      <div className="max-w-md w-full text-center space-y-6 animate-in zoom-in-95 duration-200">
        {/* Animated Stethoscope / Medical Pulse Icon */}
        <div className="relative inline-flex items-center justify-center">
          <div className="w-20 h-20 rounded-3xl bg-emerald-600 dark:bg-emerald-500 shadow-xl shadow-emerald-500/20 flex items-center justify-center text-4xl animate-bounce">
            🩺
          </div>
          <span className="absolute -inset-2 rounded-3xl bg-emerald-400/30 dark:bg-emerald-500/20 animate-ping -z-10" />
        </div>

        {/* Title & App Name */}
        <div className="space-y-1.5">
          <h2 className="text-xl font-bold tracking-tight text-emerald-950 dark:text-white flex items-center justify-center gap-2">
            <span>AssistantMedixa</span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
              AI Medical Co-Pilot
            </span>
          </h2>
          <p className="text-xs font-semibold text-emerald-800 dark:text-slate-300">
            {message}
          </p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400">
            {subMessage}
          </p>
        </div>

        {/* Step Progress Pills */}
        <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md rounded-2xl p-4 border border-emerald-200 dark:border-slate-800 shadow-sm space-y-2.5">
          <div className="flex items-center justify-between text-[11px] font-semibold text-slate-500 dark:text-slate-400 mb-1">
            <span>Status Inisialisasi</span>
            <span className="font-mono text-emerald-600 dark:text-emerald-400 font-bold">
              {currentStepIdx + 1}/{LOADING_STEPS.length}
            </span>
          </div>

          <div className="space-y-1.5 text-left">
            {LOADING_STEPS.map((step, idx) => {
              const isCurrent = idx === currentStepIdx;
              const isDone = idx < currentStepIdx;
              return (
                <div
                  key={step}
                  className={`px-3 py-1.5 rounded-lg text-xs flex items-center justify-between transition-all ${
                    isCurrent
                      ? 'bg-emerald-100/80 dark:bg-emerald-950/80 text-emerald-900 dark:text-emerald-200 font-bold border border-emerald-300 dark:border-emerald-700'
                      : isDone
                      ? 'text-emerald-700 dark:text-slate-400 font-medium opacity-80'
                      : 'text-slate-400 dark:text-slate-600 font-normal opacity-50'
                  }`}
                >
                  <span className="truncate">{step}</span>
                  {isCurrent ? (
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping shrink-0" />
                  ) : isDone ? (
                    <span className="text-emerald-600 dark:text-emerald-400 font-bold text-[11px]">✓</span>
                  ) : null}
                </div>
              );
            })}
          </div>

          {/* Shimmering Progress Bar */}
          <div className="w-full bg-emerald-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden mt-3">
            <div className="bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-500 h-full rounded-full animate-pulse w-full" />
          </div>
        </div>

        {/* Delayed Health Check / Retry Option if Backend is taking time */}
        {showDelayedHelp && (
          <div className="space-y-2.5 animate-in fade-in slide-in-from-bottom-2 duration-200">
            <p className="text-[11px] text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950/50 p-2.5 rounded-xl border border-amber-200 dark:border-amber-800">
              💡 Jika proses memuat membutuhkan waktu lebih lama, server backend medis mungkin sedang melakukan inisialisasi model AI.
            </p>

            {onRetry && (
              <button
                type="button"
                onClick={onRetry}
                disabled={isRetrying}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-sm hover:shadow transition-all flex items-center justify-center gap-1.5 mx-auto active:scale-95 cursor-pointer disabled:opacity-50"
              >
                {isRetrying ? (
                  <>
                    <svg className="w-3.5 h-3.5 animate-spin" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    <span>Mencoba Menghubungkan Ulang...</span>
                  </>
                ) : (
                  <>
                    <span>🔄</span>
                    <span>Hubungkan Ulang Sekarang</span>
                  </>
                )}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
