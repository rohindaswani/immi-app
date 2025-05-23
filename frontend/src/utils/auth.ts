import { User } from '../store/slices/authSlice';
import authApi from '../api/auth';

/**
 * Function to check if the user is authenticated
 * We check both session storage and try to fetch current user info
 */
export const checkAuthentication = async (): Promise<{
  isAuthenticated: boolean;
  user: User | null;
}> => {
  try {
    // First check session storage
    const userStr = sessionStorage.getItem('user');
    
    if (userStr) {
      const user = JSON.parse(userStr) as User;
      return { isAuthenticated: true, user };
    }

    // If not in session storage, try getting user from API
    const response = await authApi.getCurrentUser();
    
    if (response.status === 200) {
      return { isAuthenticated: true, user: response.data };
    }

    return { isAuthenticated: false, user: null };
  } catch (error) {
    return { isAuthenticated: false, user: null };
  }
};

/**
 * Utility function to handle logout
 */
export const logout = async (): Promise<boolean> => {
  try {
    await authApi.logout();
    // Clear session storage
    sessionStorage.removeItem('user');
    sessionStorage.removeItem('authMethod');
    return true;
  } catch (error) {
    console.error('Logout error:', error);
    return false;
  }
};

/**
 * Get auth method used
 */
export const getAuthMethod = (): 'google' | 'password' | null => {
  return sessionStorage.getItem('authMethod') as 'google' | 'password' | null;
};

/**
 * Initialize Google auth script
 */
export const initGoogleAuth = () => {
  // No need to load the Google SDK for now
  // Our implementation uses server-side OAuth flow
  // This function is a placeholder for any future client-side OAuth initialization
};