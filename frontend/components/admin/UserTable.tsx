'use client';
import type { UserAdminView } from '@/services/admin.service';

interface UserTableProps {
  users: UserAdminView[];
  onToggleStatus: (userId: string) => void;
  onOpenCreateModal?: () => void;
}

export default function UserTable({ users, onToggleStatus, onOpenCreateModal }: UserTableProps) {
  return (
    <div className="bg-white border border-emerald-200 rounded-2xl p-6 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-bold text-emerald-950">Akun Pengguna &amp; Dokter</h2>
          <p className="text-xs text-emerald-700 mt-0.5">Kelola status aktif dan hak akses staf medis.</p>
        </div>
        {onOpenCreateModal && (
          <button
            type="button"
            onClick={onOpenCreateModal}
            className="py-2 px-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow-sm transition-all flex items-center gap-1.5"
          >
            <span>➕</span>
            <span>Tambah Pengguna</span>
          </button>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-emerald-200 text-[10px] text-emerald-700 uppercase tracking-wider">
              <th className="pb-3 pr-4">Nama</th>
              <th className="pb-3 pr-4">Email</th>
              <th className="pb-3 pr-4">Peran</th>
              <th className="pb-3 pr-4">Spesialisasi / Lisensi</th>
              <th className="pb-3 pr-4">Status</th>
              <th className="pb-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-emerald-200/50">
            {users.map((u) => (
              <tr key={u.id} className="group hover:bg-emerald-100/30 transition-colors">
                <td className="py-3 pr-4 font-semibold text-xs text-emerald-900">{u.name}</td>
                <td className="py-3 pr-4 text-xs text-emerald-700">{u.email}</td>
                <td className="py-3 pr-4">
                  <span
                    className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                      u.role === 'admin'
                        ? 'bg-emerald-500/15 text-emerald-700 border-emerald-500/20'
                        : 'bg-emerald-500/15 text-emerald-700 border-emerald-500/20'
                    }`}
                  >
                    {u.role === 'admin' ? 'ADMIN' : 'DOKTER'}
                  </span>
                </td>
                <td className="py-3 pr-4 text-xs text-emerald-700">
                  {u.specialty || '—'} {u.license_no ? `(${u.license_no})` : ''}
                </td>
                <td className="py-3 pr-4">
                  <span
                    className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                      u.is_active
                        ? 'bg-emerald-500/15 text-emerald-700 border-emerald-500/20'
                        : 'bg-red-500/15 text-red-400 border-red-500/20'
                    }`}
                  >
                    {u.is_active ? 'Aktif' : 'Nonaktif'}
                  </span>
                </td>
                <td className="py-3 text-right">
                  <button
                    onClick={() => onToggleStatus(u.id)}
                    className="px-3 py-1 bg-emerald-100 hover:bg-emerald-200 text-[10px] text-emerald-900 rounded border border-emerald-300 transition-colors"
                  >
                    {u.is_active ? 'Nonaktifkan' : 'Aktifkan'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
