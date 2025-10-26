import axios from 'axios';
import type { AxiosInstance } from 'axios';
import { API_CONFIG } from './config';

export class ApiError extends Error {
  status?: number;
  data?: any;

  constructor(message: string, status?: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

class AxiosApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for authentication
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        if (typeof window !== 'undefined') {
          // Try to get token from direct storage first (faster)
          let access_token = localStorage.getItem('access_token');
          
          // Fallback to auth_tokens object
          if (!access_token) {
            const tokens = localStorage.getItem('auth_tokens');
            if (tokens) {
              try {
                const parsedTokens = JSON.parse(tokens);
                access_token = parsedTokens.access_token;
              } catch (error) {
                console.error('Error parsing auth tokens:', error);
              }
            }
          }
          
          if (access_token) {
            config.headers.Authorization = `Bearer ${access_token}`;
          }
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const resp = error.response;
        
        // Handle 401 Unauthorized - token expired or invalid
        if (resp?.status === 401) {
          if (typeof window !== 'undefined') {
            // Try to refresh token
            try {
              const tokens = localStorage.getItem('auth_tokens');
              if (tokens) {
                const { refresh_token } = JSON.parse(tokens);
                if (refresh_token) {
                  // Token refresh is not implemented yet, just logout user
                  throw error;
                }
              }
            } catch (refreshError) {
              console.error('Token refresh failed:', refreshError);
              // Clear invalid tokens
              localStorage.removeItem('access_token');
              localStorage.removeItem('token_type');
              localStorage.removeItem('auth_tokens');
              localStorage.removeItem('current_user');
              // Redirect to login or emit auth error
              window.dispatchEvent(new CustomEvent('auth:expired'));
            }
          }
        }
        
        if (resp) {
          const message = resp.data?.detail || resp.data?.message || resp.statusText || 'API error';
          return Promise.reject(new ApiError(message, resp.status, resp.data));
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    const response = await this.client.get<T>(endpoint, { params });
    return response.data as T;
  }

  async post<T>(endpoint: string, data?: any, config?: any): Promise<T> {
    const response = await this.client.post<T>(endpoint, data, config);
    return response.data as T;
  }

  async put<T>(endpoint: string, data?: any, config?: any): Promise<T> {
    const response = await this.client.put<T>(endpoint, data, config);
    return response.data as T;
  }

  async delete<T>(endpoint: string): Promise<T> {
    const response = await this.client.delete<T>(endpoint);
    return response.data as T;
  }
}

export const apiClient = new AxiosApiClient();
