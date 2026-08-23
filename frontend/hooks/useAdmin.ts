'use client';

import { useState, useCallback } from 'react';
import { 
  AdminService, 
  type AdminStats, 
  type UserAdminView, 
  type AuditLogItem, 
  type UsageAnalytics, 
  type SystemMonitoring, 
  type CreateUserInput,
  type ClinicRoomAdmin,
  type CreateClinicRoomInput,
  type UpdateClinicRoomInput,
} from '@/services/admin.service';
import { RAGService, type KnowledgeItem } from '@/services/rag.service';

export function useAdmin() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<UserAdminView[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);
  const [analytics, setAnalytics] = useState<UsageAnalytics | null>(null);
  const [monitoring, setMonitoring] = useState<SystemMonitoring | null>(null);
  const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([]);
  const [clinicRooms, setClinicRooms] = useState<ClinicRoomAdmin[]>([]);
  const [creatingUser, setCreatingUser] = useState(false);
  const [savingClinicRoom, setSavingClinicRoom] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadAdminData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [statsData, usersData, logsData, analyticsData, monitoringData, knowledgeData, roomsData] = await Promise.all([
        AdminService.getStats(),
        AdminService.getUsers(),
        AdminService.getAuditLogs(),
        AdminService.getAnalytics(),
        AdminService.getMonitoring(),
        RAGService.getKnowledgeList(),
        AdminService.getClinicRooms().catch((e) => {
          console.error('Failed to load clinic rooms:', e);
          return [];
        }),
      ]);
      setStats(statsData);
      setUsers(usersData);
      setAuditLogs(logsData);
      setAnalytics(analyticsData);
      setMonitoring(monitoringData);
      setKnowledgeItems(knowledgeData.items);
      setClinicRooms(roomsData);
    } catch (e: any) {
      console.error('Failed to load admin data:', e);
      setError(e.message || 'Data admin tidak dapat dimuat.');
    } finally {
      setLoading(false);
    }
  }, []);

  const toggleUserStatus = useCallback(async (userId: string) => {
    try {
      await AdminService.toggleUserStatus(userId);
      await loadAdminData();
    } catch (e: any) {
      console.error('Failed to toggle user:', e);
      setError(e.message || 'Status pengguna tidak dapat diperbarui.');
    }
  }, [loadAdminData]);

  const createUser = useCallback(async (input: CreateUserInput) => {
    setCreatingUser(true);
    try {
      await AdminService.createUser(input);
      await loadAdminData();
      return true;
    } catch (e: any) {
      console.error('Failed to create user:', e);
      setError(e.message || 'Pengguna tidak dapat dibuat.');
      return false;
    } finally {
      setCreatingUser(false);
    }
  }, [loadAdminData]);

  const createClinicRoom = useCallback(async (input: CreateClinicRoomInput) => {
    setSavingClinicRoom(true);
    try {
      await AdminService.createClinicRoom(input);
      await loadAdminData();
      return true;
    } catch (e: any) {
      console.error('Failed to create clinic room:', e);
      setError(e.message || 'Ruangan poli tidak dapat dibuat.');
      return false;
    } finally {
      setSavingClinicRoom(false);
    }
  }, [loadAdminData]);

  const updateClinicRoom = useCallback(async (roomId: string, input: UpdateClinicRoomInput) => {
    setSavingClinicRoom(true);
    try {
      await AdminService.updateClinicRoom(roomId, input);
      await loadAdminData();
      return true;
    } catch (e: any) {
      console.error('Failed to update clinic room:', e);
      setError(e.message || 'Ruangan poli tidak dapat diperbarui.');
      return false;
    } finally {
      setSavingClinicRoom(false);
    }
  }, [loadAdminData]);

  const deleteClinicRoom = useCallback(async (roomId: string) => {
    try {
      await AdminService.deleteClinicRoom(roomId);
      await loadAdminData();
      return true;
    } catch (e: any) {
      console.error('Failed to delete clinic room:', e);
      setError(e.message || 'Ruangan poli tidak dapat dihapus.');
      return false;
    }
  }, [loadAdminData]);

  const toggleClinicRoomStatus = useCallback(async (roomId: string) => {
    try {
      await AdminService.toggleClinicRoomStatus(roomId);
      await loadAdminData();
      return true;
    } catch (e: any) {
      console.error('Failed to toggle clinic room status:', e);
      setError(e.message || 'Status ruangan poli tidak dapat diubah.');
      return false;
    }
  }, [loadAdminData]);

  const deleteKnowledge = useCallback(async (itemId: string) => {
    try {
      await RAGService.deleteKnowledge(itemId);
      await loadAdminData();
    } catch (e: any) {
      console.error('Failed to delete knowledge:', e);
      setError(e.message || 'Pengetahuan tidak dapat dihapus.');
    }
  }, [loadAdminData]);

  return {
    stats,
    users,
    auditLogs,
    analytics,
    monitoring,
    knowledgeItems,
    clinicRooms,
    loading,
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
    deleteKnowledge,
  };
}

