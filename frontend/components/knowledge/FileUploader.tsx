'use client';
import { useRef, useState } from 'react';

interface FileUploaderProps {
  onUpload: (file: File, category: string, specialty: string) => Promise<boolean>;
  uploading: boolean;
}

export default function FileUploader({ onUpload, uploading }: FileUploaderProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [category, setCategory] = useState('disease');
  const [specialty, setSpecialty] = useState('Kedokteran Umum');
  const [dragOver, setDragOver] = useState(false);
  const [selectedFileName, setSelectedFileName] = useState('');
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedback(null);
    const file = fileRef.current?.files?.[0];
    if (!file) {
      setFeedback({ type: 'error', message: 'Silakan pilih file terlebih dahulu.' });
      return;
    }

    const ok = await onUpload(file, category, specialty);
    if (ok) {
      setFeedback({
        type: 'success',
        message: `File "${file.name}" berhasil diunggah dan diindeks ke Qdrant.`,
      });
      setSelectedFileName('');
      if (fileRef.current) fileRef.current.value = '';
    } else {
      setFeedback({
        type: 'error',
        message: 'Gagal mengunggah file. Pastikan format teks/json valid.',
      });
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFileName(file.name);
      setFeedback(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && fileRef.current) {
      const dt = new DataTransfer();
      dt.items.add(file);
      fileRef.current.files = dt.files;
      setSelectedFileName(file.name);
      setFeedback(null);
    }
  };

  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return '📕';
    if (ext === 'docx' || ext === 'doc') return '📘';
    if (ext === 'json') return '📦';
    if (ext === 'md' || ext === 'txt') return '📄';
    return '📁';
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm flex flex-col justify-between transition-colors">
      <div>
        <div className="flex items-center justify-between gap-2 mb-1">
          <h2 className="text-base font-bold text-emerald-950 dark:text-white flex items-center gap-2">
            <span>📄</span>
            <span>Unggah Dokumen Medis</span>
          </h2>
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
            ✨ AI Generative AI Auto-Keywords
          </span>
        </div>
        <p className="text-xs text-emerald-700 dark:text-slate-400 mb-4">
          Unggah panduan klinis, jurnal, atau protokol format <strong>PDF, DOCX, TXT, MD, JSON</strong> untuk diindeks ke Qdrant.
        </p>

        {feedback && (
          <div
            className={`mb-4 p-3 rounded-2xl border text-xs flex items-center justify-between ${feedback.type === 'success'
                ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-800 text-emerald-900 dark:text-emerald-300'
                : 'bg-red-50 dark:bg-red-950/40 border-red-300 dark:border-red-800 text-red-700 dark:text-red-300'
              }`}
          >
            <div className="flex items-center gap-2">
              <span>{feedback.type === 'success' ? '✅' : '⚠️'}</span>
              <span>{feedback.message}</span>
            </div>
            <button
              type="button"
              onClick={() => setFeedback(null)}
              className="text-xs opacity-70 hover:opacity-100"
            >
              ✕
            </button>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Drop Zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            className={`relative border-2 border-dashed rounded-2xl p-6 text-center transition-all cursor-pointer ${dragOver
                ? 'border-emerald-500 bg-emerald-500/10 dark:bg-emerald-950/30'
                : selectedFileName
                  ? 'border-emerald-500 bg-emerald-50/50 dark:bg-slate-800/60'
                  : 'border-emerald-300 dark:border-slate-700 hover:border-emerald-500 hover:bg-emerald-50/30 dark:hover:bg-slate-800/40'
              }`}
            onClick={() => fileRef.current?.click()}
          >
            <div className="text-3xl mb-2">
              {selectedFileName ? getFileIcon(selectedFileName) : '📤'}
            </div>
            {selectedFileName ? (
              <div>
                <p className="text-xs text-emerald-950 dark:text-slate-100 font-bold truncate px-4">
                  {selectedFileName}
                </p>
                <p className="text-[10px] text-emerald-600 dark:text-emerald-400 mt-1 font-semibold">
                  Klik untuk mengganti file
                </p>
              </div>
            ) : (
              <div>
                <p className="text-xs text-emerald-800 dark:text-slate-200 font-medium">
                  Seret file ke sini, atau <span className="text-emerald-600 dark:text-emerald-400 underline font-bold">klik untuk memilih</span>
                </p>
                <p className="text-[10px] text-emerald-600 dark:text-slate-400 mt-1">
                  Mendukung <strong>.pdf, .docx, .doc, .txt, .md, .json, .csv</strong>
                </p>
              </div>
            )}
            <input
              ref={fileRef}
              type="file"
              accept=".pdf,.docx,.doc,.txt,.md,.json,.csv"
              className="hidden"
              onChange={handleFileChange}
            />
          </div>

          {/* AI Auto-Extraction Badge Banner */}
          <div className="p-2.5 bg-emerald-50/60 dark:bg-slate-800/60 rounded-xl border border-emerald-200/60 dark:border-slate-700 text-[11px] text-emerald-800 dark:text-slate-300 flex items-center gap-2">
            <span className="text-sm">🤖</span>
            <span>
              <strong>Generative AI AI Integration:</strong> Teks diekstrak otomatis dan kata kunci klinis dianalisis langsung menggunakan model LLM Generative AI.
            </span>
          </div>

          {/* Category & Specialty */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[10px] font-bold text-emerald-800 dark:text-slate-300 uppercase tracking-wider mb-1">
                Kategori
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl p-2.5 text-xs text-emerald-950 dark:text-slate-100 focus:border-emerald-500 focus:outline-none"
              >
                <option value="disease">Penyakit (Disease)</option>
                <option value="medicine">Obat / Farmakologi</option>
                <option value="terminology">Terminologi Klinis</option>
                <option value="guideline">Panduan Praktik Klinis</option>
              </select>
            </div>
            <div>
              <label className="block text-[10px] font-bold text-emerald-800 dark:text-slate-300 uppercase tracking-wider mb-1">
                Spesialisasi
              </label>
              <input
                type="text"
                value={specialty}
                onChange={(e) => setSpecialty(e.target.value)}
                placeholder="Contoh: Pulmonologi, Kardiologi"
                className="w-full bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl p-2.5 text-xs text-emerald-950 dark:text-slate-100 focus:border-emerald-500 focus:outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={uploading}
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-md shadow-emerald-600/20 transition-all active:scale-[0.98] flex items-center justify-center gap-2"
          >
            {uploading ? (
              <>
                <span className="animate-spin">⏳</span>
                <span>Mengekstrak teks & menganalisis kata kunci Generative AI…</span>
              </>
            ) : (
              <>
                <span>🚀</span>
                <span>Unggah &amp; Ekstrak ke Qdrant</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}


