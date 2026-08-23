'use client';

import { useState, useMemo } from 'react';
import type { ClinicRoomAdmin, CreateClinicRoomInput, UpdateClinicRoomInput } from '@/services/admin.service';
import ClinicRoomModal from './ClinicRoomModal';

interface ClinicRoomManagementProps {
  clinicRooms: ClinicRoomAdmin[];
  onCreateRoom: (input: CreateClinicRoomInput) => Promise<boolean>;
  onUpdateRoom: (roomId: string, input: UpdateClinicRoomInput) => Promise<boolean>;
  onDeleteRoom: (roomId: string) => Promise<boolean>;
  onToggleStatus: (roomId: string) => Promise<boolean>;
  savingRoom: boolean;
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
  'Orthopedics': '🦴',
  'Pulmonology': '🫁',
  'Obstetrics & Gynecology': '🤰',
  'Psychiatry': '🧠',
  'General Practice / Primary Care': '🏥',
};

export default function ClinicRoomManagement({
  clinicRooms,
  onCreateRoom,
  onUpdateRoom,
  onDeleteRoom,
  onToggleStatus,
  savingRoom,
}: ClinicRoomManagementProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterBuilding, setFilterBuilding] = useState('all');
  const [filterFloor, setFilterFloor] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table');

  // Modal States
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRoom, setEditingRoom] = useState<ClinicRoomAdmin | null>(null);

  // Delete Confirmation State
  const [deleteConfirmRoom, setDeleteConfirmRoom] = useState<ClinicRoomAdmin | null>(null);
  const [deleting, setDeleting] = useState(false);

  // Status Toggling State
  const [togglingId, setTogglingId] = useState<string | null>(null);

  // Toast feedback
  const [toastMessage, setToastMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const showToast = (text: string, type: 'success' | 'error' = 'success') => {
    setToastMessage({ text, type });
    setTimeout(() => {
      setToastMessage(null);
    }, 4000);
  };

  // Extract unique buildings and floors for filter dropdowns
  const availableBuildings = useMemo(() => {
    const set = new Set<string>();
    clinicRooms.forEach((r) => {
      if (r.building) set.add(r.building);
    });
    return Array.from(set).sort();
  }, [clinicRooms]);

  const availableFloors = useMemo(() => {
    const set = new Set<string>();
    clinicRooms.forEach((r) => {
      if (r.floor) set.add(r.floor);
    });
    return Array.from(set).sort();
  }, [clinicRooms]);

  // Summary Metrics
  const metrics = useMemo(() => {
    const total = clinicRooms.length;
    const active = clinicRooms.filter((r) => r.status === 'active').length;
    const maintenance = clinicRooms.filter((r) => r.status === 'maintenance' || r.status === 'inactive').length;
    const withDoctor = clinicRooms.filter((r) => r.assigned_doctors && r.assigned_doctors.length > 0).length;
    return { total, active, maintenance, withDoctor };
  }, [clinicRooms]);

  // Filtered List
  const filteredRooms = useMemo(() => {
    return clinicRooms.filter((room) => {
      const matchesSearch =
        !searchQuery.trim() ||
        room.room_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        room.room_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
        room.specialty.toLowerCase().includes(searchQuery.toLowerCase()) ||
        room.building.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (room.description && room.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
        room.assigned_doctors.some((d) => d.name.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesBuilding = filterBuilding === 'all' || room.building === filterBuilding;
      const matchesFloor = filterFloor === 'all' || room.floor === filterFloor;
      const matchesStatus = filterStatus === 'all' || room.status === filterStatus;

      return matchesSearch && matchesBuilding && matchesFloor && matchesStatus;
    });
  }, [clinicRooms, searchQuery, filterBuilding, filterFloor, filterStatus]);

  // Handlers
  const handleOpenCreate = () => {
    setEditingRoom(null);
    setIsModalOpen(true);
  };

  const handleOpenEdit = (room: ClinicRoomAdmin) => {
    setEditingRoom(room);
    setIsModalOpen(true);
  };

  const handleModalSubmit = async (input: CreateClinicRoomInput | UpdateClinicRoomInput) => {
    if (editingRoom) {
      const ok = await onUpdateRoom(editingRoom.room_id, input as UpdateClinicRoomInput);
      if (ok) {
        showToast(`Ruangan poli ${editingRoom.room_code} berhasil diperbarui.`);
        return true;
      } else {
        showToast(`Gagal memperbarui ruangan poli ${editingRoom.room_code}.`, 'error');
        return false;
      }
    } else {
      const ok = await onCreateRoom(input as CreateClinicRoomInput);
      if (ok) {
        showToast(`Ruangan poli baru berhasil ditambahkan.`);
        return true;
      } else {
        showToast(`Gagal menambahkan ruangan poli baru.`, 'error');
        return false;
      }
    }
  };

  const handleToggleStatus = async (room: ClinicRoomAdmin) => {
    setTogglingId(room.room_id);
    try {
      const ok = await onToggleStatus(room.room_id);
      if (ok) {
        showToast(`Status ruangan poli ${room.room_code} berhasil diubah.`);
      } else {
        showToast(`Gagal mengubah status ruangan ${room.room_code}.`, 'error');
      }
    } finally {
      setTogglingId(null);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteConfirmRoom) return;
    setDeleting(true);
    try {
      const ok = await onDeleteRoom(deleteConfirmRoom.room_id);
      if (ok) {
        showToast(`Ruangan poli ${deleteConfirmRoom.room_code} berhasil dihapus.`);
        setDeleteConfirmRoom(null);
      } else {
        showToast(`Gagal menghapus ruangan poli ${deleteConfirmRoom.room_code}.`, 'error');
      }
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {toastMessage && (
        <div
          className={`p-4 rounded-2xl text-xs font-semibold flex items-center justify-between border shadow-lg transition-all animate-in slide-in-from-top-2 duration-200 ${
            toastMessage.type === 'success'
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-900 dark:text-emerald-300'
              : 'bg-red-500/10 border-red-500/30 text-red-900 dark:text-red-300'
          }`}
        >
          <div className="flex items-center gap-2.5">
            <span className="text-base">{toastMessage.type === 'success' ? '✅' : '❌'}</span>
            <span>{toastMessage.text}</span>
          </div>
          <button
            type="button"
            onClick={() => setToastMessage(null)}
            className="text-xs opacity-70 hover:opacity-100"
          >
            ✕
          </button>
        </div>
      )}

      {/* Modal Form Tambah / Edit */}
      <ClinicRoomModal
        isOpen={isModalOpen}
        room={editingRoom}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleModalSubmit}
        submitting={savingRoom}
      />

      {/* Modal Konfirmasi Hapus */}
      {deleteConfirmRoom && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white dark:bg-slate-900 border border-red-200 dark:border-red-900/50 rounded-3xl shadow-2xl w-full max-w-md p-6 animate-in zoom-in-95 duration-200">
            <div className="flex items-center gap-3 text-red-600 dark:text-red-400 mb-3">
              <div className="w-10 h-10 rounded-2xl bg-red-100 dark:bg-red-950/50 flex items-center justify-center text-xl">
                🗑️
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Hapus Ruang Poli?
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Tindakan ini tidak dapat dibatalkan.
                </p>
              </div>
            </div>

            <div className="my-4 p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200 dark:border-slate-700 text-xs space-y-1.5">
              <div className="font-bold text-slate-900 dark:text-white">
                {deleteConfirmRoom.room_name} ({deleteConfirmRoom.room_code})
              </div>
              <div className="text-slate-600 dark:text-slate-400">
                {deleteConfirmRoom.building} • {deleteConfirmRoom.floor} • {deleteConfirmRoom.specialty}
              </div>
              {deleteConfirmRoom.assigned_doctors && deleteConfirmRoom.assigned_doctors.length > 0 && (
                <div className="mt-2 p-2 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-xl text-amber-800 dark:text-amber-300 text-[11px]">
                  ⚠️ Perhatian: Terdapat <strong>{deleteConfirmRoom.assigned_doctors.length} dokter</strong> yang sedang bertugas di ruangan ini. Dokter akan otomatis di-unassign.
                </div>
              )}
            </div>

            <div className="flex items-center gap-3 mt-5">
              <button
                type="button"
                disabled={deleting}
                onClick={() => setDeleteConfirmRoom(null)}
                className="flex-1 py-2.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-semibold rounded-xl text-xs transition-colors"
              >
                Batal
              </button>
              <button
                type="button"
                disabled={deleting}
                onClick={handleDeleteConfirm}
                className="flex-1 py-2.5 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white font-semibold rounded-xl text-xs transition-all shadow-md shadow-red-600/20 active:scale-[0.98]"
              >
                {deleting ? 'Menghapus…' : 'Ya, Hapus Ruangan'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Summary Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 rounded-2xl shadow-sm flex items-center justify-between">
          <div>
            <p className="text-[11px] font-semibold text-emerald-700 dark:text-slate-400">Total Ruang Poli</p>
            <p className="text-2xl font-black text-emerald-950 dark:text-white mt-1">{metrics.total}</p>
          </div>
          <div className="w-11 h-11 rounded-2xl bg-emerald-100 dark:bg-slate-800 text-emerald-700 dark:text-emerald-400 flex items-center justify-center text-xl font-bold">
            🏥
          </div>
        </div>

        <div className="p-4 bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 rounded-2xl shadow-sm flex items-center justify-between">
          <div>
            <p className="text-[11px] font-semibold text-emerald-700 dark:text-slate-400">Poli Aktif / Siap</p>
            <p className="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-1">{metrics.active}</p>
          </div>
          <div className="w-11 h-11 rounded-2xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-xl font-bold">
            🟢
          </div>
        </div>

        <div className="p-4 bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 rounded-2xl shadow-sm flex items-center justify-between">
          <div>
            <p className="text-[11px] font-semibold text-emerald-700 dark:text-slate-400">Poli Terisi Dokter</p>
            <p className="text-2xl font-black text-teal-600 dark:text-teal-400 mt-1">{metrics.withDoctor}</p>
          </div>
          <div className="w-11 h-11 rounded-2xl bg-teal-500/15 text-teal-600 dark:text-teal-400 flex items-center justify-center text-xl font-bold">
            🩺
          </div>
        </div>

        <div className="p-4 bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 rounded-2xl shadow-sm flex items-center justify-between">
          <div>
            <p className="text-[11px] font-semibold text-emerald-700 dark:text-slate-400">Nonaktif / Perawatan</p>
            <p className="text-2xl font-black text-amber-600 dark:text-amber-400 mt-1">{metrics.maintenance}</p>
          </div>
          <div className="w-11 h-11 rounded-2xl bg-amber-500/15 text-amber-600 dark:text-amber-400 flex items-center justify-center text-xl font-bold">
            🛠️
          </div>
        </div>
      </div>

      {/* Main Table & Filter Panel */}
      <div className="bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm">
        {/* Header & Action Bar */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="text-xl">🏥</span>
              <h2 className="text-lg font-bold text-emerald-950 dark:text-white">
                Daftar Ruangan Poliklinik
              </h2>
            </div>
            <p className="text-xs text-emerald-700 dark:text-slate-400 mt-0.5">
              Kelola master data ruangan poli, penugasan dokter, spesialisasi, dan status operasional.
            </p>
          </div>

          <div className="flex items-center gap-2.5 flex-wrap">
            {/* View Mode Toggle */}
            <div className="flex items-center bg-emerald-50 dark:bg-slate-800 p-1 rounded-xl border border-emerald-200/80 dark:border-slate-700">
              <button
                type="button"
                onClick={() => setViewMode('table')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                  viewMode === 'table'
                    ? 'bg-white dark:bg-slate-900 text-emerald-900 dark:text-emerald-300 shadow-xs'
                    : 'text-emerald-700 dark:text-slate-400 hover:text-emerald-900'
                }`}
              >
                <span>📑</span>
                <span>Tabel</span>
              </button>
              <button
                type="button"
                onClick={() => setViewMode('grid')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                  viewMode === 'grid'
                    ? 'bg-white dark:bg-slate-900 text-emerald-900 dark:text-emerald-300 shadow-xs'
                    : 'text-emerald-700 dark:text-slate-400 hover:text-emerald-900'
                }`}
              >
                <span>🗂️</span>
                <span>Grid Kartu</span>
              </button>
            </div>

            {/* Create Button */}
            <button
              type="button"
              onClick={handleOpenCreate}
              className="py-2.5 px-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold shadow-md shadow-emerald-600/20 transition-all flex items-center gap-2 active:scale-[0.98]"
            >
              <span className="text-sm font-bold">➕</span>
              <span>Tambah Ruang Poli</span>
            </button>
          </div>
        </div>

        {/* Filter Controls Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 p-4 bg-emerald-50/60 dark:bg-slate-800/50 rounded-2xl border border-emerald-200/70 dark:border-slate-700 mb-6">
          {/* Search Box */}
          <div>
            <label className="block text-[10px] font-bold text-emerald-800 dark:text-slate-300 uppercase tracking-wider mb-1">
              Pencarian
            </label>
            <input
              type="text"
              placeholder="Cari nama, kode, spesialis, dokter..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-xs text-emerald-950 dark:text-slate-100 placeholder-emerald-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
            />
          </div>

          {/* Building Filter */}
          <div>
            <label className="block text-[10px] font-bold text-emerald-800 dark:text-slate-300 uppercase tracking-wider mb-1">
              Filter Gedung
            </label>
            <select
              value={filterBuilding}
              onChange={(e) => setFilterBuilding(e.target.value)}
              className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-xs text-emerald-950 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
            >
              <option value="all">Semua Gedung ({clinicRooms.length})</option>
              {availableBuildings.map((b) => (
                <option key={b} value={b}>
                  {b}
                </option>
              ))}
            </select>
          </div>

          {/* Floor Filter */}
          <div>
            <label className="block text-[10px] font-bold text-emerald-800 dark:text-slate-300 uppercase tracking-wider mb-1">
              Filter Lantai
            </label>
            <select
              value={filterFloor}
              onChange={(e) => setFilterFloor(e.target.value)}
              className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-xs text-emerald-950 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
            >
              <option value="all">Semua Lantai</option>
              {availableFloors.map((f) => (
                <option key={f} value={f}>
                  {f}
                </option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-[10px] font-bold text-emerald-800 dark:text-slate-300 uppercase tracking-wider mb-1">
              Filter Status
            </label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-xs text-emerald-950 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
            >
              <option value="all">Semua Status</option>
              <option value="active">🟢 Aktif</option>
              <option value="inactive">🔴 Nonaktif</option>
              <option value="maintenance">🟡 Pemeliharaan</option>
            </select>
          </div>
        </div>

        {/* Content View: Table or Grid */}
        {filteredRooms.length === 0 ? (
          <div className="text-center py-12 border-2 border-dashed border-emerald-200/60 dark:border-slate-800 rounded-3xl">
            <span className="text-3xl block mb-2">🔍</span>
            <p className="text-sm font-bold text-emerald-950 dark:text-white">Tidak ada ruangan poli yang sesuai</p>
            <p className="text-xs text-emerald-700 dark:text-slate-400 mt-1 max-w-sm mx-auto">
              Coba sesuaikan kata kunci pencarian atau bersihkan filter gedung/status.
            </p>
            <button
              type="button"
              onClick={() => {
                setSearchQuery('');
                setFilterBuilding('all');
                setFilterFloor('all');
                setFilterStatus('all');
              }}
              className="mt-3.5 px-4 py-2 bg-emerald-100 dark:bg-slate-800 hover:bg-emerald-200 dark:hover:bg-slate-700 text-emerald-900 dark:text-emerald-300 rounded-xl text-xs font-semibold transition-colors"
            >
              Reset Semua Filter
            </button>
          </div>
        ) : viewMode === 'table' ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-emerald-200 dark:border-slate-800 text-[10px] text-emerald-800 dark:text-slate-400 uppercase tracking-wider">
                  <th className="pb-3 pr-4">Ruangan &amp; Kode</th>
                  <th className="pb-3 pr-4">Lokasi</th>
                  <th className="pb-3 pr-4">Spesialisasi</th>
                  <th className="pb-3 pr-4">Jam Operasional</th>
                  <th className="pb-3 pr-4">Dokter Bertugas</th>
                  <th className="pb-3 pr-4">Status</th>
                  <th className="pb-3 text-right">Aksi</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-emerald-100 dark:divide-slate-800">
                {filteredRooms.map((room) => {
                  const icon = SPECIALTY_ICONS[room.specialty] || '🏥';
                  const isToggling = togglingId === room.room_id;

                  return (
                    <tr key={room.room_id} className="group hover:bg-emerald-50/40 dark:hover:bg-slate-800/40 transition-colors">
                      {/* Name & Code */}
                      <td className="py-3.5 pr-4">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-xl bg-emerald-100/70 dark:bg-slate-800 text-emerald-700 dark:text-emerald-400 flex items-center justify-center text-base shrink-0 font-bold">
                            {icon}
                          </div>
                          <div className="min-w-0">
                            <div className="font-bold text-xs text-emerald-950 dark:text-slate-100 truncate">
                              {room.room_name}
                            </div>
                            <div className="flex items-center gap-1.5 mt-0.5">
                              <span className="font-mono text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100/80 dark:bg-slate-800 text-emerald-800 dark:text-emerald-300 border border-emerald-200/80 dark:border-slate-700">
                                {room.room_code}
                              </span>
                              <span className="text-[10px] text-emerald-600 dark:text-slate-400">
                                {room.room_id}
                              </span>
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* Location */}
                      <td className="py-3.5 pr-4 text-xs text-emerald-800 dark:text-slate-300">
                        <div className="font-semibold">{room.building}</div>
                        <div className="text-[10px] text-emerald-600 dark:text-slate-400">{room.floor}</div>
                      </td>

                      {/* Specialty */}
                      <td className="py-3.5 pr-4">
                        <span className="inline-block px-2.5 py-1 rounded-lg text-[10px] font-semibold bg-emerald-100/60 dark:bg-slate-800 text-emerald-800 dark:text-emerald-400 border border-emerald-200/60 dark:border-slate-700">
                          {room.specialty}
                        </span>
                      </td>

                      {/* Hours */}
                      <td className="py-3.5 pr-4 text-xs text-emerald-800 dark:text-slate-300">
                        <span className="font-mono text-[11px]">{room.operational_hours || '08:00 - 16:00 WIB'}</span>
                      </td>

                      {/* Assigned Doctors */}
                      <td className="py-3.5 pr-4">
                        {room.assigned_doctors && room.assigned_doctors.length > 0 ? (
                          <div className="flex flex-wrap gap-1 max-w-xs">
                            {room.assigned_doctors.map((doc) => (
                              <span
                                key={doc.id}
                                className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-teal-100 dark:bg-teal-950/60 text-teal-800 dark:text-teal-300 border border-teal-200 dark:border-teal-800"
                                title={`${doc.name} (${doc.email})`}
                              >
                                <span className="w-1.5 h-1.5 rounded-full bg-teal-500" />
                                {doc.name.split(',')[0]}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <span className="text-[11px] text-slate-400 italic">
                            Belum ada dokter
                          </span>
                        )}
                      </td>

                      {/* Status */}
                      <td className="py-3.5 pr-4">
                        <span
                          className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold border ${
                            room.status === 'active'
                              ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/30'
                              : room.status === 'maintenance'
                              ? 'bg-amber-500/15 text-amber-700 dark:text-amber-300 border-amber-500/30'
                              : 'bg-red-500/15 text-red-700 dark:text-red-300 border-red-500/30'
                          }`}
                        >
                          <span
                            className={`w-1.5 h-1.5 rounded-full ${
                              room.status === 'active'
                                ? 'bg-emerald-500'
                                : room.status === 'maintenance'
                                ? 'bg-amber-500'
                                : 'bg-red-500'
                            }`}
                          />
                          {room.status === 'active'
                            ? 'Aktif'
                            : room.status === 'maintenance'
                            ? 'Pemeliharaan'
                            : 'Nonaktif'}
                        </span>
                      </td>

                      {/* Action buttons */}
                      <td className="py-3.5 text-right">
                        <div className="inline-flex items-center gap-1.5 justify-end">
                          <button
                            type="button"
                            onClick={() => handleToggleStatus(room)}
                            disabled={isToggling}
                            title={room.status === 'active' ? 'Nonaktifkan Ruangan' : 'Aktifkan Ruangan'}
                            className="px-2.5 py-1 rounded-lg text-[10px] font-semibold bg-emerald-100 hover:bg-emerald-200/80 dark:bg-slate-800 dark:hover:bg-slate-700 text-emerald-900 dark:text-emerald-300 border border-emerald-300 dark:border-slate-700 transition-colors"
                          >
                            {isToggling ? '…' : room.status === 'active' ? 'Nonaktifkan' : 'Aktifkan'}
                          </button>

                          <button
                            type="button"
                            onClick={() => handleOpenEdit(room)}
                            title="Ubah Data Ruangan"
                            className="p-1.5 rounded-lg text-emerald-700 hover:text-emerald-900 dark:text-slate-300 dark:hover:text-white bg-emerald-50 hover:bg-emerald-100 dark:bg-slate-800 dark:hover:bg-slate-700 border border-emerald-200 dark:border-slate-700 transition-colors"
                          >
                            ✏️
                          </button>

                          <button
                            type="button"
                            onClick={() => setDeleteConfirmRoom(room)}
                            title="Hapus Ruangan"
                            className="p-1.5 rounded-lg text-red-600 hover:text-red-700 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/40 border border-red-200 dark:border-red-900/50 transition-colors"
                          >
                            🗑️
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          /* Grid Cards View */
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredRooms.map((room) => {
              const icon = SPECIALTY_ICONS[room.specialty] || '🏥';
              const isToggling = togglingId === room.room_id;

              return (
                <div
                  key={room.room_id}
                  className="rounded-3xl p-5 bg-emerald-50/30 dark:bg-slate-850 border border-emerald-200 dark:border-slate-800 hover:border-emerald-400 dark:hover:border-slate-700 transition-all flex flex-col justify-between shadow-2xs hover:shadow-md group"
                >
                  <div>
                    {/* Top row */}
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-2xl bg-emerald-100 dark:bg-slate-800 text-emerald-700 dark:text-emerald-400 flex items-center justify-center text-lg font-bold">
                          {icon}
                        </div>
                        <div>
                          <h3 className="font-bold text-xs text-emerald-950 dark:text-white line-clamp-1">
                            {room.room_name}
                          </h3>
                          <div className="flex items-center gap-1.5 mt-0.5">
                            <span className="font-mono text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100/80 dark:bg-slate-800 text-emerald-800 dark:text-emerald-300">
                              {room.room_code}
                            </span>
                            <span className="text-[10px] text-emerald-600 dark:text-slate-400 font-medium">
                              {room.room_id}
                            </span>
                          </div>
                        </div>
                      </div>

                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold border ${
                          room.status === 'active'
                            ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/30'
                            : room.status === 'maintenance'
                            ? 'bg-amber-500/15 text-amber-700 dark:text-amber-300 border-amber-500/30'
                            : 'bg-red-500/15 text-red-700 dark:text-red-300 border-red-500/30'
                        }`}
                      >
                        {room.status === 'active' ? 'Aktif' : room.status === 'maintenance' ? 'Maintenance' : 'Nonaktif'}
                      </span>
                    </div>

                    {/* Tags & info */}
                    <div className="space-y-1.5 my-3 text-[11px]">
                      <div className="flex items-center justify-between text-emerald-800 dark:text-slate-300">
                        <span className="text-emerald-600 dark:text-slate-400 text-[10px]">Lokasi:</span>
                        <span className="font-semibold">{room.building} ({room.floor})</span>
                      </div>
                      <div className="flex items-center justify-between text-emerald-800 dark:text-slate-300">
                        <span className="text-emerald-600 dark:text-slate-400 text-[10px]">Spesialisasi:</span>
                        <span className="font-medium truncate max-w-[140px] text-right">{room.specialty}</span>
                      </div>
                      <div className="flex items-center justify-between text-emerald-800 dark:text-slate-300">
                        <span className="text-emerald-600 dark:text-slate-400 text-[10px]">Jam Layanan:</span>
                        <span className="font-mono">{room.operational_hours || '08:00 - 16:00 WIB'}</span>
                      </div>
                    </div>

                    {/* Assigned doctor banner */}
                    <div className="p-2.5 bg-white/70 dark:bg-slate-800/80 rounded-xl border border-emerald-100 dark:border-slate-700 my-2">
                      <div className="text-[10px] font-bold text-emerald-700 dark:text-slate-400 mb-1 flex items-center gap-1">
                        <span>🩺</span>
                        <span>Dokter Bertugas:</span>
                      </div>
                      {room.assigned_doctors && room.assigned_doctors.length > 0 ? (
                        <div className="space-y-1">
                          {room.assigned_doctors.map((d) => (
                            <div key={d.id} className="text-xs font-bold text-teal-800 dark:text-teal-300 flex items-center gap-1.5">
                              <span className="w-2 h-2 rounded-full bg-teal-500" />
                              <span className="truncate">{d.name}</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-[10px] text-slate-400 italic">
                          Tidak ada dokter yang aktif di ruangan ini.
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Card bottom actions */}
                  <div className="flex items-center justify-between gap-2 pt-3 border-t border-emerald-100 dark:border-slate-800 mt-2">
                    <button
                      type="button"
                      onClick={() => handleToggleStatus(room)}
                      disabled={isToggling}
                      className="px-2.5 py-1.5 rounded-xl text-[10px] font-semibold bg-emerald-100 hover:bg-emerald-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-emerald-900 dark:text-emerald-300 border border-emerald-300 dark:border-slate-700 transition-colors"
                    >
                      {isToggling ? '…' : room.status === 'active' ? 'Nonaktifkan' : 'Aktifkan'}
                    </button>

                    <div className="flex items-center gap-1.5">
                      <button
                        type="button"
                        onClick={() => handleOpenEdit(room)}
                        className="p-1.5 rounded-xl text-emerald-700 dark:text-slate-300 hover:bg-emerald-100 dark:hover:bg-slate-700 border border-emerald-200 dark:border-slate-700 transition-colors text-xs"
                      >
                        ✏️ Edit
                      </button>
                      <button
                        type="button"
                        onClick={() => setDeleteConfirmRoom(room)}
                        className="p-1.5 rounded-xl text-red-600 hover:bg-red-50 dark:hover:bg-red-950/40 border border-red-200 dark:border-red-900/50 transition-colors text-xs"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
