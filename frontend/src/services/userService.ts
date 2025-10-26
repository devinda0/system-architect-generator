import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';

// User Types
export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  profile?: {
    bio?: string;
    avatar_url?: string;
    preferences?: Record<string, any>;
  };
}

export interface UserCreateRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  profile?: {
    bio?: string;
    avatar_url?: string;
    preferences?: Record<string, any>;
  };
}

export interface UserUpdateRequest {
  username?: string;
  email?: string;
  full_name?: string;
  profile?: {
    bio?: string;
    avatar_url?: string;
    preferences?: Record<string, any>;
  };
}

export interface UserResponse {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  profile?: {
    bio?: string;
    avatar_url?: string;
    preferences?: Record<string, any>;
  };
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
  expires_in?: number;
  refresh_token?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  user: UserResponse;
  tokens: AuthTokens;
}

class UserService {
  private currentUser: UserResponse | null = null;
  private tokens: AuthTokens | null = null;

  /**
   * Register a new user
   */
  async register(request: UserCreateRequest): Promise<UserResponse> {
    try {
      const response = await apiClient.post<UserResponse>(
        API_ENDPOINTS.AUTH_REGISTER,
        request
      );
      return response;
    } catch (error) {
      console.error('User registration error:', error);
      throw error;
    }
  }

  /**
   * Login user
   */
  async login(request: LoginRequest): Promise<LoginResponse> {
    try {
      // Convert to URLSearchParams for OAuth2PasswordRequestForm
      const formData = new URLSearchParams();
      formData.append('username', request.username);
      formData.append('password', request.password);
      
      const response = await apiClient.post<LoginResponse>(
        API_ENDPOINTS.AUTH_LOGIN,
        formData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );
      
      this.currentUser = response.user;
      this.tokens = response.tokens;
      
      // Store tokens in localStorage for persistence
      if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', response.tokens.access_token);
        localStorage.setItem('token_type', response.tokens.token_type);
        localStorage.setItem('auth_tokens', JSON.stringify(this.tokens));
        localStorage.setItem('current_user', JSON.stringify(this.currentUser));
      }
      
      return response;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      // Call logout endpoint if available
      await apiClient.post(API_ENDPOINTS.AUTH_LOGOUT);
    } catch (error) {
      console.error('Logout error (continuing anyway):', error);
    } finally {
      this.currentUser = null;
      this.tokens = null;
      
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('token_type');
        localStorage.removeItem('auth_tokens');
        localStorage.removeItem('current_user');
      }
    }
  }

  /**
   * Get current user from memory or localStorage
   */
  getCurrentUser(): UserResponse | null {
    if (this.currentUser) {
      return this.currentUser;
    }
    
    // Try to restore from localStorage
    if (typeof window !== 'undefined') {
      const storedUser = localStorage.getItem('current_user');
      if (storedUser) {
        this.currentUser = JSON.parse(storedUser);
        return this.currentUser;
      }
    }
    
    return null;
  }

  /**
   * Fetch current user from API
   */
  async fetchCurrentUser(): Promise<UserResponse> {
    try {
      const response = await apiClient.get<UserResponse>(
        API_ENDPOINTS.AUTH_ME
      );
      this.currentUser = response;
      if (typeof window !== 'undefined') {
        localStorage.setItem('current_user', JSON.stringify(this.currentUser));
      }
      return response;
    } catch (error) {
      console.error('Fetch current user error:', error);
      throw error;
    }
  }

  /**
   * Get current auth tokens
   */
  getTokens(): AuthTokens | null {
    if (this.tokens) {
      return this.tokens;
    }
    
    // Try to restore from localStorage
    if (typeof window !== 'undefined') {
      const storedTokens = localStorage.getItem('auth_tokens');
      if (storedTokens) {
        this.tokens = JSON.parse(storedTokens);
        return this.tokens;
      }
    }
    
    return null;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.getCurrentUser() !== null && this.getTokens() !== null;
  }

  /**
   * Get user profile by ID
   */
  async getUserById(userId: string): Promise<UserResponse> {
    try {
      const response = await apiClient.get<UserResponse>(
        API_ENDPOINTS.USER_BY_ID(userId)
      );
      return response;
    } catch (error) {
      console.error('Get user by ID error:', error);
      throw error;
    }
  }

  /**
   * Update user profile
   */
  async updateUser(userId: string, request: UserUpdateRequest): Promise<UserResponse> {
    try {
      const response = await apiClient.put<UserResponse>(
        API_ENDPOINTS.USER_BY_ID(userId),
        request
      );
      
      // Update current user if it's the same user
      if (this.currentUser && this.currentUser.id === userId) {
        this.currentUser = response;
        if (typeof window !== 'undefined') {
          localStorage.setItem('current_user', JSON.stringify(this.currentUser));
        }
      }
      
      return response;
    } catch (error) {
      console.error('Update user error:', error);
      throw error;
    }
  }

  /**
   * Delete user account
   */
  async deleteUser(userId: string): Promise<{ message: string }> {
    try {
      const response = await apiClient.delete<{ message: string }>(
        API_ENDPOINTS.USER_BY_ID(userId)
      );
      
      // If deleting current user, logout
      if (this.currentUser && this.currentUser.id === userId) {
        await this.logout();
      }
      
      return response;
    } catch (error) {
      console.error('Delete user error:', error);
      throw error;
    }
  }

  /**
   * Refresh authentication tokens
   */
  async refreshTokens(): Promise<AuthTokens> {
    try {
      const currentTokens = this.getTokens();
      if (!currentTokens?.refresh_token) {
        throw new Error('No refresh token available');
      }

      const response = await apiClient.post<AuthTokens>(
        API_ENDPOINTS.AUTH_REFRESH,
        { refresh_token: currentTokens.refresh_token }
      );
      
      this.tokens = response;
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_tokens', JSON.stringify(this.tokens));
      }
      
      return response;
    } catch (error) {
      console.error('Refresh tokens error:', error);
      // If refresh fails, logout user
      await this.logout();
      throw error;
    }
  }
}

export const userService = new UserService();