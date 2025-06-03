
import api from './api';
import { LoginRequest, RegisterRequest, AuthResponse, User } from '../types/auth.types';

export const authService = {
  async login(credentials: LoginRequest): Promise<{ auth: AuthResponse; user: User }> {
    const authResponse = await api.post<AuthResponse>('/auth/login', credentials);
    
    // Get user profile after login
    localStorage.setItem('access_token', authResponse.data.access_token);
    localStorage.setItem('refresh_token', authResponse.data.refresh_token);
    
    const userResponse = await api.get<User>('/users/me');
    
    return {
      auth: authResponse.data,
      user: userResponse.data
    };
  },

  async register(userData: RegisterRequest): Promise<User> {
    const response = await api.post<User>('/auth/register', userData);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/users/me');
    return response.data;
  },

  async updateProfile(userData: Partial<User>): Promise<User> {
    const response = await api.put<User>('/users/me', userData);
    return response.data;
  },

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }
};
