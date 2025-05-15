import axios from 'axios';

const BASE_URL = '/api/v1';

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle common errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Handle token expiration
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // This would call a refresh token endpoint in a real implementation
        // const refreshToken = localStorage.getItem('refreshToken');
        // const response = await authApi.refreshToken(refreshToken);
        // localStorage.setItem('token', response.data.access_token);
        // originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
        // return apiClient(originalRequest);
      } catch (err) {
        // If refresh token fails, log out the user
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;