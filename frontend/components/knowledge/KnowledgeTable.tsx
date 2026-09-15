'use client';

import { useState, useMemo, useEffect } from 'react';
import type { KnowledgeItem } from '@/services/rag.service';

interface KnowledgeTableProps {
  items: KnowledgeItem[];
  onDelete: (itemId: string) => void;
}

const categoryColors: Record<string, string> = {
  disease: 'bg-emerald-500/15 text-emerald-800 dark:text-emerald-300 border-emerald-500/30',
  medicine: 'bg-teal-500/15 text-teal-800 dark:text-teal-300 border-teal-500/30',
  terminology: 'bg-cyan-500/15 text-cyan-800 dark:text-cyan-300 border-cyan-500/30',
  guideline: 'bg-amber-500/15 text-amber-800 dark:text-amber-300 border-amber-500/30',
  document: 'bg-indigo-500/15 text-indigo-800 dark:text-indigo-300 border-indigo-500/30',
};

const categoryLabels: Record<string, string> = {
  disease: 'PENYAKIT',
  medicine: 'OBAT',
  terminology: 'TERMINOLOGI',
  guideline: 'PANDUAN',
  document: 'DOKUMEN',
};

export default function KnowledgeTable({ items, onDelete }: KnowledgeTableProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedSpecialty, setSelectedSpecialty] = useState('all');

  // Pagination States
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);

  // Detail Modal State
  const [viewingItem, setViewingItem] = useState<KnowledgeItem | null>(null);

  // Delete Confirmation State
  const [deleteConfirmItem, setDeleteConfirmItem] = useState<KnowledgeItem | null>(null);

  // Extract unique specialties for filter
  const availableSpecialties = useMemo(() => {
    const set = new Set<string>();
    items.forEach((it) => {
      if (it.specialty) set.add(it.specialty);
    });
    return Array.from(set).sort();
  }, [items]);

  // Filtered List
  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      const q = searchTerm.toLowerCase().trim();
      const matchesSearch =
        !q ||
        item.title.toLowerCase().includes(q) ||
        (item.specialty && item.specialty.toLowerCase().includes(q)) ||
        (item.icd10_code && item.icd10_code.toLowerCase().includes(q)) ||
        (item.rxnorm_code && item.rxnorm_code.toLowerCase().includes(q)) ||
        (item.keywords && item.keywords.some((k) => k.toLowerCase().includes(q))) ||
        (item.synonyms && item.synonyms.some((s) => s.toLowerCase().includes(q)));

      const matchesCategory =
        selectedCategory === 'all' || item.category.toLowerCase() === selectedCategory.toLowerCase();

      const matchesSpecialty =
        selectedSpecialty === 'all' || item.specialty === selectedSpecialty;

      return matchesSearch && matchesCategory && matchesSpecialty;
    });
  }, [items, searchTerm, selectedCategory, selectedSpecialty]);

  // Reset page to 1 when filters or page size change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, selectedCategory, selectedSpecialty, pageSize]);

  // Pagination Calculations
  const totalItems = filteredItems.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const safePage = Math.min(currentPage, totalPages);

  const paginatedItems = useMemo(() => {
    const startIndex = (safePage - 1) * pageSize;
    return filteredItems.slice(startIndex, startIndex + pageSize);
  }, [filteredItems, safePage, pageSize]);

  const startIndexDisplay = totalItems === 0 ? 0 : (safePage - 1) * pageSize + 1;
  const endIndexDisplay = Math.min(safePage * pageSize, totalItems);

  // Pagination Page Number Generator with ellipsis
  const pageNumbers = useMemo(() => {
    const pages: (number | string)[] = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      if (safePage > 3) pages.push('...');

      const start = Math.max(2, safePage - 1);
      const end = Math.min(totalPages - 1, safePage + 1);
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (safePage < totalPages - 2) pages.push('...');
      pages.push(totalPages);
    }
    return pages;
  }, [safePage, totalPages]);

  return (
    <div className="bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm transition-colors">
      {/* Detail Modal */}
      {viewingItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white dark:bg-slate-900 border border-emerald-300 dark:border-slate-800 rounded-3xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
            <div className="px-6 py-5 border-b border-emerald-100 dark:border-slate-800 flex items-center justify-between bg-emerald-50/40 dark:bg-slate-800/50">
              <div className="flex items-center gap-3">
                <span className="text-2xl">📚</span>
                <div>
                  <h3 className="text-base font-bold text-emerald-950 dark:text-white">
                    Detail Dokumen Pengetahuan
                  </h3>
                  <p className="text-xs text-emerald-700 dark:text-slate-400">
                    ID: {viewingItem.id} • {viewingItem.chunks_count} Vector Chunks
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setViewingItem(null)}
                className="w-8 h-8 rounded-xl flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                ✕
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4 text-xs">
              <div>
                <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Judul Dokumen</label>
                <div className="text-sm font-bold text-emerald-950 dark:text-white mt-0.5">
                  {viewingItem.title}
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3.5 bg-emerald-50/40 dark:bg-slate-800/60 rounded-2xl border border-emerald-100 dark:border-slate-700">
                <div>
                  <span className="text-[10px] text-slate-400 font-semibold block">Kategori</span>
                  <span className="font-bold text-emerald-900 dark:text-emerald-300 uppercase">
                    {viewingItem.category}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-semibold block">Spesialisasi</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">
                    {viewingItem.specialty || '—'}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-semibold block">Kode Medis</span>
                  <span className="font-mono font-bold text-slate-800 dark:text-slate-200">
                    {viewingItem.icd10_code || viewingItem.rxnorm_code || '—'}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-semibold block">Tingkat Bukti</span>
                  <span className="font-medium text-slate-800 dark:text-slate-200 truncate block">
                    {viewingItem.evidence_level || '—'}
                  </span>
                </div>
              </div>

              {/* Keywords */}
              <div>
                <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1.5">
                  Kata Kunci Ekstraksi Generative AI AI
                </label>
                {viewingItem.keywords && viewingItem.keywords.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {viewingItem.keywords.map((kw, i) => (
                      <span
                        key={i}
                        className="px-2.5 py-1 rounded-xl text-[11px] font-semibold bg-teal-50 dark:bg-teal-950/60 text-teal-800 dark:text-teal-300 border border-teal-200 dark:border-teal-800 flex items-center gap-1"
                      >
                        <span className="text-[10px]">✨</span>
                        <span>{kw}</span>
                      </span>
                    ))}
                  </div>
                ) : (
                  <span className="text-slate-400 italic">Tidak ada kata kunci terlampir</span>
                )}
              </div>

              {/* Synonyms */}
              {viewingItem.synonyms && viewingItem.synonyms.length > 0 && (
                <div>
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1.5">
                    Sinonim &amp; Istilah Terkait
                  </label>
                  <div className="flex flex-wrap gap-1.5">
                    {viewingItem.synonyms.map((syn, i) => (
                      <span
                        key={i}
                        className="px-2.5 py-1 rounded-xl text-[11px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700"
                      >
                        {syn}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="px-6 py-4 border-t border-emerald-100 dark:border-slate-800 flex justify-end">
              <button
                type="button"
                onClick={() => setViewingItem(null)}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-xl transition-all"
              >
                Tutup
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirmItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white dark:bg-slate-900 border border-red-200 dark:border-red-900/50 rounded-3xl shadow-2xl w-full max-w-md p-6 animate-in zoom-in-95 duration-200">
            <div className="flex items-center gap-3 text-red-600 dark:text-red-400 mb-3">
              <div className="w-10 h-10 rounded-2xl bg-red-100 dark:bg-red-950/50 flex items-center justify-center text-xl">
                🗑️
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Hapus Dokumen Pengetahuan?
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Dokumen dan seluruh {deleteConfirmItem.chunks_count} titik vektor Qdrant akan dihapus.
                </p>
              </div>
            </div>

            <div className="my-4 p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200 dark:border-slate-700 text-xs">
              <div className="font-bold text-slate-900 dark:text-white line-clamp-2">
                {deleteConfirmItem.title}
              </div>
              <div className="text-slate-500 dark:text-slate-400 mt-1">
                Kategori: <strong className="uppercase">{deleteConfirmItem.category}</strong> • Spesialisasi: {deleteConfirmItem.specialty}
              </div>
            </div>

            <div className="flex items-center gap-3 mt-5">
              <button
                type="button"
                onClick={() => setDeleteConfirmItem(null)}
                className="flex-1 py-2.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-semibold rounded-xl text-xs transition-colors"
              >
                Batal
              </button>
              <button
                type="button"
                onClick={() => {
                  onDelete(deleteConfirmItem.id);
                  setDeleteConfirmItem(null);
                }}
                className="flex-1 py-2.5 bg-red-600 hover:bg-red-500 text-white font-semibold rounded-xl text-xs transition-all shadow-md shadow-red-600/20 active:scale-[0.98]"
              >
                Ya, Hapus Dokumen
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header & Search / Filter Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xl">📚</span>
            <h2 className="text-lg font-bold text-emerald-950 dark:text-white">
              Vektor Pengetahuan Qdrant Terindeks
            </h2>
          </div>
          <p className="text-xs text-emerald-700 dark:text-slate-400 mt-0.5">
            Total <strong>{items.length} dokumen</strong> panduan, terminologi, dan literatur klinis.
          </p>
        </div>

        {/* Filter Controls Bar */}
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="relative">
            <input
              type="text"
              placeholder="Cari judul, ICD, kata kunci..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="px-3.5 py-2 bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-xs text-emerald-950 dark:text-slate-100 placeholder-emerald-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 w-52 sm:w-64"
            />
            {searchTerm && (
              <button
                type="button"
                onClick={() => setSearchTerm('')}
                className="absolute right-2.5 top-2 text-slate-400 hover:text-slate-600 text-xs"
              >
                ✕
              </button>
            )}
          </div>

          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-xs text-emerald-950 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
          >
            <option value="all">Semua Kategori</option>
            <option value="disease">Penyakit</option>
            <option value="medicine">Obat</option>
            <option value="terminology">Terminologi</option>
            <option value="guideline">Panduan</option>
            <option value="document">Dokumen</option>
          </select>

          {availableSpecialties.length > 0 && (
            <select
              value={selectedSpecialty}
              onChange={(e) => setSelectedSpecialty(e.target.value)}
              className="px-3 py-2 bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-xs text-emerald-950 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
            >
              <option value="all">Semua Spesialisasi</option>
              {availableSpecialties.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          )}

          {/* Page Size Selector */}
          <div className="flex items-center gap-1.5 pl-1">
            <span className="text-[11px] text-slate-400 hidden sm:inline">Per hal:</span>
            <select
              value={pageSize}
              onChange={(e) => setPageSize(Number(e.target.value))}
              className="px-2.5 py-2 bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-xs font-semibold text-emerald-950 dark:text-slate-100 focus:outline-none"
            >
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-emerald-200 dark:border-slate-800 text-[10px] text-emerald-800 dark:text-slate-400 uppercase tracking-wider">
              <th className="pb-3 pr-4">Judul &amp; Informasi</th>
              <th className="pb-3 pr-4">Kategori</th>
              <th className="pb-3 pr-4">Spesialisasi</th>
              <th className="pb-3 pr-4">Kata Kunci AI</th>
              <th className="pb-3 pr-4">Kode Medis</th>
              <th className="pb-3 pr-4 text-center">Chunks</th>
              <th className="pb-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-emerald-100 dark:divide-slate-800">
            {paginatedItems.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-xs text-emerald-600 dark:text-slate-400">
                  <span className="text-2xl block mb-2">🔍</span>
                  {items.length === 0
                    ? 'Belum ada pengetahuan yang diindeks ke Qdrant'
                    : 'Tidak ada dokumen yang cocok dengan filter pencarian.'}
                </td>
              </tr>
            ) : (
              paginatedItems.map((item) => {
                const colorClass = categoryColors[item.category] || categoryColors.document;
                const code = item.icd10_code || item.rxnorm_code || item.loinc_code || '—';
                const keywords = item.keywords || [];

                return (
                  <tr key={item.id} className="group hover:bg-emerald-50/40 dark:hover:bg-slate-800/40 transition-colors">
                    {/* Title */}
                    <td className="py-3.5 pr-4">
                      <button
                        type="button"
                        onClick={() => setViewingItem(item)}
                        className="text-left font-bold text-xs text-emerald-950 dark:text-slate-100 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors line-clamp-1"
                      >
                        {item.title}
                      </button>
                      {item.evidence_level && (
                        <div className="text-[10px] text-emerald-700 dark:text-slate-400 mt-0.5 truncate max-w-xs">
                          {item.evidence_level}
                        </div>
                      )}
                    </td>

                    {/* Category */}
                    <td className="py-3.5 pr-4">
                      <span className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${colorClass}`}>
                        {categoryLabels[item.category] || item.category.toUpperCase()}
                      </span>
                    </td>

                    {/* Specialty */}
                    <td className="py-3.5 pr-4 text-xs text-emerald-800 dark:text-slate-300">
                      {item.specialty || 'General'}
                    </td>

                    {/* Keywords Preview */}
                    <td className="py-3.5 pr-4">
                      {keywords.length > 0 ? (
                        <div className="flex flex-wrap gap-1 max-w-[200px]">
                          {keywords.slice(0, 2).map((k, i) => (
                            <span
                              key={i}
                              className="px-1.5 py-0.5 rounded-md text-[9px] font-semibold bg-teal-50 dark:bg-teal-950/50 text-teal-800 dark:text-teal-300 border border-teal-200/60 dark:border-teal-800 truncate max-w-[90px]"
                            >
                              {k}
                            </span>
                          ))}
                          {keywords.length > 2 && (
                            <span
                              onClick={() => setViewingItem(item)}
                              className="px-1.5 py-0.5 rounded-md text-[9px] font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 cursor-pointer hover:bg-slate-200"
                              title={keywords.slice(2).join(', ')}
                            >
                              +{keywords.length - 2}
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-[10px] text-slate-400 italic">—</span>
                      )}
                    </td>

                    {/* Code */}
                    <td className="py-3.5 pr-4 text-xs font-mono font-bold text-emerald-800 dark:text-slate-300">
                      {code}
                    </td>

                    {/* Chunks */}
                    <td className="py-3.5 pr-4 text-center">
                      <span className="inline-flex items-center justify-center px-2 py-0.5 rounded-lg text-xs font-mono font-bold bg-emerald-100/70 dark:bg-slate-800 text-emerald-800 dark:text-emerald-300">
                        {item.chunks_count}
                      </span>
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 text-right">
                      <div className="inline-flex items-center gap-1.5 justify-end">
                        <button
                          type="button"
                          onClick={() => setViewingItem(item)}
                          title="Lihat Detail & Kata Kunci"
                          className="px-2 py-1 bg-emerald-50 hover:bg-emerald-100 dark:bg-slate-800 dark:hover:bg-slate-700 text-emerald-800 dark:text-emerald-300 text-[10px] font-semibold rounded-lg border border-emerald-200 dark:border-slate-700 transition-colors"
                        >
                          Detail
                        </button>
                        <button
                          type="button"
                          onClick={() => setDeleteConfirmItem(item)}
                          title="Hapus Dokumen"
                          className="p-1 text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/40 rounded-lg transition-colors text-xs"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      {totalPages > 1 && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-5 mt-4 border-t border-emerald-100 dark:border-slate-800">
          {/* Item count status */}
          <div className="text-xs text-emerald-700 dark:text-slate-400 font-medium">
            Menampilkan <strong className="text-emerald-950 dark:text-slate-100">{startIndexDisplay}</strong> –{' '}
            <strong className="text-emerald-950 dark:text-slate-100">{endIndexDisplay}</strong> dari{' '}
            <strong className="text-emerald-950 dark:text-slate-100">{totalItems}</strong> dokumen
          </div>

          {/* Page controls */}
          <div className="flex items-center gap-1.5 flex-wrap">
            {/* Prev Button */}
            <button
              type="button"
              disabled={safePage <= 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              className="px-3 py-1.5 rounded-xl text-xs font-semibold text-emerald-800 dark:text-emerald-300 bg-emerald-100/70 dark:bg-slate-800 hover:bg-emerald-200/80 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              ← Sebelumnya
            </button>

            {/* Numbered Buttons */}
            <div className="flex items-center gap-1">
              {pageNumbers.map((page, idx) => {
                if (typeof page === 'string') {
                  return (
                    <span key={`ellipsis-${idx}`} className="px-1 text-xs text-slate-400">
                      …
                    </span>
                  );
                }
                const isActive = page === safePage;
                return (
                  <button
                    key={page}
                    type="button"
                    onClick={() => setCurrentPage(page)}
                    className={`w-8 h-8 rounded-xl text-xs font-bold transition-all ${isActive
                        ? 'bg-emerald-600 text-white shadow-sm'
                        : 'text-emerald-800 dark:text-slate-300 hover:bg-emerald-100 dark:hover:bg-slate-800'
                      }`}
                  >
                    {page}
                  </button>
                );
              })}
            </div>

            {/* Next Button */}
            <button
              type="button"
              disabled={safePage >= totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              className="px-3 py-1.5 rounded-xl text-xs font-semibold text-emerald-800 dark:text-emerald-300 bg-emerald-100/70 dark:bg-slate-800 hover:bg-emerald-200/80 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Selanjutnya →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
