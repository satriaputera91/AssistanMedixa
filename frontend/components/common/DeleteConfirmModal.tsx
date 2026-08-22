'use client';

import React from 'react';

interface DeleteConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title?: string;
  itemName?: string;
  description?: string;
  confirmLabel?: string;
  loading?: boolean;
}

export default function DeleteConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title = 'Hapus Riwayat Konsultasi?',
  itemName,
  description = 'Riwayat percakapan klinis ini akan dihapus secara permanen dari basis data sistem dan tidak dapat dipulihkan kembali.',
  confirmLabel = 'Ya, Hapus Sekarang',
  loading = false,
}: DeleteConfirmModalProps) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/60 dark:bg-black/80 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-150"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 rounded-3xl p-6 sm:p-7 shadow-2xl space-y-5 animate-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Icon & Heading */}
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-2xl bg-red-100 dark:bg-red-950/60 text-red-600 dark:text-red-400 flex items-center justify-center text-2xl shrink-0 shadow-xs">
            🗑️
          </div>
          <div>
            <h3 className="text-base sm:text-lg font-bold text-emerald-950 dark:text-white">
              {title}
            </h3>
            {itemName && (
              <p className="text-xs font-semibold text-red-600 dark:text-red-400 mt-1 truncate max-w-xs">
                "{itemName}"
              </p>
            )}
          </div>
        </div>

        {/* Warning text */}
        <p className="text-xs text-emerald-800/80 dark:text-slate-400 leading-relaxed">
          {description}
        </p>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-2.5 pt-2">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2.5 rounded-xl border border-emerald-200 dark:border-slate-700 bg-emerald-50 dark:bg-slate-800 text-emerald-900 dark:text-slate-200 hover:bg-emerald-100 dark:hover:bg-slate-700 text-xs font-semibold transition-colors"
          >
            Batal
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={loading}
            className="px-5 py-2.5 rounded-xl bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white text-xs font-bold shadow-md hover:shadow-lg transition-all flex items-center gap-2 active:scale-95"
          >
            {loading ? (
              <>
                <span className="animate-spin text-xs">⏳</span>
                <span>Menghapus…</span>
              </>
            ) : (
              <>
                <span>🗑️</span>
                <span>{confirmLabel}</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
