'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { useAdmin } from '@/hooks/useAdmin';
import Navbar from '@/components/common/Navbar';
import MetricCard from '@/components/common/MetricCard';
import UserTable from '@/components/admin/UserTable';
import AuditFeed from '@/components/admin/AuditFeed';
import MonitoringCard from '@/components/admin/MonitoringCard';
import AnalyticsView from '@/components/admin/AnalyticsView';
import CreateUserModal from '@/components/admin/CreateUserModal';
import GuardrailsPanel from '@/components/admin/GuardrailsPanel';
import ClinicRoomManagement from '@/components/admin/ClinicRoomManagement';

type AdminMenuKey = 'overview' | 'users' | 'clinic_rooms' | 'guardrails' | 'monitoring' | 'analytics' | 'audit';

export default function AdminPage() {
  const { userName, userRole, loading, logout } = useAuth('admin');
  const {
    stats,
    users,
    auditLogs,
    analytics,
    monitoring,
    clinicRooms,
    error,
    creatingUser,
    savingClinicRoom,
    loadAdminData,
    toggleUserStatus,
    createUser,
    createClinicRoom,
    updateClinicRoom,
    deleteClinicRoom,
    toggleClinicRoomStatus,
  } = useAdmin();

  const [activeMenu, setActiveMenu] = useState<AdminMenuKey>('overview');
  const [createUserOpen, setCreateUserOpen] = useState(false);

  useEffect(() => {
    if (!loading) loadAdminData();
  }, [loading, loadAdminData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-emerald-50 text-emerald-700">
        <div className="text-center">
          <div className="text-3xl mb-3 animate-pulse">⚙️</div>
          <p className="text-sm">Memuat dasbor admin…</p>
        </div>
      </div>
    );
  }

  const menuItems = [
    { key: 'overview' as AdminMenuKey, label: 'Ikhtisar & Metrik', icon: '📊', desc: 'Ringkasan sistem & LLM' },
    { key: 'users' as AdminMenuKey, label: 'Manajemen Pengguna', icon: '👥', desc: `${users.length} akun dokter` },
    { key: 'clinic_rooms' as AdminMenuKey, label: 'Manajemen Ruang Poli', icon: '🏥', desc: `${clinicRooms.length} ruangan poli` },
    { key: 'guardrails' as AdminMenuKey, label: 'AI Safety & Guardrails', icon: '🛡️', desc: 'Kebijakan & sensor PII' },
    { key: 'monitoring' as AdminMenuKey, label: 'Monitoring Sistem', icon: '🖥️', desc: 'SIMRS, Gemini, Qdrant' },
    { key: 'analytics' as AdminMenuKey, label: 'Analitik & Token', icon: '📈', desc: 'Metrik penggunaan & latensi' },
    { key: 'audit' as AdminMenuKey, label: 'Audit Trail & Log', icon: '📋', desc: 'Rekam jejak aktivitas' },
  ];


  return (
    <div className="flex flex-col h-screen bg-emerald-50 dark:bg-slate-950 text-emerald-950 dark:text-slate-100 overflow-hidden transition-colors">
      <Navbar userName={userName} userRole={userRole} onLogout={logout} activePage="admin" />

      {/* Modal Tambah Pengguna */}
      <CreateUserModal
        isOpen={createUserOpen}
        onClose={() => setCreateUserOpen(false)}
        onSubmit={createUser}
        submitting={creatingUser}
      />

      <div className="flex flex-1 min-h-0">
        {/* Left Side Menu */}
        <aside className="w-72 bg-white dark:bg-slate-900 border-r border-emerald-200 dark:border-slate-800 flex flex-col shrink-0 transition-colors">
          {/* Sidebar Header */}
          <div className="p-4 border-b border-emerald-200 dark:border-slate-800">
            <div className="flex items-center justify-between gap-2 mb-3">
              <div className="flex items-center gap-2">
                <span className="text-lg">⚙️</span>
                <div>
                  <h2 className="font-bold text-emerald-950 dark:text-white text-xs">Menu Administrasi</h2>
                  <p className="text-[10px] text-emerald-700 dark:text-slate-400">Kontrol & Keamanan Sistem</p>
                </div>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setCreateUserOpen(true)}
              className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold shadow-sm transition-all active:scale-[0.98]"
            >
              <span>👤+</span>
              <span>+ Tambah Akun Dokter</span>
            </button>
          </div>

          {/* Navigation Menu List */}
          <nav className="flex-1 overflow-y-auto p-3 space-y-1">
            <div className="text-[10px] font-semibold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider px-2 py-1 mb-1">
              Navigasi Admin
            </div>

            {menuItems.map((item) => {
              const isActive = activeMenu === item.key;
              return (
                <button
                  key={item.key}
                  type="button"
                  onClick={() => setActiveMenu(item.key)}
                  className={`w-full text-left px-3 py-2.5 rounded-xl text-xs transition-all flex items-center gap-3 ${
                    isActive
                      ? 'bg-emerald-600/15 dark:bg-emerald-500/20 text-emerald-900 dark:text-emerald-300 border border-emerald-500/30 font-bold shadow-2xs'
                      : 'text-emerald-800 dark:text-slate-300 hover:bg-emerald-100/70 dark:hover:bg-slate-800'
                  }`}
                >
                  <span className="text-base shrink-0">{item.icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="truncate">{item.label}</div>
                    <div className="text-[10px] font-normal text-emerald-600 dark:text-slate-400 truncate">
                      {item.desc}
                    </div>
                  </div>
                  {isActive && <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />}
                </button>
              );
            })}

            <div className="pt-2 border-t border-emerald-100 dark:border-slate-800 my-2">
              <div className="text-[10px] font-semibold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider px-2 py-1 mb-1">
                Modul Eksternal
              </div>
              <Link
                href="/knowledge"
                className="w-full text-left px-3 py-2.5 rounded-xl text-xs text-emerald-800 dark:text-slate-300 hover:bg-emerald-100/70 dark:hover:bg-slate-800 transition-colors flex items-center gap-3"
              >
                <span className="text-base shrink-0">📚</span>
                <div className="flex-1 min-w-0">
                  <div className="font-semibold truncate">Basis Pengetahuan</div>
                  <div className="text-[10px] text-emerald-600 dark:text-slate-400 truncate">Qdrant Vector RAG</div>
                </div>
                <span className="text-[10px] text-emerald-500">↗</span>
              </Link>
            </div>
          </nav>

          {/* Sidebar Footer */}
          <div className="p-4 border-t border-emerald-200 dark:border-slate-800 bg-emerald-50/30 dark:bg-slate-900/50">
            <div className="text-[10px] text-emerald-600 dark:text-slate-400 flex items-center justify-between">
              <span>Masuk sebagai <strong className="text-emerald-900 dark:text-slate-200 font-semibold">{userName || 'Admin'}</strong></span>
              <span className="uppercase text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 dark:bg-slate-800 text-emerald-800 dark:text-emerald-400">ADMIN</span>
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 space-y-6">
          {error && (
            <div className="flex items-center justify-between gap-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 shadow-sm">
              <span>{error}</span>
              <button
                type="button"
                onClick={loadAdminData}
                className="shrink-0 font-semibold underline hover:text-red-900"
              >
                Coba lagi
              </button>
            </div>
          )}

          {/* Section: Overview (All dashboard items) */}
          {activeMenu === 'overview' && (
            <div className="space-y-8">
              {stats && (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4 md:gap-6">
                  <MetricCard label="Dokter Terdaftar" value={stats.total_doctors} color="emerald" icon="🩺" />
                  <MetricCard label="Ruang Poli" value={stats.total_clinic_rooms ?? clinicRooms.length} color="emerald" icon="🏥" />
                  <MetricCard label="Total Pertanyaan AI" value={stats.total_queries_run} color="emerald" icon="✨" />
                  <MetricCard label="Token Gemini" value={stats.total_gemini_tokens} color="emerald" icon="⚡" />
                  <MetricCard label="LLM Aktif" value={stats.gemini_model_active} color="emerald" icon="🧠" />
                </div>
              )}

              <MonitoringCard monitoring={monitoring} />
              <AnalyticsView analytics={analytics} />

              <UserTable
                users={users}
                onToggleStatus={toggleUserStatus}
                onOpenCreateModal={() => setCreateUserOpen(true)}
              />

              <ClinicRoomManagement
                clinicRooms={clinicRooms}
                onCreateRoom={createClinicRoom}
                onUpdateRoom={updateClinicRoom}
                onDeleteRoom={deleteClinicRoom}
                onToggleStatus={toggleClinicRoomStatus}
                savingRoom={savingClinicRoom}
              />

              <AuditFeed logs={auditLogs} />
            </div>
          )}

          {/* Section: Users */}
          {activeMenu === 'users' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-emerald-950 dark:text-white">Manajemen Akun Dokter</h2>
                  <p className="text-xs text-emerald-700 dark:text-slate-400">Kelola akun, hak akses, dan status lisensi SIP/STR dokter.</p>
                </div>
              </div>
              <UserTable
                users={users}
                onToggleStatus={toggleUserStatus}
                onOpenCreateModal={() => setCreateUserOpen(true)}
              />
            </div>
          )}

          {/* Section: Clinic Rooms */}
          {activeMenu === 'clinic_rooms' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-bold text-emerald-950 dark:text-white">Manajemen Ruangan Poliklinik</h2>
                <p className="text-xs text-emerald-700 dark:text-slate-400">
                  Kelola master data ruangan poli rawat jalan, penugasan dokter bertugas, spesialisasi, dan status operasional.
                </p>
              </div>
              <ClinicRoomManagement
                clinicRooms={clinicRooms}
                onCreateRoom={createClinicRoom}
                onUpdateRoom={updateClinicRoom}
                onDeleteRoom={deleteClinicRoom}
                onToggleStatus={toggleClinicRoomStatus}
                savingRoom={savingClinicRoom}
              />
            </div>
          )}


          {/* Section: Guardrails */}
          {activeMenu === 'guardrails' && <GuardrailsPanel />}

          {/* Section: Monitoring */}
          {activeMenu === 'monitoring' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-bold text-emerald-950 dark:text-white">Kesehatan & Monitoring Layanan</h2>
                <p className="text-xs text-emerald-700 dark:text-slate-400">Status koneksi real-time FastAPI, SIMRS MCP Server, Qdrant Vector, dan Gemini API.</p>
              </div>
              <MonitoringCard monitoring={monitoring} />
            </div>
          )}

          {/* Section: Analytics */}
          {activeMenu === 'analytics' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-bold text-emerald-950 dark:text-white">Analitik Penggunaan & Konsumsi Token</h2>
                <p className="text-xs text-emerald-700 dark:text-slate-400">Grafik interaksi harian, alokasi token LLM Gemini, dan latensi inferensi.</p>
              </div>
              <AnalyticsView analytics={analytics} />
            </div>
          )}

          {/* Section: Audit */}
          {activeMenu === 'audit' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-bold text-emerald-950 dark:text-white">Audit Trail & Log Aktivitas</h2>
                <p className="text-xs text-emerald-700 dark:text-slate-400">Rekam jejak setiap pemanggilan tools, pencarian EHR pasien, dan eksekusi AI.</p>
              </div>
              <AuditFeed logs={auditLogs} />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}


