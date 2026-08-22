'use client';

import { useState } from 'react';
import { RAGService, type RAGChunkResult } from '@/services/rag.service';

export default function RAGSearchExplorer() {
  const [query, setQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState<RAGChunkResult[]>([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || searching) return;

    setSearching(true);
    setError('');
    try {
      const data = await RAGService.search({
        query: query.trim(),
        top_k: 4,
        category_filter: categoryFilter || null,
      });
      setResults(data.chunks || []);
      setHasSearched(true);
    } catch (err: any) {
      setError(err.message || 'Pencarian RAG gagal.');
    } finally {
      setSearching(false);
    }
  };

  const quickSearches = [
    'Metformin eGFR batas aman',
    'Lisinopril kontraindikasi ginjal',
    'Panduan ADA 2025 Diabetes Mellitus',
    'Acute Coronary Syndrome Clopidogrel',
  ];

  return (
    <div className="bg-white border border-emerald-200 rounded-2xl p-6 shadow-lg space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h2 className="text-lg font-bold text-emerald-950 flex items-center gap-2">
            <span>🔍</span>
            <span>Eksplorasi Vektor &amp; Pencarian Semantik RAG</span>
          </h2>
          <p className="text-xs text-emerald-700 mt-0.5">
            Uji pencarian dokumen medis berbasis embedding Gemini text-embedding-004 &amp; reranking Qdrant.
          </p>
        </div>
      </div>

      {/* Quick Search Pills */}
      <div className="flex gap-2 overflow-x-auto pb-1">
        {quickSearches.map((qs, i) => (
          <button
            key={i}
            type="button"
            onClick={() => {
              setQuery(qs);
            }}
            className="px-3 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 rounded-full border border-emerald-200 whitespace-nowrap text-xs transition-colors"
          >
            {qs}
          </button>
        ))}
      </div>

      <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          required
          placeholder="Ketik pertanyaan klinis, nama obat, atau diagnosis (mis. 'Metformin eGFR')..."
          className="flex-1 px-4 py-2.5 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-950 placeholder-emerald-400 focus:outline-none focus:border-emerald-500"
        />
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="px-3 py-2.5 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-900 focus:outline-none focus:border-emerald-500"
        >
          <option value="">Semua Kategori</option>
          <option value="disease">Penyakit</option>
          <option value="medicine">Obat</option>
          <option value="terminology">Terminologi</option>
          <option value="guideline">Panduan</option>
        </select>
        <button
          type="submit"
          disabled={searching}
          className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold text-xs rounded-xl shadow-md transition-all shrink-0"
        >
          {searching ? 'Mencari Vektor…' : 'Cari RAG'}
        </button>
      </form>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl text-xs">
          {error}
        </div>
      )}

      {/* Results */}
      {hasSearched && (
        <div className="space-y-3 pt-2">
          <div className="text-xs font-semibold text-emerald-800">
            Ditemukan {results.length} potongan informasi klinis relevan:
          </div>

          {results.length === 0 ? (
            <p className="text-xs text-emerald-700 dark:text-slate-400 py-4 text-center font-medium bg-emerald-50 dark:bg-slate-800/60 rounded-xl border border-emerald-200 dark:border-slate-700">
              Mohon maaf permintaan anda belum tersedia dipengetahuan saya
            </p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {results.map((res, idx) => (
                <div
                  key={idx}
                  className="p-4 bg-emerald-50/70 border border-emerald-200 rounded-xl flex flex-col justify-between space-y-2 hover:border-emerald-300 transition-colors"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <span className="font-bold text-xs text-emerald-950 truncate">{res.title}</span>
                      <span className="px-2 py-0.5 rounded-full bg-emerald-200/70 text-emerald-900 font-mono text-[10px] font-bold shrink-0">
                        Score: {(res.reranked_score * 100).toFixed(1)}%
                      </span>
                    </div>

                    <div className="flex flex-wrap gap-1.5 mb-2">
                      <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded text-[10px] font-semibold">
                        {res.category}
                      </span>
                      {res.specialty && (
                        <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded text-[10px]">
                          {res.specialty}
                        </span>
                      )}
                      {res.icd10_code && (
                        <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 font-mono rounded text-[10px]">
                          ICD-10: {res.icd10_code}
                        </span>
                      )}
                      {res.rxnorm_code && (
                        <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 font-mono rounded text-[10px]">
                          RxNorm: {res.rxnorm_code}
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-emerald-900 leading-relaxed bg-white/80 p-2.5 rounded-lg border border-emerald-100 whitespace-pre-wrap font-sans">
                      {res.chunk_snippet}
                    </p>
                  </div>

                  {res.evidence_level && (
                    <div className="text-[10px] text-emerald-700 italic border-t border-emerald-200/50 pt-1.5 mt-1">
                      📚 {res.evidence_level}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
