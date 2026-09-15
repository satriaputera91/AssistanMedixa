'use client';
import { useState } from 'react';
import { RAGService, type KnowledgeFormInput } from '@/services/rag.service';

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
  const [extractingKeywords, setExtractingKeywords] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  const handleExtractKeywordsAI = async () => {
    if (!content.trim() && !title.trim()) {
      setFeedback({
        type: 'error',
        message: 'Mohon isi judul atau konten teks terlebih dahulu untuk mengekstrak kata kunci.',
      });
      return;
    }

    setExtractingKeywords(true);
    setFeedback(null);
    try {
      const extracted = await RAGService.extractKeywords(content || title, title);
      if (extracted && extracted.length > 0) {
        setKeywords(extracted.join(', '));
        if (!synonyms.trim() && title.trim()) {
          setSynonyms(extracted.slice(0, 3).join(', '));
        }
        setFeedback({
          type: 'success',
          message: `✨ Berhasil mengekstrak ${extracted.length} kata kunci klinis dengan AI Generative AI.`,
        });
      } else {
        setFeedback({
          type: 'error',
          message: 'AI tidak menemukan kata kunci spesifik dari teks yang diberikan.',
        });
      }
    } catch (e: any) {
      console.error('Failed to extract keywords:', e);
      setFeedback({
        type: 'error',
        message: e.message || 'Gagal mengekstrak kata kunci dengan AI.',
      });
    } finally {
      setExtractingKeywords(false);
    }
  };

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
    <div className="bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm transition-colors">
      <div className="flex items-center justify-between mb-1">
        <h2 className="text-base font-bold text-emerald-950 dark:text-white flex items-center gap-2">
          <span>📝</span>
          <span>Tambah Pengetahuan Terstruktur</span>
        </h2>
        <span className="text-[10px] font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-100/70 dark:bg-slate-800 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-slate-700">
          Qdrant RAG Ingestion
        </span>
      </div>
      <p className="text-xs text-emerald-700 dark:text-slate-400 mb-4">
        Tambahkan pengetahuan medis berkode ICD-10 / RxNorm atau ekstrak kata kunci otomatis dengan AI Generative AI.
      </p>

      {feedback && (
        <div
          className={`mb-4 p-3 rounded-2xl border text-xs flex items-center justify-between ${feedback.type === 'success'
              ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-800 text-emerald-900 dark:text-emerald-300'
              : feedback.type === 'info'
                ? 'bg-blue-50 dark:bg-blue-950/40 border-blue-300 dark:border-blue-800 text-blue-900 dark:text-blue-300'
                : 'bg-red-50 dark:bg-red-950/40 border-red-300 dark:border-red-800 text-red-700 dark:text-red-300'
            }`}
        >
          <div className="flex items-center gap-2">
            <span>{feedback.type === 'success' ? '✅' : feedback.type === 'info' ? 'ℹ️' : '⚠️'}</span>
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

      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="block text-[10px] font-bold text-emerald-800 dark:text-slate-300 uppercase tracking-wider mb-1">
            Judul Dokumen <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            placeholder="Judul (mis. Panduan Penatalaksanaan Asma Bronkial Akut)"
            className="w-full bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl p-2.5 text-xs text-emerald-950 dark:text-slate-100 placeholder-emerald-400 dark:placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          <div>
            <label className="block text-[10px] font-bold text-emerald-800 dark:text-slate-300 uppercase tracking-wider mb-1">
              Kategori
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl p-2.5 text-xs text-emerald-950 dark:text-slate-100 focus:border-emerald-500 focus:outline-none"
            >
              <option value="disease">Penyakit</option>
              <option value="medicine">Obat / Farmakologi</option>
              <option value="terminology">Terminologi</option>
              <option value="guideline">Panduan Klinis</option>
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
              placeholder="Spesialisasi"
              className="w-full bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl p-2.5 text-xs text-emerald-950 dark:text-slate-100 focus:border-emerald-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-[10px] font-bold text-emerald-800 dark:text-slate-300 uppercase tracking-wider mb-1">
              Kode ICD-10
            </label>
            <input
              type="text"
              value={icd10Code}
              onChange={(e) => setIcd10Code(e.target.value)}
              placeholder="J45.909"
              className="w-full bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl p-2.5 text-xs font-mono text-emerald-950 dark:text-slate-100 focus:border-emerald-500 focus:outline-none"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <div>
            <label className="block text-[10px] font-bold text-emerald-800 dark:text-slate-300 uppercase tracking-wider mb-1">
              Kode RxNorm
            </label>
            <input
              type="text"
              value={rxnormCode}
              onChange={(e) => setRxnormCode(e.target.value)}
              placeholder="RxNorm (mis. 6809)"
              className="w-full bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl p-2.5 text-xs font-mono text-emerald-950 dark:text-slate-100 focus:border-emerald-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-[10px] font-bold text-emerald-800 dark:text-slate-300 uppercase tracking-wider mb-1">
              Tingkat Bukti / Referensi
            </label>
            <input
              type="text"
              value={evidenceLevel}
              onChange={(e) => setEvidenceLevel(e.target.value)}
              placeholder="mis. GINA 2025 Level A"
              className="w-full bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl p-2.5 text-xs text-emerald-950 dark:text-slate-100 placeholder-emerald-400 dark:placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
            />
          </div>
        </div>

        <div>
          <label className="block text-[10px] font-bold text-emerald-800 dark:text-slate-300 uppercase tracking-wider mb-1">
            Sinonim &amp; Istilah Terkait
          </label>
          <input
            type="text"
            value={synonyms}
            onChange={(e) => setSynonyms(e.target.value)}
            placeholder="Sinonim klinis (pisahkan dengan koma, mis. asma attack, serangan sesak napas)"
            className="w-full bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl p-2.5 text-xs text-emerald-950 dark:text-slate-100 focus:border-emerald-500 focus:outline-none"
          />
        </div>

        {/* Content Textarea */}
        <div>
          <label className="block text-[10px] font-bold text-emerald-800 dark:text-slate-300 uppercase tracking-wider mb-1">
            Isi Teks Klinis <span className="text-red-500">*</span>
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
            rows={4}
            placeholder="Isi teks klinis (gunakan header ### untuk setiap sub-bagian seperti Kriteria Diagnostik, Rekomendasi Terapi, Dosis)..."
            className="w-full bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl p-2.5 text-xs text-emerald-950 dark:text-slate-100 placeholder-emerald-400 dark:placeholder-slate-500 focus:border-emerald-500 focus:outline-none resize-none font-sans"
          />
        </div>

        {/* Keywords Section with AI Extraction Trigger */}
        <div>
          <div className="flex items-center justify-between gap-2 mb-1">
            <label className="block text-[10px] font-bold text-emerald-800 dark:text-slate-300 uppercase tracking-wider">
              Kata Kunci (Keywords)
            </label>
            <button
              type="button"
              onClick={handleExtractKeywordsAI}
              disabled={extractingKeywords}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] font-bold bg-teal-100 dark:bg-teal-950/60 text-teal-800 dark:text-teal-300 hover:bg-teal-200 dark:hover:bg-teal-900 border border-teal-200 dark:border-teal-800 transition-colors disabled:opacity-50"
            >
              {extractingKeywords ? (
                <>
                  <span className="animate-spin">⏳</span>
                  <span>Menganalisis dengan Generative AI…</span>
                </>
              ) : (
                <>
                  <span>✨</span>
                  <span>Ekstrak Otomatis dg Generative AI AI</span>
                </>
              )}
            </button>
          </div>
          <input
            type="text"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            placeholder="Kata kunci (pisahkan dengan koma atau klik tombol Ekstrak AI di atas)"
            className="w-full bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl p-2.5 text-xs text-emerald-950 dark:text-slate-100 focus:border-emerald-500 focus:outline-none font-medium"
          />
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-md shadow-emerald-600/20 transition-all active:scale-[0.98] mt-2 flex items-center justify-center gap-2"
        >
          {submitting ? (
            <>
              <span className="animate-spin">⏳</span>
              <span>Mengindeks ke Qdrant…</span>
            </>
          ) : (
            <>
              <span>💾</span>
              <span>Simpan ke Koleksi Vektor Qdrant</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}


