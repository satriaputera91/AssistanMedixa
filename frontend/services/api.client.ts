const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
export const API_BASE_URL = `${BACKEND_URL}/api/v1`;

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
  public static getToken(): string | null {
    return typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  }

  private static getHeaders(isMultipart = false): Record<string, string> {
    const headers: Record<string, string> = {};
    if (!isMultipart) {
      headers['Content-Type'] = 'application/json';
    }
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  private static async request<T>(
    endpoint: string,
    options: RequestInit,
    isMultipart = false,
    retries = 2
  ): Promise<T> {
    const isGet = !options.method || options.method === 'GET';
    let lastError: any = null;

    for (let attempt = 0; attempt <= (isGet ? retries : 0); attempt++) {
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
          // If 502/503/504 Bad Gateway / Service Unavailable from proxy during reboot, retry
          if ([502, 503, 504].includes(response.status) && isGet && attempt < retries) {
            await new Promise((r) => setTimeout(r, 1000 * (attempt + 1)));
            continue;
          }

          const error = await response.json().catch(() => ({}));
          if (response.status >= 500) {
            if (typeof window !== 'undefined') {
              window.dispatchEvent(
                new CustomEvent('api_connection_error', {
                  detail: {
                    message: 'Terjadi kendala pada server backend (Error 500). Menghubungkan kembali...',
                    status: response.status,
                  },
                })
              );
            }
            throw new ApiError(
              error.detail || 'Terjadi kendala teknis pada server (Error 500). Silakan coba beberapa saat lagi.',
              response.status,
              error.request_id
            );
          }
          throw new ApiError(
            error.detail || `Permintaan gagal (HTTP ${response.status}). Silakan coba beberapa saat lagi.`,
            response.status,
            error.request_id
          );
        }

        // Successfully received response -> notify connection restored if previously disconnected
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('api_connection_restored'));
        }

        return (await response.json()) as Promise<T>;
      } catch (error) {
        lastError = error;
        if (error instanceof ApiError && error.status && error.status < 500) {
          throw error;
        }

        // If network failure / fetch error during startup, wait and retry for GET requests
        if (isGet && attempt < retries) {
          await new Promise((r) => setTimeout(r, 1000 * (attempt + 1)));
          continue;
        }

        if (typeof window !== 'undefined') {
          window.dispatchEvent(
            new CustomEvent('api_connection_error', {
              detail: {
                message: 'Tidak dapat terhubung ke server backend (Port 8000). Server mungkin sedang dimulai ulang.',
              },
            })
          );
        }

        if (error instanceof ApiError) throw error;
        if (error instanceof DOMException && error.name === 'AbortError') {
          throw new ApiError('Waktu permintaan habis. Silakan coba beberapa saat lagi.');
        }
        throw new ApiError('Tidak dapat terhubung ke server. Silakan periksa koneksi Anda dan coba beberapa saat lagi.');
      } finally {
        window.clearTimeout(timeout);
      }
    }

    throw lastError || new ApiError('Gagal terhubung ke layanan server.');
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
