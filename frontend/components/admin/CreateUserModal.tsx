'use client';

import { useState } from 'react';
import type { CreateUserInput } from '@/services/admin.service';

interface CreateUserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (input: CreateUserInput) => Promise<boolean>;
  submitting: boolean;
}

export default function CreateUserModal({
  isOpen,
  onClose,
  onSubmit,
  submitting,
}: CreateUserModalProps) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<'doctor' | 'admin'>('doctor');
  const [specialty, setSpecialty] = useState('Kedokteran Umum');
  const [licenseNo, setLicenseNo] = useState('');
  const [formError, setFormError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');

    if (!name || !email || !password) {
      setFormError('Nama, email, dan kata sandi wajib diisi.');
      return;
    }

    const ok = await onSubmit({
      name,
      email,
      password,
      role,
      specialty: role === 'doctor' ? specialty : undefined,
      license_no: role === 'doctor' ? licenseNo : undefined,
    });

    if (ok) {
      setName('');
      setEmail('');
      setPassword('');
      setLicenseNo('');
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4 animate-in fade-in duration-150">
      <div className="w-full max-w-md bg-white rounded-2xl border border-emerald-200 shadow-2xl p-6 relative">
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 text-emerald-700 hover:text-emerald-950 text-sm font-bold w-7 h-7 rounded-full bg-emerald-50 flex items-center justify-center"
        >
          ✕
        </button>

        <div className="mb-5">
          <h3 className="text-lg font-bold text-emerald-950">Tambah Akun Pengguna Baru</h3>
          <p className="text-xs text-emerald-700 mt-0.5">
            Daftarkan akun dokter atau administrator AIMedical.
          </p>
        </div>

        {formError && (
          <div className="mb-4 p-2.5 bg-red-50 border border-red-200 rounded-lg text-red-700 text-xs">
            {formError}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5">
          <div>
            <label className="block text-[11px] font-semibold text-emerald-800 mb-1">Nama Lengkap</label>
            <input
              type="text"
              required
              placeholder="dr. Budi Santoso, Sp.PD"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-950 placeholder-emerald-400 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-emerald-800 mb-1">Email</label>
            <input
              type="email"
              required
              placeholder="budi.santoso@aimedical.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-950 placeholder-emerald-400 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-emerald-800 mb-1">Kata Sandi</label>
            <input
              type="password"
              required
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-950 placeholder-emerald-400 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-emerald-800 mb-1">Peran</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value as 'doctor' | 'admin')}
                className="w-full px-3 py-2 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-950 focus:outline-none focus:border-emerald-500"
              >
                <option value="doctor">Dokter</option>
                <option value="admin">Admin</option>
              </select>
            </div>

            {role === 'doctor' && (
              <div>
                <label className="block text-[11px] font-semibold text-emerald-800 mb-1">Spesialisasi</label>
                <input
                  type="text"
                  placeholder="Spesialis Penyakit Dalam"
                  value={specialty}
                  onChange={(e) => setSpecialty(e.target.value)}
                  className="w-full px-3 py-2 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-950 placeholder-emerald-400 focus:outline-none focus:border-emerald-500"
                />
              </div>
            )}
          </div>

          {role === 'doctor' && (
            <div>
              <label className="block text-[11px] font-semibold text-emerald-800 mb-1">Nomor STR / SIP</label>
              <input
                type="text"
                placeholder="STR-3171-8899-2024"
                value={licenseNo}
                onChange={(e) => setLicenseNo(e.target.value)}
                className="w-full px-3 py-2 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-950 placeholder-emerald-400 focus:outline-none focus:border-emerald-500"
              />
            </div>
          )}

          <div className="flex gap-2.5 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 bg-emerald-100 hover:bg-emerald-200 text-emerald-900 font-semibold rounded-xl text-xs border border-emerald-300 transition-colors"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold rounded-xl text-xs transition-all shadow-md"
            >
              {submitting ? 'Menyimpan…' : 'Buat Akun'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
