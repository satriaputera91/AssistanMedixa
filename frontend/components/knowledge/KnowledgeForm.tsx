'use client';
import { useState } from 'react';
import type { KnowledgeFormInput } from '@/services/rag.service';

interface KnowledgeFormProps {
  onSubmit: (input: KnowledgeFormInput) => Promise<boolean>;
  submitting: boolean;
}

export default function KnowledgeForm({ onSubmit, submitting }: KnowledgeFormProps) {
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState<string>('disease');
  const [specialty, setSpecialty] = useState('Kedokteran Umum');
  const [icd10Code, setIcd10Code] = useState('');
  const [rxnormCode, setRxnormCode] = useState('');
  const [synonyms, setSynonyms] = useState('');
  const [keywords, setKeywords] = useState('');
  const [evidenceLevel, setEvidenceLevel] = useState('');
  const [content, setContent] = useState('');
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedback(null);

    const ok = await onSubmit({
      title,
      category,
      specialty,
      icd10_code: icd10Code || undefined,
      rxnorm_code: rxnormCode || undefined,
      synonyms: synonyms ? synonyms.split(',').map(s => s.trim()).filter(Boolean) : [],
      keywords: keywords ? keywords.split(',').map(s => s.trim()).filter(Boolean) : [],
      evidence_level: evidenceLevel || undefined,
      content,
    });

    if (ok) {
      setFeedback({
        type: 'success',
        message: `Pengetahuan "${title}" berhasil diindeks ke koleksi vektor Qdrant.`,
      });
      setTitle('');
      setIcd10Code('');
      setRxnormCode('');
      setSynonyms('');
      setKeywords('');
      setEvidenceLevel('');
      setContent('');
    } else {
      setFeedback({
        type: 'error',
        message: 'Gagal menyimpan pengetahuan ke Qdrant.',
      });
    }
  };

  return (
    <div className="bg-white border border-emerald-200 rounded-2xl p-6 shadow-lg">
      <h2 className="text-lg font-bold text-emerald-950 mb-1">📝 Tambah Pengetahuan Terstruktur</h2>
      <p className="text-xs text-emerald-700 mb-4">
        Tambahkan pengetahuan medis berkode ICD-10 / RxNorm ke Qdrant RAG.
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

      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          placeholder="Judul (mis. Panduan Penatalaksanaan Asma)"
          className="w-full bg-emerald-50 border border-emerald-200 rounded-lg p-2.5 text-xs text-emerald-900 placeholder-emerald-400 focus:border-emerald-500 focus:outline-none"
        />

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="bg-emerald-50 border border-emerald-200 rounded-lg p-2 text-xs text-emerald-900 focus:border-emerald-500 focus:outline-none"
          >
            <option value="disease">Penyakit</option>
            <option value="medicine">Obat</option>
            <option value="terminology">Terminologi</option>
          </select>
          <input
            type="text"
            value={specialty}
            onChange={(e) => setSpecialty(e.target.value)}
            placeholder="Spesialisasi"
            className="bg-emerald-50 border border-emerald-200 rounded-lg p-2 text-xs text-emerald-900 focus:border-emerald-500 focus:outline-none"
          />
          <input
            type="text"
            value={icd10Code}
            onChange={(e) => setIcd10Code(e.target.value)}
            placeholder="ICD-10 Code"
            className="bg-emerald-50 border border-emerald-200 rounded-lg p-2 text-xs text-emerald-900 focus:border-emerald-500 focus:outline-none"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          <input
            type="text"
            value={rxnormCode}
            onChange={(e) => setRxnormCode(e.target.value)}
            placeholder="RxNorm Code"
            className="bg-emerald-50 border border-emerald-200 rounded-lg p-2 text-xs text-emerald-900 focus:border-emerald-500 focus:outline-none"
          />
          <input
            type="text"
            value={synonyms}
            onChange={(e) => setSynonyms(e.target.value)}
            placeholder="Sinonim (pisahkan dengan koma)"
            className="bg-emerald-50 border border-emerald-200 rounded-lg p-2 text-xs text-emerald-900 focus:border-emerald-500 focus:outline-none"
          />
          <input
            type="text"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            placeholder="Kata kunci (pisahkan dengan koma)"
            className="bg-emerald-50 border border-emerald-200 rounded-lg p-2 text-xs text-emerald-900 focus:border-emerald-500 focus:outline-none"
          />
        </div>

        <input
          type="text"
          value={evidenceLevel}
          onChange={(e) => setEvidenceLevel(e.target.value)}
          placeholder="Tingkat bukti (mis. ADA 2025 Level A)"
          className="w-full bg-emerald-50 border border-emerald-200 rounded-lg p-2 text-xs text-emerald-900 placeholder-emerald-400 focus:border-emerald-500 focus:outline-none"
        />

        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
          rows={4}
          placeholder="Isi teks klinis (gunakan header ### untuk setiap bagian)..."
          className="w-full bg-emerald-50 border border-emerald-200 rounded-lg p-2.5 text-xs text-emerald-900 placeholder-emerald-400 focus:border-emerald-500 focus:outline-none resize-none"
        />

        <button
          type="submit"
          disabled={submitting}
          className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold text-xs rounded-xl shadow-md transition-all active:scale-[0.98]"
        >
          {submitting ? 'Mengindeks…' : 'Simpan ke koleksi vektor Qdrant'}
        </button>
      </form>
    </div>
  );
}

