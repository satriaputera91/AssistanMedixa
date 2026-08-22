import { ApiClient } from './api.client';

export interface AdminStats {
  total_doctors: number;
  total_admins: number;
  total_chat_sessions: number;
  total_queries_run: number;
  total_gemini_tokens: number;
  gemini_model_active: string;
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
}
