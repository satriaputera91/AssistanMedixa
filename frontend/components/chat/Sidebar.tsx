'use client';
import { useState, useEffect } from 'react';
import type { PatientRecord, ChatSession, ClinicRoom } from '@/services/agent.service';
import BotAvatar from '@/components/common/BotAvatar';
import ChatSearchModal from './ChatSearchModal';
import DeleteConfirmModal from '@/components/common/DeleteConfirmModal';

interface SidebarProps {
  patients: PatientRecord[];
  selectedPatient: string;
  onSelectPatient: (id: string) => void;
  sessions: ChatSession[];
  activeSessionId: string;
  onSelectSession: (id: string) => void;
  onNewSession?: () => void;
  onRenameSession?: (sessionId: string, newTitle: string) => Promise<void> | void;
  onDeleteSession?: (sessionId: string) => Promise<void> | void;
  userName: string;
  userRole: string;
  selectedRoom?: ClinicRoom | null;
  onChangeRoom?: () => void;
}

export default function Sidebar({
  patients,
  selectedPatient,
  onSelectPatient,
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onRenameSession,
  onDeleteSession,
  userName,
  userRole,
  selectedRoom,
  onChangeRoom,
}: SidebarProps) {
  const [searchModalOpen, setSearchModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [pendingDeleteSession, setPendingDeleteSession] = useState<ChatSession | null>(null);

  // Global shortcut Cmd+K / Ctrl+K to open search modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setSearchModalOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const currentPatientObj = patients.find(p => p.patient_id === selectedPatient);

  const filteredSessions = sessions.filter((s) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    const titleMatch = (s.title || '').toLowerCase().includes(q);
    const patientMatch = (s.patient_id || '').toLowerCase().includes(q);
    const messagesMatch = (s.messages || []).some((m) =>
      (m.content || '').toLowerCase().includes(q)
    );
    return titleMatch || patientMatch || messagesMatch;
  });

  const startRename = (session: ChatSession, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingSessionId(session.session_id);
    setEditTitle(session.title || 'Konsultasi');
  };

  const handleSaveRename = async (sessionId: string, e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (onRenameSession && editTitle.trim()) {
      await onRenameSession(sessionId, editTitle.trim());
    }
    setEditingSessionId(null);
  };

  const openDeleteModal = (session: ChatSession, e: React.MouseEvent) => {
    e.stopPropagation();
    setPendingDeleteSession(session);
  };

  const handleConfirmDelete = async () => {
    if (!pendingDeleteSession) return;
    setDeletingId(pendingDeleteSession.session_id);
    try {
      if (onDeleteSession) await onDeleteSession(pendingDeleteSession.session_id);
      setPendingDeleteSession(null);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <aside className="w-80 bg-white dark:bg-slate-900 border-r border-emerald-200 dark:border-slate-800 flex flex-col shrink-0 transition-colors">
      {/* Header & New Chat Button */}
      <div className="p-4 border-b border-emerald-200 dark:border-slate-800">
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2.5">
            <BotAvatar size="sm" />
            <span className="font-bold text-emerald-950 dark:text-white text-sm">Asisten AI Medis</span>
          </div>
        </div>
        <button
          type="button"
          onClick={onNewSession}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold shadow-sm transition-all active:scale-[0.98]"
        >
          <span>✨</span>
          <span>+ Konsultasi Baru</span>
        </button>
      </div>

      {/* Search Bar for Chat History (Opens Centered Spotlight Modal) */}
      <div className="px-3 pt-3 pb-1">
        <button
          type="button"
          onClick={() => setSearchModalOpen(true)}
          className="w-full flex items-center justify-between px-3 py-2 bg-emerald-50/90 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-xs text-emerald-800/80 dark:text-slate-400 hover:bg-emerald-100/70 dark:hover:bg-slate-700 hover:text-emerald-950 dark:hover:text-white transition-all shadow-2xs group"
        >
          <div className="flex items-center gap-2">
            <span className="text-xs group-hover:scale-110 transition-transform">🔍</span>
            <span className="font-medium">Cari riwayat chat...</span>
          </div>
          <kbd className="px-1.5 py-0.5 text-[10px] font-mono font-bold text-emerald-700 dark:text-slate-400 bg-emerald-100/80 dark:bg-slate-900 border border-emerald-200 dark:border-slate-700 rounded">
            ⌘K
          </kbd>
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1">
        <div className="text-[10px] font-semibold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider px-2 py-1 mb-1 flex items-center justify-between">
          <span>Konsultasi Tersimpan</span>
          <span className="text-[9px] font-mono text-emerald-600 dark:text-slate-400">
            {searchQuery ? `${filteredSessions.length}/${sessions.length}` : `${sessions.length}`}
          </span>
        </div>

        {sessions.length === 0 && (
          <p className="text-[10px] text-emerald-600 dark:text-slate-400 px-2 py-3 text-center">
            Belum ada konsultasi
          </p>
        )}

        {sessions.length > 0 && filteredSessions.length === 0 && (
          <p className="text-[11px] text-emerald-700 dark:text-slate-400 px-2 py-4 text-center">
            Tidak ditemukan riwayat untuk "{searchQuery}"
          </p>
        )}

        {filteredSessions.map((s) => {
          const isActive = activeSessionId === s.session_id;
          const isEditing = editingSessionId === s.session_id;

          return (
            <div
              key={s.session_id}
              onClick={() => !isEditing && onSelectSession(s.session_id)}
              className={`group relative w-full text-left px-3 py-2.5 rounded-xl text-xs transition-all cursor-pointer ${
                isActive
                  ? 'bg-emerald-600/15 dark:bg-emerald-500/20 text-emerald-900 dark:text-emerald-300 border border-emerald-500/30 font-medium'
                  : 'text-emerald-800 dark:text-slate-300 hover:bg-emerald-100/70 dark:hover:bg-slate-800'
              }`}
            >
              {isEditing ? (
                <form
                  onSubmit={(e) => handleSaveRename(s.session_id, e)}
                  onClick={(e) => e.stopPropagation()}
                  className="flex items-center gap-1.5"
                >
                  <input
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    autoFocus
                    onKeyDown={(e) => {
                      if (e.key === 'Escape') setEditingSessionId(null);
                    }}
                    className="flex-1 px-2 py-1 bg-white dark:bg-slate-800 border border-emerald-400 dark:border-emerald-600 rounded-lg text-xs text-emerald-950 dark:text-white focus:outline-none"
                  />
                  <button
                    type="submit"
                    title="Simpan nama"
                    className="p-1 text-emerald-700 dark:text-emerald-400 hover:text-emerald-900 bg-emerald-100 dark:bg-slate-700 rounded-md text-xs font-bold"
                  >
                    ✓
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditingSessionId(null)}
                    title="Batal"
                    className="p-1 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 bg-slate-100 dark:bg-slate-700 rounded-md text-xs"
                  >
                    ✕
                  </button>
                </form>
              ) : (
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0 pr-1">
                    <div className="font-semibold truncate">{s.title || 'Percakapan Tanpa Judul'}</div>
                    <div className="text-[10px] text-emerald-600 dark:text-slate-400 mt-0.5">
                      {new Date(s.created_at).toLocaleDateString('id-ID', {
                        day: 'numeric',
                        month: 'short',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </div>

                  {/* Actions (Rename & Delete) */}
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                    <button
                      type="button"
                      onClick={(e) => startRename(s, e)}
                      title="Ubah judul konsultasi"
                      className="p-1 rounded-md text-slate-600 dark:text-slate-400 hover:text-emerald-700 dark:hover:text-emerald-300 hover:bg-emerald-200/60 dark:hover:bg-slate-700 transition-colors text-[11px]"
                    >
                      ✏️
                    </button>
                    <button
                      type="button"
                      onClick={(e) => openDeleteModal(s, e)}
                      disabled={deletingId === s.session_id}
                      title="Hapus konsultasi"
                      className="p-1 rounded-md text-slate-600 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-100 dark:hover:bg-red-950/50 transition-colors text-[11px]"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Active Clinic Room Strip */}
      {selectedRoom && (
        <div className="px-3 py-2.5 border-t border-emerald-200 dark:border-slate-800 bg-emerald-500/5 dark:bg-emerald-950/20">
          <button
            type="button"
            onClick={onChangeRoom}
            className="w-full text-left group flex items-center gap-2.5 rounded-xl px-3 py-2 hover:bg-emerald-100/70 dark:hover:bg-slate-800 transition-colors"
          >
            <div className="w-8 h-8 rounded-xl bg-emerald-600 text-white flex items-center justify-center text-sm shrink-0 shadow-sm">
              🏥
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-[11px] font-bold text-emerald-900 dark:text-emerald-300 truncate">
                {selectedRoom.room_name}
              </div>
              <div className="text-[10px] text-emerald-600 dark:text-slate-400">
                {selectedRoom.room_code} • {selectedRoom.floor}
              </div>
            </div>
            <span className="text-[10px] text-emerald-500 dark:text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity font-semibold">Ganti</span>
          </button>
        </div>
      )}

      {/* Footer */}
      <div className="p-4 border-t border-emerald-200 dark:border-slate-800 bg-emerald-50/30 dark:bg-slate-900/50">
        <div className="text-[10px] text-emerald-600 dark:text-slate-400 flex items-center justify-between">
          <span>Masuk sebagai <strong className="text-emerald-900 dark:text-slate-200 font-semibold">{userName || 'Pengguna'}</strong></span>
          <span className="uppercase text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 dark:bg-slate-800 text-emerald-800 dark:text-emerald-400">{userRole}</span>
        </div>
      </div>

      {/* Centered Spotlight Chat Search Modal */}
      <ChatSearchModal
        isOpen={searchModalOpen}
        onClose={() => setSearchModalOpen(false)}
        sessions={sessions}
        onSelectSession={onSelectSession}
      />

      {/* Centered Delete Confirmation Modal */}
      <DeleteConfirmModal
        isOpen={!!pendingDeleteSession}
        onClose={() => setPendingDeleteSession(null)}
        onConfirm={handleConfirmDelete}
        title="Hapus Riwayat Konsultasi?"
        itemName={pendingDeleteSession?.title}
        description="Riwayat percakapan klinis ini akan dihapus secara permanen dari basis data sistem dan tidak dapat dipulihkan kembali."
        loading={!!deletingId}
      />
    </aside>
  );
}

