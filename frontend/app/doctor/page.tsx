'use client';
import { useEffect, useState, useCallback } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useAgentChat } from '@/hooks/useAgentChat';
import { AgentService, type ClinicRoom } from '@/services/agent.service';
import Navbar from '@/components/common/Navbar';
import Sidebar from '@/components/chat/Sidebar';
import ChatWindow from '@/components/chat/ChatWindow';
import ClinicRoomPickerModal from '@/components/chat/ClinicRoomPickerModal';
import AppLoadingOverlay from '@/components/common/AppLoadingOverlay';
import ConnectionStatusBanner from '@/components/common/ConnectionStatusBanner';

export default function DoctorPage() {
  const { userName, userRole, loading, logout } = useAuth(['doctor', 'admin']);

  const {
    patients,
    selectedPatient,
    setSelectedPatient,
    sessions,
    activeSessionId,
    messages,
    executing,
    activeNode,
    completedNodes,
    latestSummary,
    loadPatients,
    loadSessions,
    loadSessionMessages,
    startNewSession,
    renameSession,
    deleteSession,
    sendMessage,
    sendAudio,
    reviewSOA,
    confirmSOA,
    commitTempSOAP,
    updateTempSOAP,
  } = useAgentChat();

  // Clinic room state
  const [clinicRooms, setClinicRooms] = useState<ClinicRoom[]>([]);
  const [selectedRoom, setSelectedRoom] = useState<ClinicRoom | null>(null);
  const [roomPickerOpen, setRoomPickerOpen] = useState(false);
  const [roomLoaded, setRoomLoaded] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);

  const loadClinicRooms = useCallback(async () => {
    try {
      const [rooms, selected] = await Promise.all([
        AgentService.getClinicRooms(),
        AgentService.getSelectedRoom(),
      ]);
      setClinicRooms(rooms);
      if (selected.selected_room) {
        setSelectedRoom(selected.selected_room);
        loadPatients(selected.selected_room.room_id);
      } else {
        // First time — no room selected, force popup
        setRoomPickerOpen(true);
        loadPatients();
      }
    } catch (e) {
      console.error('Failed to load clinic rooms:', e);
    } finally {
      setRoomLoaded(true);
    }
  }, [loadPatients]);

  const handleSelectRoom = async (room: ClinicRoom) => {
    try {
      await AgentService.selectClinicRoom(room.room_id);
      setSelectedRoom(room);
      setRoomPickerOpen(false);
      loadPatients(room.room_id);
    } catch (e) {
      console.error('Failed to select room:', e);
    }
  };

  const handleRetryInit = async () => {
    setIsRetrying(true);
    try {
      await Promise.all([loadSessions(), loadClinicRooms()]);
    } finally {
      setIsRetrying(false);
    }
  };

  useEffect(() => {
    if (!loading) {
      loadSessions();
      loadClinicRooms();
    }
  }, [loading, loadSessions, loadClinicRooms]);

  if (loading || (!roomLoaded && clinicRooms.length === 0)) {
    return (
      <AppLoadingOverlay
        message="Mempersiapkan Ruang Kerja Medis & Layanan AI..."
        subMessage="Menghubungkan ke layanan poliklinik & rekam medis..."
        onRetry={handleRetryInit}
        isRetrying={isRetrying}
      />
    );
  }

  return (
    <div className="flex flex-col h-screen bg-emerald-50 dark:bg-slate-950 text-emerald-950 dark:text-slate-100 overflow-hidden transition-colors relative">
      <ConnectionStatusBanner />
      <Navbar userName={userName} userRole={userRole} onLogout={logout} activePage="doctor" />

      {/* Clinic Room Picker Modal (shown on first login or when user changes room) */}
      <ClinicRoomPickerModal
        isOpen={roomPickerOpen}
        rooms={clinicRooms}
        selectedRoomId={selectedRoom?.room_id}
        onSelect={handleSelectRoom}
        onClose={selectedRoom ? () => setRoomPickerOpen(false) : undefined}
        required={!selectedRoom}
      />

      <div className="flex flex-1 min-h-0">
        <Sidebar
          patients={patients}
          selectedPatient={selectedPatient}
          onSelectPatient={setSelectedPatient}
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={loadSessionMessages}
          onNewSession={startNewSession}
          onRenameSession={renameSession}
          onDeleteSession={deleteSession}
          userName={userName}
          userRole={userRole}
          selectedRoom={selectedRoom}
          onChangeRoom={() => setRoomPickerOpen(true)}
        />

        <main className="flex-1 flex flex-col min-h-0 overflow-hidden">
          <ChatWindow
            messages={messages}
            executing={executing}
            onSend={sendMessage}
            onSendAudio={sendAudio}
            onReviewSOA={reviewSOA}
            onConfirmSOA={confirmSOA}
            onCommitTempSOAP={commitTempSOAP}
            onUpdateTempSOAP={updateTempSOAP}
            patients={patients}
            selectedPatient={selectedPatient}
            onSelectPatient={setSelectedPatient}
            sessionId={activeSessionId}
            activeNode={activeNode}
            completedNodes={completedNodes}
            latestSummary={latestSummary}
          />
        </main>
      </div>
    </div>
  );
}
