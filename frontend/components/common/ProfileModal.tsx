'use client';

import { useState, useEffect } from 'react';
import { AuthService, type UserInfo } from '@/services/auth.service';
import { useTheme } from '@/hooks/useTheme';

interface ProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLogout: () => void;
}

export default function ProfileModal({ isOpen, onClose, onLogout }: ProfileModalProps) {
  const [profile, setProfile] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { theme, isDark, toggleTheme } = useTheme();

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      setError('');
      AuthService.getMe()
        .then((data) => {
          setProfile(data);
        })
        .catch((err) => {
          setError(err.message || 'Gagal memuat profil');
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const getInitials = (name?: string) => {
    if (!name) return 'DR';
    return name
      .split(' ')
      .filter((n) => !n.startsWith('dr.') && !n.startsWith('Dr.') && !n.includes(','))
      .map((n) => n[0])
      .join('')
      .substring(0, 2)
      .toUpperCase() || 'DR';
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-in fade-in duration-150">
      <div className="w-full max-w-md bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 rounded-3xl shadow-2xl overflow-hidden relative">
        {/* Top Banner */}
        <div className="h-24 bg-gradient-to-r from-emerald-600 to-teal-700 p-4 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="text-white/80 hover:text-white bg-black/20 hover:bg-black/40 rounded-full w-8 h-8 flex items-center justify-center transition-colors text-sm font-bold"
          >
            ✕
          </button>
        </div>

        {/* Profile Card Header with Avatar */}
        <div className="px-6 pb-6 relative">
          <div className="-mt-12 mb-4 flex justify-between items-end">
            <div className="w-20 h-20 rounded-2xl bg-white dark:bg-slate-800 border-4 border-white dark:border-slate-900 shadow-xl flex items-center justify-center text-2xl font-black text-emerald-700 dark:text-emerald-400">
              {profile?.name ? getInitials(profile.name) : '🩺'}
            </div>
            <div className="flex gap-2">
              <span
                className={`px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider border ${
                  profile?.role === 'admin'
                    ? 'bg-purple-50 dark:bg-purple-950/50 border-purple-200 dark:border-purple-800 text-purple-700 dark:text-purple-300'
                    : 'bg-emerald-50 dark:bg-emerald-950/50 border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300'
                }`}
              >
                {profile?.role === 'admin' ? '🛡️ Administrator' : '🩺 Dokter Spesialis'}
              </span>
            </div>
          </div>

          {loading ? (
            <div className="py-8 text-center text-emerald-700 dark:text-emerald-400 text-xs">
              <div className="text-2xl mb-2 animate-bounce">🩺</div>
              Memuat profil akun...
            </div>
          ) : error ? (
            <div className="p-3 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-300 text-xs text-center">
              {error}
            </div>
          ) : profile ? (
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-bold text-emerald-950 dark:text-white">
                  {profile.name}
                </h3>
                <p className="text-xs text-emerald-700 dark:text-slate-400">{profile.email}</p>
              </div>

              {/* Detail Fields */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 p-3.5 bg-emerald-50/60 dark:bg-slate-800/60 border border-emerald-200/80 dark:border-slate-800 rounded-2xl text-xs">
                <div>
                  <span className="text-[10px] uppercase font-bold text-emerald-700 dark:text-slate-400 block mb-0.5">
                    Spesialisasi Klinis
                  </span>
                  <span className="font-semibold text-emerald-950 dark:text-slate-200">
                    {profile.specialty || 'Kedokteran Umum'}
                  </span>
                </div>

                <div>
                  <span className="text-[10px] uppercase font-bold text-emerald-700 dark:text-slate-400 block mb-0.5">
                    Nomor STR / SIP
                  </span>
                  <span className="font-mono font-medium text-emerald-900 dark:text-slate-200">
                    {profile.license_no || 'MD-SIMRS-ACTIVE'}
                  </span>
                </div>

                <div>
                  <span className="text-[10px] uppercase font-bold text-emerald-700 dark:text-slate-400 block mb-0.5">
                    Status Akun
                  </span>
                  <span className="inline-flex items-center gap-1 font-semibold text-emerald-700 dark:text-emerald-400">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    {profile.is_active ? 'Aktif & Terverifikasi' : 'Nonaktif'}
                  </span>
                </div>

                <div>
                  <span className="text-[10px] uppercase font-bold text-emerald-700 dark:text-slate-400 block mb-0.5">
                    ID Dokter (EHR/MCP)
                  </span>
                  <span className="font-mono font-medium text-emerald-900 dark:text-slate-200">
                    {profile.id}
                  </span>
                </div>
              </div>

              {/* Theme Toggle Section */}
              <div className="flex items-center justify-between p-3.5 bg-emerald-50/40 dark:bg-slate-800/40 border border-emerald-200/60 dark:border-slate-800 rounded-2xl">
                <div className="flex items-center gap-2.5">
                  <span className="text-lg">{isDark ? '🌙' : '☀️'}</span>
                  <div>
                    <div className="text-xs font-bold text-emerald-950 dark:text-white">
                      Tema Tampilan
                    </div>
                    <div className="text-[10px] text-emerald-700 dark:text-slate-400">
                      {isDark ? 'Mode Malam (Night / Dark)' : 'Mode Terang (Light)'}
                    </div>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={toggleTheme}
                  className="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-white dark:bg-slate-700 text-emerald-900 dark:text-slate-100 border border-emerald-300 dark:border-slate-600 shadow-sm hover:bg-emerald-50 dark:hover:bg-slate-600 transition-all flex items-center gap-1.5"
                >
                  <span>{isDark ? '☀️ Ubah ke Terang' : '🌙 Ubah ke Gelap'}</span>
                </button>
              </div>

              {/* Action Buttons */}
              <div className="pt-2 flex gap-2.5">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 py-2.5 rounded-xl border border-emerald-200 dark:border-slate-700 text-emerald-900 dark:text-slate-300 text-xs font-semibold hover:bg-emerald-50 dark:hover:bg-slate-800 transition-colors"
                >
                  Tutup
                </button>
                <button
                  type="button"
                  onClick={onLogout}
                  className="py-2.5 px-5 rounded-xl bg-red-600 hover:bg-red-500 text-white text-xs font-bold shadow-md transition-all flex items-center gap-1.5"
                >
                  <span>🚪</span>
                  <span>Keluar</span>
                </button>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
