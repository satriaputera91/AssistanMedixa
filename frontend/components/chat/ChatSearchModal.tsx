'use client';

import { useState, useEffect, useRef, useMemo } from 'react';
import type { ChatSession } from '@/services/agent.service';

interface ChatSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessions: ChatSession[];
  onSelectSession: (sessionId: string) => void;
}

interface SearchResultItem extends ChatSession {
  snippet?: string;
}

export default function ChatSearchModal({
  isOpen,
  onClose,
  sessions,
  onSelectSession,
}: ChatSearchModalProps) {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Filter sessions matching query
  const results: SearchResultItem[] = useMemo(() => {
    if (!query.trim()) return sessions.map((s) => ({ ...s, snippet: undefined }));
    const q = query.toLowerCase();

    return sessions
      .map((s) => {
        const titleMatch = (s.title || '').toLowerCase().includes(q);
        const patientMatch = (s.patient_id || '').toLowerCase().includes(q);

        // Find first matching message snippet
        const matchingMsg = (s.messages || []).find((m) =>
          (m.content || '').toLowerCase().includes(q)
        );

        let matchSnippet = '';
        if (matchingMsg) {
          const idx = matchingMsg.content.toLowerCase().indexOf(q);
          const start = Math.max(0, idx - 40);
          const end = Math.min(matchingMsg.content.length, idx + q.length + 60);
          matchSnippet = (start > 0 ? '...' : '') + matchingMsg.content.substring(start, end) + (end < matchingMsg.content.length ? '...' : '');
        }

        const score = titleMatch ? 2 : (matchingMsg ? 1 : (patientMatch ? 1 : 0));

        return {
          session: s,
          score,
          snippet: matchSnippet,
        };
      })
      .filter((item) => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .map((item) => ({ ...item.session, snippet: item.snippet }));
  }, [sessions, query]);

  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  // Keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (results.length ? (prev + 1) % results.length : 0));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (results.length ? (prev - 1 + results.length) % results.length : 0));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (results[selectedIndex]) {
          onSelectSession(results[selectedIndex].session_id);
          onClose();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, results, selectedIndex, onSelectSession, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/50 dark:bg-black/70 backdrop-blur-sm flex items-start justify-center p-4 sm:p-6 md:pt-20 animate-in fade-in duration-150"
      onClick={onClose}
    >
      <div
        className="w-full max-w-2xl bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh] transition-all animate-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Header Input */}
        <div className="p-4 border-b border-emerald-200 dark:border-slate-800 flex items-center gap-3 bg-emerald-50/40 dark:bg-slate-900/60">
          <span className="text-lg text-emerald-600 dark:text-emerald-400 shrink-0">🔍</span>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Cari riwayat percakapan, topik klinis, nama obat, atau pasien..."
            className="flex-1 bg-transparent text-sm text-emerald-950 dark:text-white placeholder-emerald-500/70 dark:placeholder-slate-500 focus:outline-none font-medium"
          />
          {query && (
            <button
              type="button"
              onClick={() => setQuery('')}
              className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs rounded-md"
            >
              ✕
            </button>
          )}
          <kbd className="hidden sm:inline-block px-2 py-0.5 text-[10px] font-mono font-semibold text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-md">
            ESC
          </kbd>
        </div>

        {/* Results List */}
        <div className="flex-1 overflow-y-auto p-3 space-y-1 divide-y divide-emerald-50 dark:divide-slate-800/40">
          {results.length === 0 ? (
            <div className="py-12 text-center text-emerald-700 dark:text-slate-400 space-y-1">
              <div className="text-3xl mb-2">📂</div>
              <p className="text-xs font-semibold text-emerald-950 dark:text-white">
                Tidak ada riwayat chat yang cocok
              </p>
              <p className="text-[11px] text-emerald-600 dark:text-slate-500">
                Coba gunakan kata kunci diagnosis, nama obat, atau tanggal lain.
              </p>
            </div>
          ) : (
            results.map((s, idx) => {
              const isSelected = selectedIndex === idx;

              return (
                <div
                  key={s.session_id}
                  onClick={() => {
                    onSelectSession(s.session_id);
                    onClose();
                  }}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`p-3 rounded-xl cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-emerald-600/15 dark:bg-emerald-500/20 border border-emerald-500/30'
                      : 'hover:bg-emerald-50/60 dark:hover:bg-slate-800/60'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="text-xs">💬</span>
                      <h4 className="text-xs font-bold text-emerald-950 dark:text-white truncate">
                        {s.title || 'Percakapan Tanpa Judul'}
                      </h4>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      {s.patient_id && (
                        <span className="px-2 py-0.5 rounded-md bg-emerald-100 dark:bg-slate-800 text-[10px] font-mono font-semibold text-emerald-800 dark:text-emerald-300">
                          {s.patient_id}
                        </span>
                      )}
                      <span className="text-[10px] text-emerald-600 dark:text-slate-400">
                        {new Date(s.created_at).toLocaleDateString('id-ID', {
                          day: 'numeric',
                          month: 'short',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                    </div>
                  </div>

                  {s.snippet && (
                    <p className="text-[11px] text-emerald-800/90 dark:text-slate-300 line-clamp-2 bg-white/60 dark:bg-slate-950/40 p-2 rounded-lg border border-emerald-100 dark:border-slate-800 font-mono text-[10px]">
                      {s.snippet}
                    </p>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Modal Footer with Keyboard Shortcuts */}
        <div className="p-3 border-t border-emerald-200 dark:border-slate-800 bg-emerald-50/30 dark:bg-slate-900/60 flex items-center justify-between text-[10px] text-emerald-700 dark:text-slate-400">
          <span>
            Menampilkan <strong>{results.length}</strong> riwayat percakapan
          </span>

          <div className="hidden sm:flex items-center gap-3">
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded font-mono">
                ↑↓
              </kbd>{' '}
              Navigasi
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded font-mono">
                ↵
              </kbd>{' '}
              Buka Sesi
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded font-mono">
                ESC
              </kbd>{' '}
              Tutup
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
