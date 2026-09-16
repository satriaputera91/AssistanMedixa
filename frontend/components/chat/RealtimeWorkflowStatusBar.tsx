'use client';

import { useState } from 'react';

export interface RealtimeWorkflowStatusBarProps {
  executing: boolean;
  sessionId?: string | null;
  activeNode?: string | null;
  completedNodes?: string[];
  latestSummary?: string;
}

const WORKFLOW_PIPELINE_NODES = [
  { key: 'planner', label: 'Planner', icon: '🧠' },
  { key: 'fetch_patient_history', label: 'SIMRS EMR', icon: '👤' },
  { key: 'fetch_patient_anamnesis', label: 'Anamnesis', icon: '📝' },
  { key: 'eval_simrs_labs', label: 'Lab & Vitals', icon: '🧪' },
  { key: 'diagnostic_recommendation', label: 'Diagnosis', icon: '🎯' },
  { key: 'km_disease_explanations', label: 'Knowledge', icon: '📚' },
  { key: 'km_red_flag_detection', label: 'Red Flag', icon: '🚨' },
  { key: 'km_medication_recommendation', label: 'Medication', icon: '💊' },
  { key: 'patient_drug_safety', label: 'Drug Safety', icon: '🛡️' },
  { key: 'tools', label: 'MCP & RAG', icon: '🛠️' },
  { key: 'synthesis', label: 'Synthesis', icon: '🩺' },
  { key: 'validate_output', label: 'Guardrails', icon: '🛡️' },
];

export default function RealtimeWorkflowStatusBar({
  executing,
  activeNode = null,
  completedNodes = [],
  latestSummary = '',
}: RealtimeWorkflowStatusBarProps) {
  const [isOpen, setIsOpen] = useState(true);

  if (!executing && (!completedNodes || completedNodes.length === 0)) return null;

  return (
    <div className="mb-3 p-3 rounded-2xl bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border border-emerald-200/90 dark:border-slate-800 shadow-sm text-xs transition-all animate-in fade-in slide-in-from-top-1 duration-200">
      <div className="flex items-center justify-between gap-2 pb-1.5 border-b border-emerald-100/70 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 font-bold text-emerald-950 dark:text-slate-100">
            {executing && <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping shrink-0" />}
            <span>Alur Kerja LangGraph (SSE Stream)</span>
          </div>
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
            {executing ? 'Sedang Berjalan' : 'Selesai'}
          </span>
        </div>

        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="text-[10px] text-emerald-700 dark:text-slate-400 hover:text-emerald-950 dark:hover:text-white"
        >
          {isOpen ? 'Sembunyikan' : 'Tampilkan'}
        </button>
      </div>

      {isOpen && (
        <div className="mt-2.5 space-y-2">
          {/* Node Progression Pipeline Tracker */}
          <div className="flex items-center gap-1 overflow-x-auto pb-1 scrollbar-none">
            {WORKFLOW_PIPELINE_NODES.map((node, idx) => {
              const isDone = completedNodes.includes(node.key);
              const isCurrent = activeNode === node.key;

              return (
                <div key={node.key} className="flex items-center shrink-0">
                  <div
                    className={`flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-medium transition-all ${
                      isCurrent && executing
                        ? 'bg-emerald-600 text-white font-bold shadow-xs scale-105 animate-pulse'
                        : isDone
                        ? 'bg-emerald-100 dark:bg-emerald-950/70 text-emerald-900 dark:text-emerald-300 border border-emerald-300/60 dark:border-emerald-800 shadow-2xs font-semibold'
                        : 'bg-slate-100 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 opacity-60'
                    }`}
                  >
                    <span>{node.icon}</span>
                    <span className="whitespace-nowrap">{node.label}</span>
                    {isDone && <span className="text-emerald-600 dark:text-emerald-400 text-[9px] font-bold">✓</span>}
                  </div>

                  {idx < WORKFLOW_PIPELINE_NODES.length - 1 && (
                    <span className="text-[9px] text-slate-300 dark:text-slate-700 mx-0.5">➔</span>
                  )}
                </div>
              );
            })}
          </div>

          {/* Realtime Summary Ticker */}
          {latestSummary && (
            <div className="p-2 rounded-xl bg-emerald-50/70 dark:bg-slate-950/60 border border-emerald-100 dark:border-slate-800/80 flex items-center justify-between text-[11px] text-emerald-900 dark:text-slate-300">
              <div className="flex items-center gap-2 truncate">
                <span className="text-emerald-600 dark:text-emerald-400 font-mono text-[10px] uppercase font-bold shrink-0">
                  Status Live:
                </span>
                <span className="truncate">{latestSummary}</span>
              </div>

              {activeNode && (
                <span className="px-1.5 py-0.2 rounded bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-700 text-[9px] font-mono text-emerald-800 dark:text-slate-300 shrink-0 ml-2">
                  Node: {activeNode}
                </span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
