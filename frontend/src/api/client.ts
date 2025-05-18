import axios from 'axios';

const BASE_URL = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}`;

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for sending/receiving cookies
});

// Add request interceptor for API requests
apiClient.interceptors.request.use(
  (config) => {
    // No need to add Authorization header as we're using HTTP-only cookies
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Handle token expiration
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Call the token refresh endpoint
        await axios.post(`${BASE_URL}/auth/token/refresh`, {}, { 
          withCredentials: true 
        });
        
        // Retry the original request
        return apiClient(originalRequest);
      } catch (err) {
        // If refresh token fails, redirect to login
        sessionStorage.removeItem('user');
        sessionStorage.removeItem('authMethod');
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;