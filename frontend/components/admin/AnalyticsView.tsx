'use client';

import type { UsageAnalytics } from '@/services/admin.service';

interface AnalyticsViewProps {
  analytics: UsageAnalytics | null;
}

export default function AnalyticsView({ analytics }: AnalyticsViewProps) {
  if (!analytics) return null;

  const maxDailyRequests = Math.max(...analytics.requests_by_day.map((d) => d.requests), 1);

  return (
    <div className="bg-white border border-emerald-200 rounded-2xl p-6 shadow-lg space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-emerald-950 flex items-center gap-2">
            <span>📊</span>
            <span>Analisis Penggunaan &amp; Pemakaian Token</span>
          </h2>
          <p className="text-xs text-emerald-700 mt-0.5">
            Aktivitas harian, beban token Gemini, dan statistik evaluasi klinis.
          </p>
        </div>
      </div>

      {/* Highlights */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-3.5 bg-emerald-50/70 border border-emerald-200 rounded-xl">
          <div className="text-[10px] uppercase font-semibold text-emerald-700">Total Permintaan</div>
          <div className="text-xl font-extrabold text-emerald-950 mt-1">{analytics.total_requests}</div>
        </div>
        <div className="p-3.5 bg-emerald-50/70 border border-emerald-200 rounded-xl">
          <div className="text-[10px] uppercase font-semibold text-emerald-700">Rata-rata Token/Req</div>
          <div className="text-xl font-extrabold text-emerald-950 mt-1">{analytics.average_tokens_per_request}</div>
        </div>
        <div className="p-3.5 bg-emerald-50/70 border border-emerald-200 rounded-xl">
          <div className="text-[10px] uppercase font-semibold text-emerald-700">Permintaan Audio WAV</div>
          <div className="text-xl font-extrabold text-emerald-950 mt-1">{analytics.audio_requests}</div>
        </div>
        <div className="p-3.5 bg-emerald-50/70 border border-emerald-200 rounded-xl">
          <div className="text-[10px] uppercase font-semibold text-emerald-700">Revisi S/O/A Dikonfirmasi</div>
          <div className="text-xl font-extrabold text-emerald-950 mt-1">{analytics.soa_revisions}</div>
        </div>
      </div>

      {/* 7-Day Activity Chart & Top Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Daily Request Chart */}
        <div className="lg:col-span-2 p-4 bg-emerald-50/50 border border-emerald-200/80 rounded-xl">
          <div className="text-xs font-bold text-emerald-950 mb-3">Tren Aktivitas 7 Hari Terakhir</div>
          <div className="flex items-end gap-3 h-36 pt-4 px-2">
            {analytics.requests_by_day.map((day, idx) => {
              const heightPercent = Math.max(12, Math.round((day.requests / maxDailyRequests) * 100));
              const dateLabel = new Date(day.date).toLocaleDateString('id-ID', {
                weekday: 'short',
                day: 'numeric',
              });

              return (
                <div key={idx} className="flex-1 flex flex-col items-center gap-1 h-full justify-end group">
                  <span className="text-[10px] font-mono text-emerald-800 opacity-0 group-hover:opacity-100 transition-opacity">
                    {day.requests} req
                  </span>
                  <div
                    style={{ height: `${heightPercent}%` }}
                    className="w-full bg-gradient-to-t from-emerald-600 to-emerald-400 rounded-t-md hover:from-emerald-500 hover:to-emerald-300 transition-all cursor-pointer relative"
                    title={`${day.date}: ${day.requests} req, ${day.tokens.toLocaleString()} tokens`}
                  />
                  <span className="text-[10px] text-emerald-700 font-medium truncate w-full text-center mt-1">
                    {dateLabel}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Top Actions */}
        <div className="p-4 bg-emerald-50/50 border border-emerald-200/80 rounded-xl flex flex-col justify-between">
          <div>
            <div className="text-xs font-bold text-emerald-950 mb-3">Aktivitas Terbanyak</div>
            <div className="space-y-2.5">
              {analytics.top_actions.length === 0 && (
                <p className="text-xs text-emerald-600">Belum ada aktivitas tercatat</p>
              )}
              {analytics.top_actions.map((act, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs">
                  <span className="text-emerald-900 font-medium truncate max-w-[180px]">{act.action}</span>
                  <span className="px-2 py-0.5 rounded-md bg-emerald-200/60 font-mono text-[10px] text-emerald-900 font-bold shrink-0">
                    {act.count}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
