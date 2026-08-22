'use client';

import { useState } from 'react';
import type { AgentStep } from '@/services/agent.service';

interface WorkflowExpandableProps {
  steps?: AgentStep[];
}

export default function WorkflowExpandable({ steps }: WorkflowExpandableProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!steps || steps.length === 0) return null;

  return (
    <div className="mt-3 pt-2.5 border-t border-emerald-100 dark:border-slate-800/80">
      {/* Toggle Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium text-emerald-800 dark:text-slate-300 hover:text-emerald-950 dark:hover:text-white bg-emerald-50/80 dark:bg-slate-800/80 hover:bg-emerald-100 dark:hover:bg-slate-700 border border-emerald-200/80 dark:border-slate-700 transition-all shadow-2xs group"
      >
        <span className="text-xs">🔍</span>
        <span>{isOpen ? 'Sembunyikan' : 'Lihat'} Langkah Alur Kerja AI</span>
        <span className="px-1.5 py-0.2 rounded-full bg-emerald-200/70 dark:bg-slate-700 text-[10px] font-bold text-emerald-900 dark:text-emerald-300">
          {steps.length}
        </span>
        <span className={`text-[10px] ml-0.5 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}>
          ▼
        </span>
      </button>

      {/* Expanded Workflow Steps Container */}
      {isOpen && (
        <div className="mt-2.5 space-y-2 p-3 rounded-xl bg-emerald-50/50 dark:bg-slate-950/60 border border-emerald-200/70 dark:border-slate-800 text-xs animate-in fade-in slide-in-from-top-1 duration-200">
          <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 dark:text-emerald-400 mb-1 flex items-center justify-between">
            <span>Rincian Eksekusi Agen LangGraph & SIMRS MCP</span>
            <span className="text-[9px] font-mono text-emerald-600 dark:text-slate-500">Audit Trail</span>
          </div>

          <div className="space-y-1.5">
            {steps.map((step, idx) => {
              const isSuccess = step.status === 'success';

              return (
                <div
                  key={idx}
                  className="p-2 rounded-lg bg-white dark:bg-slate-900 border border-emerald-100 dark:border-slate-800 shadow-2xs space-y-1"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-1.5 font-semibold text-[11px] text-emerald-950 dark:text-slate-200">
                      <span className="w-4 h-4 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400 flex items-center justify-center text-[9px] font-mono shrink-0">
                        {idx + 1}
                      </span>
                      <span>{step.step_name}</span>
                    </div>

                    <span
                      className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold uppercase tracking-wider ${
                        isSuccess
                          ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
                          : 'bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800'
                      }`}
                    >
                      {step.status}
                    </span>
                  </div>

                  {step.description && (
                    <p className="text-[11px] text-emerald-800 dark:text-slate-400 pl-5.5 leading-relaxed">
                      {step.description}
                    </p>
                  )}

                  {step.result && typeof step.result === 'string' && (
                    <div className="pl-5.5 text-[10px] font-mono text-emerald-700 dark:text-slate-500 bg-emerald-50/50 dark:bg-slate-950 p-1.5 rounded border border-emerald-100/60 dark:border-slate-800/80 truncate">
                      {step.result}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
