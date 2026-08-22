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

  return (
    <div className="bg-white border border-emerald-200 rounded-2xl p-6 shadow-lg flex flex-col justify-between">
      <div>
        <h2 className="text-lg font-bold text-emerald-950 mb-1">📄 Unggah Dokumen Medis</h2>
        <p className="text-xs text-emerald-700 mb-4">
          Unggah panduan atau protokol klinis .txt, .md, atau .json untuk diindeks ke Qdrant.
        </p>

        {feedback && (
          <div
            className={`mb-4 p-3 rounded-xl border text-xs ${
              feedback.type === 'success'
                ? 'bg-emerald-50 border-emerald-300 text-emerald-800'
                : 'bg-red-50 border-red-300 text-red-700'
            }`}
          >
            {feedback.message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Drop Zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            className={`relative border-2 border-dashed rounded-xl p-6 text-center transition-colors cursor-pointer ${
              dragOver
                ? 'border-emerald-500 bg-emerald-500/10'
                : selectedFileName
                ? 'border-emerald-500 bg-emerald-50/50'
                : 'border-emerald-300 hover:border-emerald-500'
            }`}
            onClick={() => fileRef.current?.click()}
          >
            <div className="text-2xl mb-2">{selectedFileName ? '📄' : '📁'}</div>
            {selectedFileName ? (
              <p className="text-xs text-emerald-950 font-semibold truncate px-4">
                {selectedFileName}
              </p>
            ) : (
              <p className="text-xs text-emerald-700">
                Seret file ke sini, atau <span className="text-emerald-700 underline font-semibold">klik untuk memilih</span>
              </p>
            )}
            <p className="text-[10px] text-emerald-600 mt-1">Mendukung .txt, .md, .json</p>
            <input
              ref={fileRef}
              type="file"
              accept=".txt,.md,.json,.csv"
              className="hidden"
              onChange={handleFileChange}
            />
          </div>

          {/* Category & Specialty */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[10px] font-semibold text-emerald-700 uppercase mb-1">Kategori</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-emerald-50 border border-emerald-200 rounded-lg p-2 text-xs text-emerald-900 focus:border-emerald-500 focus:outline-none"
              >
                <option value="disease">Penyakit</option>
                <option value="medicine">Obat</option>
                <option value="terminology">Terminologi</option>
                <option value="guideline">Panduan Klinis</option>
              </select>
            </div>
            <div>
              <label className="block text-[10px] font-semibold text-emerald-700 uppercase mb-1">Spesialisasi</label>
              <input
                type="text"
                value={specialty}
                onChange={(e) => setSpecialty(e.target.value)}
                className="w-full bg-emerald-50 border border-emerald-200 rounded-lg p-2 text-xs text-emerald-900 focus:border-emerald-500 focus:outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={uploading}
            className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold text-xs rounded-xl shadow-md transition-all active:scale-[0.98]"
          >
            {uploading ? 'Mengunggah & mengindeks…' : 'Unggah & indeks ke Qdrant'}
          </button>
        </form>
      </div>
    </div>
  );
}

