import { ApiClient } from './api.client';

export interface AdminStats {
  total_doctors: number;
  total_admins: number;
  total_chat_sessions: number;
  total_queries_run: number;
  total_gemini_tokens: number;
  gemini_model_active: string;
  total_clinic_rooms?: number;
}

export interface UserAdminView {
  id: string;
  email: string;
  name: string;
  role: string;
  specialty?: string;
  license_no?: string;
  is_active: boolean;
  created_at: string;
}

export interface AuditLogItem {
  id: string;
  timestamp: string;
  user_id: string;
  doctor_name: string;
  action: string;
  details: string;
  tokens_used: number;
  status: string;
}

export interface UsageDailyPoint {
  date: string;
  requests: number;
  tokens: number;
}

export interface UsageAnalytics {
  total_requests: number;
  total_tokens: number;
  average_tokens_per_request: number;
  audio_requests: number;
  soa_revisions: number;
  requests_by_day: UsageDailyPoint[];
  top_actions: { action: string; count: number }[];
}

export interface ServiceHealth {
  name: string;
  status: 'healthy' | 'warning' | 'unhealthy';
  detail: string;
}

export interface SystemMonitoring {
  services: ServiceHealth[];
  checked_at: string;
}

export interface CreateUserInput {
  name: string;
  email: string;
  password: string;
  role: 'doctor' | 'admin';
  specialty?: string;
  license_no?: string;
}

export interface ClinicRoomAssignedDoctor {
  id: string;
  name: string;
  email: string;
  specialty?: string;
  license_no?: string;
}

export interface ClinicRoomAdmin {
  room_id: string;
  room_name: string;
  room_code: string;
  floor: string;
  building: string;
  specialty: string;
  status: 'active' | 'inactive' | 'maintenance';
  description?: string;
  operational_hours?: string;
  assigned_doctors: ClinicRoomAssignedDoctor[];
  created_at?: string;
  updated_at?: string;
}

export interface CreateClinicRoomInput {
  room_id?: string;
  room_name: string;
  room_code: string;
  floor: string;
  building: string;
  specialty: string;
  status?: 'active' | 'inactive' | 'maintenance';
  description?: string;
  operational_hours?: string;
}

export interface UpdateClinicRoomInput {
  room_name?: string;
  room_code?: string;
  floor?: string;
  building?: string;
  specialty?: string;
  status?: 'active' | 'inactive' | 'maintenance';
  description?: string;
  operational_hours?: string;
}

export class AdminService {
  public static async getStats(): Promise<AdminStats> {
    return ApiClient.get<AdminStats>('/admin/stats');
  }

  public static async getUsers(): Promise<UserAdminView[]> {
    return ApiClient.get<UserAdminView[]>('/admin/users');
  }

  public static async createUser(input: CreateUserInput): Promise<UserAdminView> {
    return ApiClient.post<UserAdminView>('/admin/users', input);
  }

  public static async toggleUserStatus(userId: string): Promise<any> {
    return ApiClient.post(`/admin/users/${userId}/toggle-status`);
  }

  public static async getAuditLogs(): Promise<AuditLogItem[]> {
    return ApiClient.get<AuditLogItem[]>('/admin/audit-logs');
  }

  public static async getAnalytics(): Promise<UsageAnalytics> {
    return ApiClient.get<UsageAnalytics>('/admin/analytics');
  }

  public static async getMonitoring(): Promise<SystemMonitoring> {
    return ApiClient.get<SystemMonitoring>('/admin/monitoring');
  }

  // ── Clinic Room / Poli Management Methods ──────────────────────────

  public static async getClinicRooms(): Promise<ClinicRoomAdmin[]> {
    return ApiClient.get<ClinicRoomAdmin[]>('/admin/clinic-rooms');
  }

  public static async getClinicRoom(roomId: string): Promise<ClinicRoomAdmin> {
    return ApiClient.get<ClinicRoomAdmin>(`/admin/clinic-rooms/${roomId}`);
  }

  public static async createClinicRoom(input: CreateClinicRoomInput): Promise<ClinicRoomAdmin> {
    return ApiClient.post<ClinicRoomAdmin>('/admin/clinic-rooms', input);
  }

  public static async updateClinicRoom(roomId: string, input: UpdateClinicRoomInput): Promise<ClinicRoomAdmin> {
    return ApiClient.put<ClinicRoomAdmin>(`/admin/clinic-rooms/${roomId}`, input);
  }

  public static async deleteClinicRoom(roomId: string): Promise<{ status: string; message: string; room_id: string }> {
    return ApiClient.delete<{ status: string; message: string; room_id: string }>(`/admin/clinic-rooms/${roomId}`);
  }

  public static async toggleClinicRoomStatus(roomId: string): Promise<ClinicRoomAdmin> {
    return ApiClient.post<ClinicRoomAdmin>(`/admin/clinic-rooms/${roomId}/toggle-status`, {});
  }

  // ── MCP Dynamic Configuration & Tools Methods ──────────────────────

  public static async getMCPConfig(): Promise<MCPConfig> {
    return ApiClient.get<MCPConfig>('/admin/mcp/config');
  }

  public static async updateMCPConfig(input: UpdateMCPConfigInput): Promise<MCPConfig> {
    return ApiClient.put<MCPConfig>('/admin/mcp/config', input);
  }

  public static async testMCPConnection(): Promise<MCPTestConnectionResponse> {
    return ApiClient.post<MCPTestConnectionResponse>('/admin/mcp/test-connection', {});
  }

  public static async getMCPTools(): Promise<MCPTool[]> {
    return ApiClient.get<MCPTool[]>('/admin/mcp/tools');
  }

  public static async getMCPTool(toolName: string): Promise<MCPTool> {
    return ApiClient.get<MCPTool>(`/admin/mcp/tools/${encodeURIComponent(toolName)}`);
  }

  public static async createMCPTool(input: CreateCustomMCPToolInput): Promise<MCPTool> {
    return ApiClient.post<MCPTool>('/admin/mcp/tools', input);
  }

  public static async updateMCPTool(toolName: string, input: UpdateMCPToolInput): Promise<MCPTool> {
    return ApiClient.put<MCPTool>(`/admin/mcp/tools/${encodeURIComponent(toolName)}`, input);
  }

  public static async toggleMCPToolStatus(toolName: string): Promise<MCPTool> {
    return ApiClient.post<MCPTool>(`/admin/mcp/tools/${encodeURIComponent(toolName)}/toggle`, {});
  }

  public static async deleteMCPTool(toolName: string): Promise<{ status: string; message: string; tool_name: string }> {
    return ApiClient.delete<{ status: string; message: string; tool_name: string }>(`/admin/mcp/tools/${encodeURIComponent(toolName)}`);
  }

  public static async testRunMCPTool(input: MCPTestRunToolInput): Promise<MCPTestRunToolResponse> {
    return ApiClient.post<MCPTestRunToolResponse>('/admin/mcp/tools/test-run', input);
  }
}

// ── MCP Interfaces ───────────────────────────────────────────────────

export interface MCPConfig {
  server_name: string;
  protocol_version: string;
  mode: 'mock' | 'live' | 'hybrid' | string;
  endpoint_url: string;
  auth_type: 'bearer' | 'api_key' | 'none' | string;
  auth_token?: string;
  timeout_seconds: number;
  retry_attempts: number;
  enable_audit_logging: boolean;
  auto_sync_enabled: boolean;
  custom_headers?: Record<string, any>;
  status: string;
  latency_ms?: number;
  last_health_check?: string;
  updated_at?: string;
}

export interface UpdateMCPConfigInput {
  server_name?: string;
  protocol_version?: string;
  mode?: string;
  endpoint_url?: string;
  auth_type?: string;
  auth_token?: string;
  timeout_seconds?: number;
  retry_attempts?: number;
  enable_audit_logging?: boolean;
  auto_sync_enabled?: boolean;
  custom_headers?: Record<string, any>;
}

export interface MCPTool {
  name: string;
  display_name: string;
  description: string;
  category: string;
  is_enabled: boolean;
  is_builtin: boolean;
  input_schema: Record<string, any>;
  custom_endpoint?: string;
  mock_response?: Record<string, any>;
  execution_count: number;
  last_executed_at?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CreateCustomMCPToolInput {
  name: string;
  display_name: string;
  description: string;
  category?: string;
  is_enabled?: boolean;
  input_schema?: Record<string, any>;
  custom_endpoint?: string;
  mock_response?: Record<string, any>;
}

export interface UpdateMCPToolInput {
  display_name?: string;
  description?: string;
  category?: string;
  is_enabled?: boolean;
  input_schema?: Record<string, any>;
  custom_endpoint?: string;
  mock_response?: Record<string, any>;
}

export interface MCPTestConnectionResponse {
  status: 'success' | 'warning' | 'error' | string;
  message: string;
  server_name: string;
  mode: string;
  endpoint_url: string;
  latency_ms: number;
  active_tools_count: number;
  checked_at: string;
}

export interface MCPTestRunToolInput {
  tool_name: string;
  arguments?: Record<string, any>;
}

export interface MCPTestRunToolResponse {
  tool_name: string;
  status: string;
  execution_mode: string;
  latency_ms: number;
  result: Record<string, any>;
  timestamp: string;
}
