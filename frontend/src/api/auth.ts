import apiClient from './client';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserResponse {
  user_id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  is_active: boolean;
  email_verified: boolean;
}

const authApi = {
  login: (credentials: LoginCredentials) => 
    apiClient.post<AuthResponse>('/auth/login', credentials),
    
  register: (data: RegisterData) => 
    apiClient.post<UserResponse>('/auth/register', data),
    
  refreshToken: (refreshToken: string) => 
    apiClient.post<AuthResponse>('/auth/refresh', { refresh_token: refreshToken }),
    
  logout: () => 
    apiClient.post('/auth/logout'),
    
  getCurrentUser: () => 
    apiClient.get<UserResponse>('/users/me'),
};

export default authApi;