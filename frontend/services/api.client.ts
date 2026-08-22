const API_BASE_URL = '/api/v1';

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
    public readonly requestId?: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class ApiClient {
  private static getHeaders(isMultipart = false): Record<string, string> {
    const headers: Record<string, string> = {};
    if (!isMultipart) {
      headers['Content-Type'] = 'application/json';
    }
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  private static async request<T>(endpoint: string, options: RequestInit, isMultipart = false): Promise<T> {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 120_000);
    try {
      const mergedHeaders = {
        ...this.getHeaders(isMultipart),
        ...((options.headers as Record<string, string>) || {}),
      };

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: mergedHeaders,
        signal: controller.signal,
      });

      if (response.status === 401 && typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_role');
        localStorage.removeItem('user_name');
        localStorage.removeItem('user_email');
        if (!window.location.pathname.startsWith('/login')) {
          window.location.assign('/login');
        }
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        if (response.status >= 500) {
          throw new ApiError(
            error.detail || 'Terjadi kendala teknis pada server (Error 500). Silakan coba beberapa saat lagi.',
            response.status,
            error.request_id,
          );
        }
        throw new ApiError(
          error.detail || `Permintaan gagal (HTTP ${response.status}). Silakan coba beberapa saat lagi.`,
          response.status,
          error.request_id,
        );
      }
      return response.json() as Promise<T>;
    } catch (error) {
      if (error instanceof ApiError) throw error;
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new ApiError('Waktu permintaan habis. Silakan coba beberapa saat lagi.');
      }
      throw new ApiError('Tidak dapat terhubung ke server. Silakan periksa koneksi Anda dan coba beberapa saat lagi.');
    } finally {
      window.clearTimeout(timeout);
    }
  }

  public static get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  public static async post<T>(endpoint: string, body?: any, isMultipart = false): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: isMultipart ? body : JSON.stringify(body),
    }, isMultipart);
  }

  public static async put<T>(endpoint: string, body?: any): Promise<T> {
    return this.request<T>(endpoint, { method: 'PUT', body: JSON.stringify(body) });
  }

  public static async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}
