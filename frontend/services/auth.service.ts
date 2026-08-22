import { ApiClient } from './api.client';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
  name: string;
  role: 'doctor' | 'admin';
  specialty?: string;
}

export interface UserInfo {
  id: string;
  email: string;
  name: string;
  role: string;
  specialty?: string;
  license_no?: string;
  is_active: boolean;
}

export class AuthService {
  public static async login(credentials: LoginRequest): Promise<TokenResponse> {
    const data = await ApiClient.post<TokenResponse>('/auth/login', credentials);
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user_role', data.role);
      localStorage.setItem('user_name', data.name);
      localStorage.setItem('user_email', data.email);
    }
    return data;
  }

  public static async getMe(): Promise<UserInfo> {
    return ApiClient.get<UserInfo>('/auth/me');
  }

  public static logout(): void {
    if (typeof window !== 'undefined') {
      localStorage.clear();
    }
  }

  public static getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token');
    }
    return null;
  }

  public static getUserRole(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('user_role');
    }
    return null;
  }
}
