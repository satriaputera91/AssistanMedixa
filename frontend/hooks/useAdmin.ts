'use client';
import { useState, useCallback } from 'react';
import { AdminService, type AdminStats, type UserAdminView, type AuditLogItem, type UsageAnalytics, type SystemMonitoring, type CreateUserInput } from '@/services/admin.service';
import { RAGService, type KnowledgeItem } from '@/services/rag.service';

export function useAdmin() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<UserAdminView[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);
  const [analytics, setAnalytics] = useState<UsageAnalytics | null>(null);
  const [monitoring, setMonitoring] = useState<SystemMonitoring | null>(null);
  const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([]);
  const [creatingUser, setCreatingUser] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadAdminData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [statsData, usersData, logsData, analyticsData, monitoringData, knowledgeData] = await Promise.all([
        AdminService.getStats(),
        AdminService.getUsers(),
        AdminService.getAuditLogs(),
        AdminService.getAnalytics(),
        AdminService.getMonitoring(),
        RAGService.getKnowledgeList(),
      ]);
      setStats(statsData);
      setUsers(usersData);
      setAuditLogs(logsData);
      setAnalytics(analyticsData);
      setMonitoring(monitoringData);
      setKnowledgeItems(knowledgeData.items);
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
    loading,
    error,
    creatingUser,
    loadAdminData,
    toggleUserStatus,
    createUser,
    deleteKnowledge,
  };
}
