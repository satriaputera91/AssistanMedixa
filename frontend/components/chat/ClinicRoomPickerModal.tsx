'use client';

import { useState, useEffect } from 'react';
import type { ClinicRoom } from '@/services/agent.service';

interface ClinicRoomPickerModalProps {
  isOpen: boolean;
  rooms: ClinicRoom[];
  selectedRoomId?: string;
  onSelect: (room: ClinicRoom) => void;
  onClose?: () => void;
  /** When true, the modal has no close button (first-time forced selection) */
  required?: boolean;
}

const SPECIALTY_ICONS: Record<string, string> = {
  'Internal Medicine': '🩺',
  'Cardiology': '❤️',
  'Neurology': '🧠',
  'General Surgery': '🔪',
  'Pediatrics': '👶',
  'Gastroenterology': '🫁',
  'Dermatology': '🧴',
  'Ophthalmology': '👁️',
};

export default function ClinicRoomPickerModal({
  isOpen,
  rooms,
  selectedRoomId,
  onSelect,
  onClose,
  required = false,
}: ClinicRoomPickerModalProps) {
  const ITEMS_PER_PAGE = 4;
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    if (isOpen) {
      setSearchQuery('');
      setCurrentPage(1);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const filteredRooms = rooms.filter((r) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      r.room_name.toLowerCase().includes(q) ||
      r.room_code.toLowerCase().includes(q) ||
      r.specialty.toLowerCase().includes(q) ||
      r.building.toLowerCase().includes(q)
    );
  });

  const totalPages = Math.max(1, Math.ceil(filteredRooms.length / ITEMS_PER_PAGE));
  const safePage = Math.min(currentPage, totalPages);
  const paginatedRooms = filteredRooms.slice(
    (safePage - 1) * ITEMS_PER_PAGE,
    safePage * ITEMS_PER_PAGE,
  );

  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
    setCurrentPage(1);
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white dark:bg-slate-900 border border-emerald-500/30 rounded-3xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col overflow-hidden transition-all animate-in zoom-in-95 duration-200">

        {/* Header */}
        <div className="px-6 py-5 border-b border-emerald-100 dark:border-slate-800 bg-gradient-to-r from-emerald-50 via-teal-50 to-emerald-50/50 dark:from-slate-900 dark:via-slate-850 dark:to-slate-900">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-600 text-white flex items-center justify-center text-xl font-bold shadow-lg shadow-emerald-600/20">
                🏥
              </div>
              <div>
                <h3 className="text-base font-bold text-emerald-950 dark:text-slate-100">
                  Pilih Ruangan Poli Aktif
                </h3>
                <p className="text-xs text-emerald-700 dark:text-slate-400 mt-0.5">
                  Tentukan ruangan poliklinik tempat Anda bertugas hari ini
                </p>
              </div>
            </div>
            {!required && onClose && (
              <button
                type="button"
                onClick={onClose}
                className="w-8 h-8 rounded-xl flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                ✕
              </button>
            )}
          </div>

          {/* Search */}
          <div className="mt-3">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearchChange(e.target.value)}
              placeholder="Cari ruangan poli, kode, atau spesialisasi..."
              className="w-full px-4 py-2.5 bg-white dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-sm text-emerald-950 dark:text-slate-100 placeholder-emerald-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 transition-all"
              autoFocus
            />
          </div>
        </div>

        {/* Room Grid */}
        <div className="flex-1 overflow-y-auto p-4">
          {filteredRooms.length === 0 ? (
            <div className="text-center py-8 text-emerald-600 dark:text-slate-400 text-xs">
              <span className="text-2xl block mb-2">🔍</span>
              Tidak ditemukan ruangan untuk &quot;{searchQuery}&quot;
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {paginatedRooms.map((room) => {
                const isSelected = room.room_id === selectedRoomId;
                const isHovered = room.room_id === hoveredId;
                const icon = SPECIALTY_ICONS[room.specialty] || '🏥';

                return (
                  <button
                    key={room.room_id}
                    type="button"
                    onClick={() => onSelect(room)}
                    onMouseEnter={() => setHoveredId(room.room_id)}
                    onMouseLeave={() => setHoveredId(null)}
                    className={`relative text-left rounded-2xl p-4 border-2 transition-all duration-150 group ${
                      isSelected
                        ? 'border-emerald-500 bg-emerald-50/80 dark:bg-emerald-950/40 shadow-md shadow-emerald-500/10'
                        : isHovered
                        ? 'border-emerald-300 dark:border-emerald-600/50 bg-emerald-50/40 dark:bg-slate-800/80 shadow-sm'
                        : 'border-emerald-100 dark:border-slate-800 bg-white dark:bg-slate-900 hover:shadow-sm'
                    }`}
                  >
                    {/* Selected check */}
                    {isSelected && (
                      <div className="absolute top-3 right-3 w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs font-bold shadow-sm">
                        ✓
                      </div>
                    )}

                    <div className="flex items-start gap-3">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-lg shrink-0 transition-colors ${
                        isSelected
                          ? 'bg-emerald-600 text-white shadow-sm'
                          : 'bg-emerald-100 dark:bg-slate-800 text-emerald-700 dark:text-emerald-400'
                      }`}>
                        {icon}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className={`text-sm font-bold truncate transition-colors ${
                          isSelected ? 'text-emerald-900 dark:text-emerald-300' : 'text-emerald-950 dark:text-slate-100'
                        }`}>
                          {room.room_name}
                        </div>
                        <div className="text-[11px] text-emerald-700 dark:text-slate-400 mt-0.5 font-medium">
                          {room.room_code} • {room.floor} • {room.building}
                        </div>
                        <div className="mt-1.5 inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-emerald-100/60 dark:bg-slate-800 text-[10px] font-semibold text-emerald-800 dark:text-emerald-400 border border-emerald-200/60 dark:border-slate-700">
                          {room.specialty}
                        </div>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="px-6 py-2.5 border-t border-emerald-100 dark:border-slate-800 flex items-center justify-between">
            <button
              type="button"
              disabled={safePage <= 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              className="px-3 py-1.5 rounded-xl text-xs font-semibold text-emerald-800 dark:text-emerald-300 bg-emerald-100 dark:bg-slate-800 hover:bg-emerald-200 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              ← Sebelumnya
            </button>

            <div className="flex items-center gap-1">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                <button
                  key={page}
                  type="button"
                  onClick={() => setCurrentPage(page)}
                  className={`w-8 h-8 rounded-xl text-xs font-bold transition-all ${
                    page === safePage
                      ? 'bg-emerald-600 text-white shadow-sm'
                      : 'text-emerald-700 dark:text-slate-400 hover:bg-emerald-100 dark:hover:bg-slate-800'
                  }`}
                >
                  {page}
                </button>
              ))}
            </div>

            <button
              type="button"
              disabled={safePage >= totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              className="px-3 py-1.5 rounded-xl text-xs font-semibold text-emerald-800 dark:text-emerald-300 bg-emerald-100 dark:bg-slate-800 hover:bg-emerald-200 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Selanjutnya →
            </button>
          </div>
        )}

        {/* Footer hint */}
        <div className="px-6 py-3 border-t border-emerald-100 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-900/50">
          <p className="text-[10px] text-emerald-600 dark:text-slate-400 text-center">
            {required
              ? '⚠️ Anda harus memilih ruangan poli sebelum memulai konsultasi klinis.'
              : 'Pilih ruangan poli yang berbeda untuk mengubah lokasi kerja Anda.'}
          </p>
        </div>
      </div>
    </div>
  );
}
