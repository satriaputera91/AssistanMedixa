'use client';
import { useState } from 'react';
import Link from 'next/link';
import { useTheme } from '@/hooks/useTheme';
import ProfileModal from './ProfileModal';

interface NavbarProps {
  userName: string;
  userRole: string;
  onLogout: () => void;
  activePage?: 'doctor' | 'knowledge' | 'admin';
}

export default function Navbar({ userName, userRole, onLogout, activePage }: NavbarProps) {
  const [profileOpen, setProfileOpen] = useState(false);
  const { isDark, toggleTheme } = useTheme();

  const effectiveRole = userRole || (typeof window !== 'undefined' ? localStorage.getItem('user_role') || 'doctor' : 'doctor');
  const roleLabel = effectiveRole === 'doctor' ? 'Dokter' : 'Admin';

  const navItems = [
    { key: 'knowledge', href: '/knowledge', label: '📚 Basis Pengetahuan', roles: ['admin'] },
    { key: 'admin', href: '/admin', label: '⚙️ Dasbor Admin', roles: ['admin'] },
  ];

  return (
    <>
      <ProfileModal
        isOpen={profileOpen}
        onClose={() => setProfileOpen(false)}
        onLogout={onLogout}
      />

      <header className="h-16 bg-white dark:bg-slate-900 border-b border-emerald-200 dark:border-slate-800 px-4 sm:px-6 flex items-center justify-between shrink-0 shadow-sm z-20 transition-colors">
        {/* Logo & Title */}
        <Link href={effectiveRole === 'admin' ? '/admin' : '/doctor'} className="flex items-center gap-2.5 sm:gap-3 group">
          <span className="text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-700 via-emerald-600 to-emerald-800 dark:from-emerald-400 dark:via-teal-300 dark:to-emerald-500 tracking-tight group-hover:opacity-90 transition-opacity">
            🏥 AssistantMedixa
          </span>
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] font-semibold text-emerald-800 dark:text-emerald-300">SIMRS / Satu Sehat</span>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="flex items-center gap-1.5">
          {navItems
            .filter(item => item.roles.includes(effectiveRole))
            .map(item => (
              <Link
                key={item.key}
                href={item.href}
                className={`px-3 sm:px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${activePage === item.key
                  ? 'bg-emerald-600 dark:bg-emerald-500 text-white shadow-sm'
                  : 'text-emerald-800 dark:text-slate-300 hover:text-emerald-950 dark:hover:text-white hover:bg-emerald-100/70 dark:hover:bg-slate-800'
                  }`}
              >
                {item.label}
              </Link>
            ))}
        </nav>

        {/* Theme Switcher, Profile Button & Logout */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Theme Toggle Button */}
          <button
            type="button"
            onClick={toggleTheme}
            title={isDark ? 'Beralih ke mode terang (Light)' : 'Beralih ke mode malam (Dark)'}
            className="w-9 h-9 rounded-xl flex items-center justify-center bg-emerald-50 dark:bg-slate-800 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-slate-700 hover:bg-emerald-100 dark:hover:bg-slate-700 transition-all text-sm shadow-sm"
          >
            {isDark ? '☀️' : '🌙'}
          </button>

          {/* User Profile Button */}
          <button
            type="button"
            onClick={() => setProfileOpen(true)}
            className="flex items-center gap-2 px-2.5 py-1 rounded-xl bg-emerald-50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 hover:bg-emerald-100 dark:hover:bg-slate-700 transition-all group"
          >
            <div className="w-6 h-6 rounded-lg bg-emerald-600 text-white flex items-center justify-center text-xs font-bold shadow-xs">
              {userName ? userName.charAt(0).toUpperCase() : '👨‍⚕️'}
            </div>
            <div className="text-left hidden md:block">
              <div className="text-xs font-bold text-emerald-950 dark:text-slate-100 leading-tight">
                {userName || 'Pengguna'}
              </div>
              <div className="text-[9px] font-semibold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider">
                {roleLabel} • Lihat Profil
              </div>
            </div>
          </button>

          {/* Logout Button */}
          <button
            type="button"
            onClick={onLogout}
            className="px-3 py-1.5 text-xs font-semibold text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-950/40 border border-red-200 dark:border-red-900/50 rounded-xl transition-colors"
          >
            Keluar
          </button>
        </div>
      </header>
    </>
  );
}
