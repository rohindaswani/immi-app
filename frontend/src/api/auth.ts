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
    
  // Google OAuth methods
  googleLogin: async () => {
    try {
      // Get the Google auth URL and state token from backend
      const response = await apiClient.get<{ url: string; state: string }>('/auth/google/url');
      
      // Store the state token in session storage
      sessionStorage.setItem('google_oauth_state', response.data.state);
      
      // Redirect to Google's auth page
      window.location.href = response.data.url;
      return Promise.resolve();
    } catch (error) {
      console.error('Failed to get Google auth URL:', error);
      return Promise.reject(error);
    }
  },
  
  // New method to handle Google OAuth callback
  handleGoogleCallback: async (code: string, state: string) => {
    try {
      // Verify the state parameter
      const storedState = sessionStorage.getItem('google_oauth_state');
      if (!storedState || storedState !== state) {
        throw new Error('Invalid state parameter');
      }
      
      // Exchange code for tokens
      const response = await apiClient.get<AuthResponse>('/auth/google/callback', {
        params: { code, state }
      });
      
      // Clean up the stored state
      sessionStorage.removeItem('google_oauth_state');
      
      return response.data;
    } catch (error) {
      console.error('Google OAuth callback failed:', error);
      throw error;
    }
  },
  
  // Handle successful OAuth authentication redirect
  handleAuthSuccess: (params: URLSearchParams): UserResponse => {
    return {
      user_id: params.get('user_id') || '',
      email: params.get('email') || '',
      first_name: params.get('first_name') || null,
      last_name: params.get('last_name') || null,
      is_active: true,
      email_verified: true
    };
  }
};

export default authApi;