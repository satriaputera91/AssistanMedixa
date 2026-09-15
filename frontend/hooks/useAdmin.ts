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
  type MCPConfig,
  type UpdateMCPConfigInput,
  type MCPTool,
  type CreateCustomMCPToolInput,
  type UpdateMCPToolInput,
  type MCPTestConnectionResponse,
  type MCPTestRunToolInput,
  type MCPTestRunToolResponse,
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
  const [mcpConfig, setMcpConfig] = useState<MCPConfig | null>(null);
  const [mcpTools, setMcpTools] = useState<MCPTool[]>([]);
  const [creatingUser, setCreatingUser] = useState(false);
  const [savingClinicRoom, setSavingClinicRoom] = useState(false);
  const [savingMcpConfig, setSavingMcpConfig] = useState(false);
  const [savingMcpTool, setSavingMcpTool] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
  const [testingTool, setTestingTool] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadAdminData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [statsData, usersData, logsData, analyticsData, monitoringData, knowledgeData, roomsData, mcpConfigData, mcpToolsData] = await Promise.all([
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
        AdminService.getMCPConfig().catch((e) => {
          console.error('Failed to load MCP config:', e);
          return null;
        }),
        AdminService.getMCPTools().catch((e) => {
          console.error('Failed to load MCP tools:', e);
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
      setMcpConfig(mcpConfigData);
      setMcpTools(mcpToolsData);
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

  // ── MCP Operations ────────────────────────────────────────────────

  const updateMCPConfig = useCallback(async (input: UpdateMCPConfigInput) => {
    setSavingMcpConfig(true);
    try {
      const updated = await AdminService.updateMCPConfig(input);
      setMcpConfig(updated);
      return updated;
    } catch (e: any) {
      console.error('Failed to update MCP config:', e);
      setError(e.message || 'Konfigurasi MCP Server gagal disimpan.');
      throw e;
    } finally {
      setSavingMcpConfig(false);
    }
  }, []);

  const testMCPConnection = useCallback(async (): Promise<MCPTestConnectionResponse> => {
    setTestingConnection(true);
    try {
      const res = await AdminService.testMCPConnection();
      const cfg = await AdminService.getMCPConfig();
      setMcpConfig(cfg);
      return res;
    } catch (e: any) {
      console.error('Failed to test MCP connection:', e);
      throw e;
    } finally {
      setTestingConnection(false);
    }
  }, []);

  const createMCPTool = useCallback(async (input: CreateCustomMCPToolInput) => {
    setSavingMcpTool(true);
    try {
      const tool = await AdminService.createMCPTool(input);
      const tools = await AdminService.getMCPTools();
      setMcpTools(tools);
      return tool;
    } catch (e: any) {
      console.error('Failed to create MCP tool:', e);
      throw e;
    } finally {
      setSavingMcpTool(false);
    }
  }, []);

  const updateMCPTool = useCallback(async (toolName: string, input: UpdateMCPToolInput) => {
    setSavingMcpTool(true);
    try {
      const tool = await AdminService.updateMCPTool(toolName, input);
      const tools = await AdminService.getMCPTools();
      setMcpTools(tools);
      return tool;
    } catch (e: any) {
      console.error('Failed to update MCP tool:', e);
      throw e;
    } finally {
      setSavingMcpTool(false);
    }
  }, []);

  const toggleMCPToolStatus = useCallback(async (toolName: string) => {
    try {
      const toggled = await AdminService.toggleMCPToolStatus(toolName);
      setMcpTools(prev => prev.map(t => t.name === toolName ? toggled : t));
      return toggled;
    } catch (e: any) {
      console.error('Failed to toggle MCP tool:', e);
      throw e;
    }
  }, []);

  const deleteMCPTool = useCallback(async (toolName: string) => {
    try {
      await AdminService.deleteMCPTool(toolName);
      setMcpTools(prev => prev.filter(t => t.name !== toolName));
      return true;
    } catch (e: any) {
      console.error('Failed to delete MCP tool:', e);
      throw e;
    }
  }, []);

  const testRunMCPTool = useCallback(async (input: MCPTestRunToolInput): Promise<MCPTestRunToolResponse> => {
    setTestingTool(true);
    try {
      const res = await AdminService.testRunMCPTool(input);
      const tools = await AdminService.getMCPTools();
      setMcpTools(tools);
      return res;
    } catch (e: any) {
      console.error('Failed to test run MCP tool:', e);
      throw e;
    } finally {
      setTestingTool(false);
    }
  }, []);

  return {
    stats,
    users,
    auditLogs,
    analytics,
    monitoring,
    knowledgeItems,
    clinicRooms,
    mcpConfig,
    mcpTools,
    loading,
    error,
    creatingUser,
    savingClinicRoom,
    savingMcpConfig,
    savingMcpTool,
    testingConnection,
    testingTool,
    loadAdminData,
    toggleUserStatus,
    createUser,
    createClinicRoom,
    updateClinicRoom,
    deleteClinicRoom,
    toggleClinicRoomStatus,
    deleteKnowledge,
    updateMCPConfig,
    testMCPConnection,
    createMCPTool,
    updateMCPTool,
    toggleMCPToolStatus,
    deleteMCPTool,
    testRunMCPTool,
  };
}

