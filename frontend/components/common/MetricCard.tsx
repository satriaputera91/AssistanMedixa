'use client';

interface MetricCardProps {
  label: string;
  value: string | number;
  color?: 'blue' | 'emerald' | 'purple' | 'amber' | 'rose';
  icon?: string;
}

const colorMap = {
  blue: 'text-emerald-700',
  emerald: 'text-emerald-700',
  purple: 'text-emerald-700',
  amber: 'text-amber-400',
  rose: 'text-rose-400',
};

export default function MetricCard({ label, value, color = 'blue', icon }: MetricCardProps) {
  return (
    <div className="bg-white border border-emerald-200 rounded-2xl p-6 shadow-lg hover:border-emerald-300 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-emerald-700 uppercase tracking-wider">{label}</span>
        {icon && <span className="text-lg">{icon}</span>}
      </div>
      <div className={`text-3xl font-extrabold ${colorMap[color]}`}>
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
    </div>
  );
}
