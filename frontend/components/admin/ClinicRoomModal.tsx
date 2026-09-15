'use client';

import { useState, useEffect } from 'react';
import type { ClinicRoomAdmin, CreateClinicRoomInput, UpdateClinicRoomInput } from '@/services/admin.service';

interface ClinicRoomModalProps {
  isOpen: boolean;
  room?: ClinicRoomAdmin | null;
  onClose: () => void;
  onSubmit: (input: CreateClinicRoomInput | UpdateClinicRoomInput) => Promise<boolean>;
  submitting: boolean;
}

const COMMON_SPECIALTIES = [
  { value: 'Internal Medicine', label: 'Internal Medicine (Penyakit Dalam)' },
  { value: 'Cardiology', label: 'Cardiology (Jantung & Pembuluh Darah)' },
  { value: 'Neurology', label: 'Neurology (Saraf / Neurologi)' },
  { value: 'General Surgery', label: 'General Surgery (Bedah Umum)' },
  { value: 'Pediatrics', label: 'Pediatrics (Anak & Tumbuh Kembang)' },
  { value: 'Gastroenterology', label: 'Gastroenterology (Pencernaan & Hepatologi)' },
  { value: 'Dermatology', label: 'Dermatology (Kulit & Kelamin)' },
  { value: 'Ophthalmology', label: 'Ophthalmology (Mata)' },
  { value: 'Orthopedics', label: 'Orthopedics (Tulang & Traumatologi)' },
  { value: 'Pulmonology', label: 'Pulmonology (Paru & Respirasi)' },
  { value: 'Obstetrics & Gynecology', label: 'Obstetrics & Gynecology (Kebidanan & Kandungan)' },
  { value: 'Psychiatry', label: 'Psychiatry (Kesehatan Jiwa)' },
  { value: 'General Practice / Primary Care', label: 'General Practice (Kedokteran Umum)' },
  { value: 'other', label: '➕ Spesialisasi Lainnya (Kustom)...' },
];

const COMMON_BUILDINGS = [
  'Gedung A',
  'Gedung B',
  'Gedung C',
  'Gedung Utama (Poliklinik)',
  'Gedung Rawat Jalan Terpadu',
  'Gedung Sayap Timur',
  'Gedung Sayap Barat',
  'other',
];

const COMMON_FLOORS = [
  'Lantai 1',
  'Lantai 2',
  'Lantai 3',
  'Lantai 4',
  'Lantai 5',
  'other',
];

export default function ClinicRoomModal({
  isOpen,
  room,
  onClose,
  onSubmit,
  submitting,
}: ClinicRoomModalProps) {
  const isEditing = Boolean(room);

  const [roomName, setRoomName] = useState('');
  const [roomCode, setRoomCode] = useState('');
  const [specialtySelect, setSpecialtySelect] = useState('Internal Medicine');
  const [customSpecialty, setCustomSpecialty] = useState('');
  const [buildingSelect, setBuildingSelect] = useState('Gedung A');
  const [customBuilding, setCustomBuilding] = useState('');
  const [floorSelect, setFloorSelect] = useState('Lantai 1');
  const [customFloor, setCustomFloor] = useState('');
  const [operationalHours, setOperationalHours] = useState('08:00 - 16:00 WIB');
  const [status, setStatus] = useState<'active' | 'inactive' | 'maintenance'>('active');
  const [description, setDescription] = useState('');
  const [formError, setFormError] = useState('');

  useEffect(() => {
    if (isOpen) {
      setFormError('');
      if (room) {
        setRoomName(room.room_name || '');
        setRoomCode(room.room_code || '');

        // Specialty matching
        const foundSpecialty = COMMON_SPECIALTIES.find((s) => s.value === room.specialty);
        if (foundSpecialty && foundSpecialty.value !== 'other') {
          setSpecialtySelect(room.specialty);
          setCustomSpecialty('');
        } else {
          setSpecialtySelect('other');
          setCustomSpecialty(room.specialty || '');
        }

        // Building matching
        if (COMMON_BUILDINGS.includes(room.building)) {
          setBuildingSelect(room.building);
          setCustomBuilding('');
        } else {
          setBuildingSelect('other');
          setCustomBuilding(room.building || '');
        }

        // Floor matching
        if (COMMON_FLOORS.includes(room.floor)) {
          setFloorSelect(room.floor);
          setCustomFloor('');
        } else {
          setFloorSelect('other');
          setCustomFloor(room.floor || '');
        }

        setOperationalHours(room.operational_hours || '08:00 - 16:00 WIB');
        setStatus(room.status || 'active');
        setDescription(room.description || '');
      } else {
        // Reset defaults for create
        setRoomName('');
        setRoomCode('');
        setSpecialtySelect('Internal Medicine');
        setCustomSpecialty('');
        setBuildingSelect('Gedung A');
        setCustomBuilding('');
        setFloorSelect('Lantai 1');
        setCustomFloor('');
        setOperationalHours('08:00 - 16:00 WIB');
        setStatus('active');
        setDescription('');
      }
    }
  }, [isOpen, room]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');

    const finalSpecialty = specialtySelect === 'other' ? customSpecialty.trim() : specialtySelect;
    const finalBuilding = buildingSelect === 'other' ? customBuilding.trim() : buildingSelect;
    const finalFloor = floorSelect === 'other' ? customFloor.trim() : floorSelect;

    if (!roomName.trim()) {
      setFormError('Nama ruangan poli wajib diisi.');
      return;
    }
    if (!roomCode.trim()) {
      setFormError('Kode ruangan poli wajib diisi (contoh: IPD-01).');
      return;
    }
    if (!finalSpecialty) {
      setFormError('Spesialisasi medis wajib ditentukan.');
      return;
    }
    if (!finalBuilding) {
      setFormError('Gedung lokasi wajib ditentukan.');
      return;
    }
    if (!finalFloor) {
      setFormError('Lantai lokasi wajib ditentukan.');
      return;
    }

    const payload: CreateClinicRoomInput = {
      room_name: roomName.trim(),
      room_code: roomCode.trim().toUpperCase(),
      specialty: finalSpecialty,
      building: finalBuilding,
      floor: finalFloor,
      operational_hours: operationalHours.trim(),
      status,
      description: description.trim(),
    };

    const ok = await onSubmit(payload);
    if (ok) {
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white dark:bg-slate-900 border border-emerald-300 dark:border-slate-800 rounded-3xl shadow-2xl w-full max-w-lg max-h-[90vh] flex flex-col overflow-hidden transition-all animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="px-6 py-5 border-b border-emerald-100 dark:border-slate-800 bg-gradient-to-r from-emerald-50 via-teal-50 to-emerald-50/50 dark:from-slate-900 dark:via-slate-850 dark:to-slate-900 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-600 text-white flex items-center justify-center text-xl font-bold shadow-lg shadow-emerald-600/20">
              {isEditing ? '✏️' : '🏥'}
            </div>
            <div>
              <h3 className="text-base font-bold text-emerald-950 dark:text-slate-100">
                {isEditing ? `Ubah Ruang Poli (${room?.room_code})` : 'Tambah Ruang Poli Baru'}
              </h3>
              <p className="text-xs text-emerald-700 dark:text-slate-400 mt-0.5">
                {isEditing
                  ? 'Perbarui informasi lokasi, spesialisasi, atau jam layanan.'
                  : 'Daftarkan ruangan poliklinik baru ke sistem SIMRS & AssistantMedixa.'}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-xl flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Content / Form */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-4">
          {formError && (
            <div className="p-3 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-300 text-xs flex items-center gap-2">
              <span>⚠️</span>
              <span>{formError}</span>
            </div>
          )}

          {/* Row 1: Name & Code */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="sm:col-span-2">
              <label className="block text-[11px] font-bold text-emerald-900 dark:text-slate-200 mb-1">
                Nama Ruang Poli <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                placeholder="Contoh: Poli Penyakit Dalam"
                value={roomName}
                onChange={(e) => setRoomName(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-xs text-emerald-950 dark:text-slate-100 placeholder-emerald-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 transition-all"
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold text-emerald-900 dark:text-slate-200 mb-1">
                Kode Ruang <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                placeholder="IPD-01"
                value={roomCode}
                onChange={(e) => setRoomCode(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-xs uppercase font-mono font-bold text-emerald-950 dark:text-slate-100 placeholder-emerald-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 transition-all"
              />
            </div>
          </div>

          {/* Row 2: Specialty */}
          <div>
            <label className="block text-[11px] font-bold text-emerald-900 dark:text-slate-200 mb-1">
              Spesialisasi Medis <span className="text-red-500">*</span>
            </label>
            <select
              value={specialtySelect}
              onChange={(e) => setSpecialtySelect(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-xs text-emerald-950 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 transition-all"
            >
              {COMMON_SPECIALTIES.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
            {specialtySelect === 'other' && (
              <input
                type="text"
                placeholder="Tuliskan spesialisasi medis (mis. Onkologi Radiasi)..."
                value={customSpecialty}
                onChange={(e) => setCustomSpecialty(e.target.value)}
                className="mt-2 w-full px-3.5 py-2 bg-emerald-50/70 dark:bg-slate-800 border border-emerald-300 dark:border-slate-600 rounded-xl text-xs text-emerald-950 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 transition-all"
              />
            )}
          </div>

          {/* Row 3: Building & Floor */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-bold text-emerald-900 dark:text-slate-200 mb-1">
                Gedung <span className="text-red-500">*</span>
              </label>
              <select
                value={buildingSelect}
                onChange={(e) => setBuildingSelect(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-xs text-emerald-950 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 transition-all"
              >
                {COMMON_BUILDINGS.map((b) => (
                  <option key={b} value={b}>
                    {b === 'other' ? '➕ Gedung Lainnya...' : b}
                  </option>
                ))}
              </select>
              {buildingSelect === 'other' && (
                <input
                  type="text"
                  placeholder="Nama gedung..."
                  value={customBuilding}
                  onChange={(e) => setCustomBuilding(e.target.value)}
                  className="mt-2 w-full px-3.5 py-2 bg-emerald-50/70 dark:bg-slate-800 border border-emerald-300 dark:border-slate-600 rounded-xl text-xs text-emerald-950 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
                />
              )}
            </div>

            <div>
              <label className="block text-[11px] font-bold text-emerald-900 dark:text-slate-200 mb-1">
                Lantai <span className="text-red-500">*</span>
              </label>
              <select
                value={floorSelect}
                onChange={(e) => setFloorSelect(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-xs text-emerald-950 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 transition-all"
              >
                {COMMON_FLOORS.map((f) => (
                  <option key={f} value={f}>
                    {f === 'other' ? '➕ Lantai Lainnya...' : f}
                  </option>
                ))}
              </select>
              {floorSelect === 'other' && (
                <input
                  type="text"
                  placeholder="Contoh: Lantai Dasar / Basement..."
                  value={customFloor}
                  onChange={(e) => setCustomFloor(e.target.value)}
                  className="mt-2 w-full px-3.5 py-2 bg-emerald-50/70 dark:bg-slate-800 border border-emerald-300 dark:border-slate-600 rounded-xl text-xs text-emerald-950 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
                />
              )}
            </div>
          </div>

          {/* Row 4: Operational Hours & Status */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-bold text-emerald-900 dark:text-slate-200 mb-1">
                Jam Operasional
              </label>
              <input
                type="text"
                placeholder="08:00 - 16:00 WIB"
                value={operationalHours}
                onChange={(e) => setOperationalHours(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-xs text-emerald-950 dark:text-slate-100 placeholder-emerald-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 transition-all"
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold text-emerald-900 dark:text-slate-200 mb-1">
                Status Operasional
              </label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as 'active' | 'inactive' | 'maintenance')}
                className="w-full px-3.5 py-2.5 bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-xs font-semibold text-emerald-950 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 transition-all"
              >
                <option value="active">🟢 Aktif (Siap Bertugas)</option>
                <option value="inactive">🔴 Nonaktif (Tutup)</option>
                <option value="maintenance">🟡 Pemeliharaan (Maintenance)</option>
              </select>
            </div>
          </div>

          {/* Row 5: Description */}
          <div>
            <label className="block text-[11px] font-bold text-emerald-900 dark:text-slate-200 mb-1">
              Deskripsi / Fasilitas Ruangan
            </label>
            <textarea
              rows={2}
              placeholder="Catatan fasilitas ruangan, peralatan medis khusus, atau keterangan poliklinik..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-emerald-50/50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-xs text-emerald-950 dark:text-slate-100 placeholder-emerald-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 transition-all resize-none"
            />
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3 pt-3 border-t border-emerald-100 dark:border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 bg-emerald-100/70 hover:bg-emerald-200/80 dark:bg-slate-800 dark:hover:bg-slate-700 text-emerald-900 dark:text-slate-200 font-semibold rounded-xl text-xs border border-emerald-200 dark:border-slate-700 transition-colors"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold rounded-xl text-xs transition-all shadow-md shadow-emerald-600/20 active:scale-[0.98]"
            >
              {submitting ? (
                <span className="flex items-center justify-center gap-1.5">
                  <span className="animate-spin">⏳</span>
                  <span>Menyimpan…</span>
                </span>
              ) : isEditing ? (
                'Simpan Perubahan'
              ) : (
                '+ Tambahkan Ruang Poli'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
