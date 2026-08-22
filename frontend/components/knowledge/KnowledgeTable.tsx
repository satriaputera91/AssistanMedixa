'use client';
import { useState } from 'react';
import type { KnowledgeItem } from '@/services/rag.service';

interface KnowledgeTableProps {
  items: KnowledgeItem[];
  onDelete: (itemId: string) => void;
}

const categoryColors: Record<string, string> = {
  disease: 'bg-emerald-500/15 text-emerald-700 border-emerald-500/20',
  medicine: 'bg-emerald-500/15 text-emerald-700 border-emerald-500/20',
  terminology: 'bg-emerald-500/15 text-emerald-700 border-emerald-500/20',
  guideline: 'bg-amber-500/15 text-amber-600 border-amber-500/20',
  document: 'bg-emerald-100 text-emerald-800 border-emerald-200',
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

  const filteredItems = items.filter((item) => {
    const matchesSearch =
      item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.specialty && item.specialty.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (item.icd10_code && item.icd10_code.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (item.rxnorm_code && item.rxnorm_code.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesCategory =
      selectedCategory === 'all' || item.category.toLowerCase() === selectedCategory.toLowerCase();

    return matchesSearch && matchesCategory;
  });

  return (
    <div className="bg-white border border-emerald-200 rounded-2xl p-6 shadow-lg">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div>
          <h2 className="text-lg font-bold text-emerald-950">Vektor Pengetahuan Qdrant Terindeks</h2>
          <p className="text-xs text-emerald-700 mt-0.5">
            Total {items.length} dokumen panduan dan literatur klinis.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Cari judul / ICD / RxNorm..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="px-3 py-1.5 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-950 placeholder-emerald-400 focus:outline-none focus:border-emerald-500"
          />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-1.5 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-900 focus:outline-none focus:border-emerald-500"
          >
            <option value="all">Semua Kategori</option>
            <option value="disease">Penyakit</option>
            <option value="medicine">Obat</option>
            <option value="terminology">Terminologi</option>
            <option value="guideline">Panduan</option>
            <option value="document">Dokumen</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-emerald-200 text-[10px] text-emerald-700 uppercase tracking-wider">
              <th className="pb-3 pr-4">Judul &amp; Bukti</th>
              <th className="pb-3 pr-4">Kategori</th>
              <th className="pb-3 pr-4">Spesialisasi</th>
              <th className="pb-3 pr-4">Kode Medis</th>
              <th className="pb-3 pr-4">Vektor Chunks</th>
              <th className="pb-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-emerald-200/50">
            {filteredItems.length === 0 && (
              <tr>
                <td colSpan={6} className="py-8 text-center text-xs text-emerald-600">
                  {items.length === 0
                    ? 'Belum ada pengetahuan yang diindeks ke Qdrant'
                    : 'Tidak ada dokumen yang cocok dengan pencarian'}
                </td>
              </tr>
            )}
            {filteredItems.map((item) => {
              const colorClass = categoryColors[item.category] || categoryColors.document;
              const code = item.icd10_code || item.rxnorm_code || item.loinc_code || '—';
              return (
                <tr key={item.id} className="group hover:bg-emerald-50/50 transition-colors">
                  <td className="py-3 pr-4">
                    <div className="font-semibold text-emerald-900 text-xs">{item.title}</div>
                    {item.evidence_level && (
                      <div className="text-[10px] text-emerald-600 mt-0.5 truncate max-w-xs">
                        {item.evidence_level}
                      </div>
                    )}
                  </td>
                  <td className="py-3 pr-4">
                    <span className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold border ${colorClass}`}>
                      {categoryLabels[item.category] || item.category.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-xs text-emerald-700">{item.specialty}</td>
                  <td className="py-3 pr-4 text-xs font-mono text-emerald-700">{code}</td>
                  <td className="py-3 pr-4">
                    <span className="text-xs font-mono text-emerald-700 font-semibold">{item.chunks_count}</span>
                  </td>
                  <td className="py-3 text-right">
                    <button
                      type="button"
                      onClick={() => {
                        if (confirm(`Hapus "${item.title}" dari koleksi vektor Qdrant?`)) onDelete(item.id);
                      }}
                      className="px-2.5 py-1 bg-red-50 hover:bg-red-100 text-[10px] text-red-600 font-medium rounded-lg border border-red-200 transition-colors"
                    >
                      Hapus
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

