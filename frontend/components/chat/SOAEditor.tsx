'use client';

import { useEffect, useState } from 'react';
import type { SOAContent, SOANote } from '@/services/agent.service';

interface SOAEditorProps {
  note: SOANote;
  busy: boolean;
  onReview: (noteId: string, content: SOAContent) => void;
  onConfirm: (noteId: string, accept: boolean) => void;
}

const FIELDS: Array<{ key: keyof SOAContent; label: string; hint: string }> = [
  { key: 'subjective', label: 'S — Subjective', hint: 'Keluhan dan riwayat yang disampaikan pasien' },
  { key: 'objective', label: 'O — Objective', hint: 'Temuan dan data objektif yang disebutkan' },
  { key: 'assessment', label: 'A — Assessment', hint: 'Asesmen yang didukung rekaman' },
  { key: 'plan', label: 'P — Plan', hint: 'Rencana terapi, obat, instruksi, dan evaluasi lanjutan' },
];

export default function SOAEditor({ note, busy, onReview, onConfirm }: SOAEditorProps) {
  const [expanded, setExpanded] = useState(false);
  const [editing, setEditing] = useState(false);
  const [content, setContent] = useState<SOAContent>(note.content);

  useEffect(() => {
    setContent(note.content);
    if (note.status !== 'pending_confirmation') setEditing(false);
  }, [note]);

  const cancelEdit = () => {
    setContent(note.content);
    setEditing(false);
  };

  return (
    <section className="mt-4 rounded-2xl border border-emerald-500/30 dark:border-emerald-500/20 bg-emerald-50/70 dark:bg-slate-800/70 overflow-hidden transition-colors">
      <div className="flex items-center justify-between gap-3 px-4 py-3 border-b border-emerald-200 dark:border-slate-700">
        <div>
          <p className="text-xs font-bold text-emerald-800 dark:text-emerald-300">Resume Audio S-O-A-P</p>
          <p className="text-[10px] text-emerald-600 dark:text-slate-400">
            {note.status === 'pending_confirmation' ? 'Menunggu konfirmasi dokter' : 'Draf klinis SOAP — perlu validasi dokter'}
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setExpanded(value => !value)} className="text-[11px] font-semibold text-emerald-800 dark:text-slate-300 hover:text-emerald-950 dark:hover:text-white">
            {expanded ? 'Ringkas' : 'Perluas'}
          </button>
          {note.status !== 'pending_confirmation' && !editing && (
            <button onClick={() => { setExpanded(true); setEditing(true); }} className="text-[11px] font-semibold text-emerald-700 dark:text-emerald-400 hover:underline">
              Edit resume
            </button>
          )}
        </div>
      </div>

      {expanded && (
        <div className="p-4 space-y-4">
          {FIELDS.map(({ key, label, hint }) => (
            <div key={key}>
              <label className="block text-[11px] font-semibold text-emerald-800 dark:text-emerald-400 mb-1">{label}</label>
              {editing ? (
                <textarea
                  value={content[key]}
                  onChange={(event) => setContent(current => ({ ...current, [key]: event.target.value }))}
                  rows={4}
                  className="w-full resize-y rounded-xl border border-emerald-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-xs leading-relaxed text-emerald-950 dark:text-slate-100 focus:border-emerald-500 focus:outline-none"
                  aria-label={label}
                />
              ) : (
                <p className="whitespace-pre-wrap text-xs leading-relaxed text-emerald-900 dark:text-slate-200 bg-white/70 dark:bg-slate-900/60 p-2.5 rounded-xl border border-emerald-100 dark:border-slate-800">{note.content[key]}</p>
              )}
              <p className="mt-1 text-[10px] text-emerald-600 dark:text-slate-400">{hint}</p>
            </div>
          ))}

          {editing && (
            <div className="flex justify-end gap-2">
              <button disabled={busy} onClick={cancelEdit} className="rounded-xl px-3 py-2 text-xs text-emerald-800 dark:text-slate-300 hover:bg-emerald-100 dark:hover:bg-slate-700">
                Batal
              </button>
              <button disabled={busy} onClick={() => onReview(note.note_id, content)} className="rounded-xl bg-emerald-600 hover:bg-emerald-500 px-3 py-2 text-xs font-semibold text-white disabled:opacity-50 shadow-sm">
                {busy ? 'Meninjau…' : 'Simpan perubahan'}
              </button>
            </div>
          )}

          {note.status === 'pending_confirmation' && note.pending_content && (
            <div className="rounded-xl border border-amber-500/30 dark:border-amber-500/20 bg-amber-500/10 dark:bg-amber-950/30 p-3.5">
              <p className="text-xs font-bold text-amber-800 dark:text-amber-300">Bot mendeteksi perubahan berikut:</p>
              <ul className="mt-2 space-y-1 text-[11px] text-amber-900 dark:text-amber-200">
                {note.changes.map(change => <li key={change.field}>• {change.field} diperbarui</li>)}
              </ul>
              <p className="mt-3 text-[11px] text-emerald-900 dark:text-slate-200 font-semibold">Terima versi revisi ini?</p>
              <div className="mt-2 flex gap-2">
                <button disabled={busy} onClick={() => onConfirm(note.note_id, true)} className="rounded-xl bg-emerald-600 hover:bg-emerald-500 px-3 py-2 text-xs font-semibold text-white disabled:opacity-50 shadow-sm">Terima perubahan</button>
                <button disabled={busy} onClick={() => onConfirm(note.note_id, false)} className="rounded-xl border border-emerald-300 dark:border-slate-700 px-3 py-2 text-xs text-emerald-900 dark:text-slate-300 hover:bg-emerald-100 dark:hover:bg-slate-800 disabled:opacity-50">Tolak</button>
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
