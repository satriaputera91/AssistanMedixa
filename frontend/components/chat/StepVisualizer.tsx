'use client';

interface StepVisualizerProps {
  executing: boolean;
}

export default function StepVisualizer({ executing }: StepVisualizerProps) {
  if (!executing) return null;

  const steps = [
    { icon: '🔌', label: 'Menghubungkan protokol SIMRS MCP...' },
    { icon: '🎯', label: 'Mencari Qdrant RAG dan melakukan pemeringkatan ulang...' },
    { icon: '💊', label: 'Memeriksa interaksi obat...' },
    { icon: '✨', label: 'Menyusun analisis klinis dengan Gemini...' },
  ];

  return (
    <div className="p-4 bg-white dark:bg-slate-900 border border-emerald-500/30 dark:border-emerald-500/20 rounded-2xl max-w-3xl animate-pulse shadow-sm">
      <div className="text-xs font-bold text-emerald-800 dark:text-emerald-300 flex items-center gap-2 mb-3">
        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
        Agen RAG &amp; MCP sedang bekerja
      </div>
      <div className="space-y-1.5">
        {steps.map((step, i) => (
          <div key={i} className="text-[11px] text-emerald-800 dark:text-slate-300 flex items-center gap-2">
            <span>{step.icon}</span>
            <span>{step.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
