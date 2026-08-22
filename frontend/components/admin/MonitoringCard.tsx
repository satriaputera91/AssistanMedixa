'use client';

import type { SystemMonitoring, ServiceHealth } from '@/services/admin.service';

interface MonitoringCardProps {
  monitoring: SystemMonitoring | null;
}

const statusBadges: Record<ServiceHealth['status'], { bg: string; dot: string; label: string }> = {
  healthy: {
    bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-800',
    dot: 'bg-emerald-500',
    label: 'Normal / Aktif',
  },
  warning: {
    bg: 'bg-amber-500/10 border-amber-500/30 text-amber-800',
    dot: 'bg-amber-500',
    label: 'Peringatan',
  },
  unhealthy: {
    bg: 'bg-red-500/10 border-red-500/30 text-red-800',
    dot: 'bg-red-500',
    label: 'Gangguan',
  },
};

export default function MonitoringCard({ monitoring }: MonitoringCardProps) {
  if (!monitoring) return null;

  return (
    <div className="bg-white border border-emerald-200 rounded-2xl p-6 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-bold text-emerald-950 flex items-center gap-2">
            <span>🛡️</span>
            <span>Status Layanan &amp; Kesiapan Sistem</span>
          </h2>
          <p className="text-xs text-emerald-700 mt-0.5">
            Pemeriksaan operasional FastAPI, Qdrant Vektor RAG, Gemini LLM, dan SIMRS MCP.
          </p>
        </div>
        <div className="text-right">
          <span className="text-[10px] text-emerald-600 font-mono">
            Diperiksa: {new Date(monitoring.checked_at).toLocaleTimeString()}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {monitoring.services.map((svc, idx) => {
          const badge = statusBadges[svc.status] || statusBadges.healthy;
          return (
            <div
              key={idx}
              className="p-4 bg-emerald-50/60 border border-emerald-200 rounded-xl flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-xs text-emerald-950">{svc.name}</span>
                  <span
                    className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-semibold border ${badge.bg}`}
                  >
                    <span className={`w-1.5 h-1.5 rounded-full ${badge.dot}`} />
                    {badge.label}
                  </span>
                </div>
                <p className="text-xs text-emerald-800 line-clamp-2">{svc.detail}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
