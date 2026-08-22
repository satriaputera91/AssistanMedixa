'use client';
import type { AuditLogItem } from '@/services/admin.service';

interface AuditFeedProps {
  logs: AuditLogItem[];
}

export default function AuditFeed({ logs }: AuditFeedProps) {
  return (
    <div className="bg-white border border-emerald-200 rounded-2xl p-6 shadow-lg">
      <h2 className="text-lg font-bold text-emerald-950 mb-4">Log Audit & Aktivitas Agen</h2>

      <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
        {logs.length === 0 && (
          <p className="text-xs text-emerald-600 text-center py-6">Belum ada catatan audit</p>
        )}
        {logs.map((log) => (
          <div
            key={log.id}
            className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex justify-between items-start gap-4 hover:border-emerald-300 transition-colors"
          >
            <div className="min-w-0 flex-1">
              <div className="text-xs font-semibold text-emerald-900">
                {log.action} — <span className="text-emerald-700">{log.doctor_name}</span>
              </div>
              <div className="text-[10px] text-emerald-700 mt-1 truncate">{log.details}</div>
            </div>
            <div className="text-right shrink-0">
              <div className="text-xs font-mono text-emerald-600">{log.tokens_used.toLocaleString()} token</div>
              <div className="text-[10px] text-emerald-600 mt-0.5">
                {new Date(log.timestamp).toLocaleString()}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
