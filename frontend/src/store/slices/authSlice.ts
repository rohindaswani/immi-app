import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface User {
  user_id: string;
  email: string;
  first_name?: string | null;
  last_name?: string | null;
  is_active: boolean;
  email_verified: boolean;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  authMethod: 'google' | 'password' | null;
}

// Get user data from sessionStorage (if available)
const getUserFromSession = (): User | null => {
  const userStr = sessionStorage.getItem('user');
  if (userStr) {
    try {
      return JSON.parse(userStr) as User;
    } catch {
      return null;
    }
  }
  return null;
};

// Check if we already have user data in session
const sessionUser = getUserFromSession();

const initialState: AuthState = {
  user: sessionUser,
  isAuthenticated: !!sessionUser,
  loading: !sessionUser, // Only set loading true if we don't have session data
  error: null,
  authMethod: sessionStorage.getItem('authMethod') as 'google' | 'password' | null
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    loginSuccess: (state, action: PayloadAction<{ user: User; token?: string; authMethod?: 'google' | 'password' }>) => {
      state.user = action.payload.user;
      state.isAuthenticated = true;
      state.loading = false;
      state.error = null;
      state.authMethod = action.payload.authMethod || 'password';
      
      // Store user in sessionStorage (not the token - it's in HTTP-only cookies)
      sessionStorage.setItem('user', JSON.stringify(action.payload.user));
      sessionStorage.setItem('authMethod', state.authMethod);
    },
    loginFailure: (state, action: PayloadAction<string>) => {
      state.loading = false;
      state.error = action.payload;
    },
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
      state.loading = false;
      state.error = null;
      state.authMethod = null;
      
      // Clear session storage
      sessionStorage.removeItem('user');
      sessionStorage.removeItem('authMethod');
    },
    updateUser: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = {
          ...state.user,
          ...action.payload,
        };
        // Update session storage
        sessionStorage.setItem('user', JSON.stringify(state.user));
      }
    },
    setAuthLoaded: (state) => {
      state.loading = false;
    },
  },
});

export const { loginStart, loginSuccess, loginFailure, logout, updateUser, setAuthLoaded } = authSlice.actions;

export default authSlice.reducer;