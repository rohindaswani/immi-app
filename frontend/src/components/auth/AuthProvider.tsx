import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';

import { RootState } from '../../store';
import { loginSuccess, logout, setAuthLoaded } from '../../store/slices/authSlice';
import { checkAuthentication } from '../../utils/auth';

interface AuthProviderProps {
  children: React.ReactNode;
}

/**
 * AuthProvider is a wrapper component that checks authentication status
 * and updates the Redux store accordingly.
 */
const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const dispatch = useDispatch();
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    // Check authentication status when the component mounts
    const verifyAuth = async () => {
      // Only try to verify if not already authenticated
      if (!isAuthenticated) {
        const { isAuthenticated: isAuth, user } = await checkAuthentication();
        
        if (isAuth && user) {
          // Get auth method from session storage
          const authMethod = sessionStorage.getItem('authMethod') as 'google' | 'password' | null;
          
          dispatch(loginSuccess({ 
            user,
            authMethod: authMethod || 'password' 
          }));
        } else {
          // Mark auth as loaded even if not authenticated
          dispatch(setAuthLoaded());
        }
      } else {
        // If already authenticated, mark as loaded
        dispatch(setAuthLoaded());
      }
    };
    
    verifyAuth();
  }, [dispatch, isAuthenticated]);

  return <>{children}</>;
};

export default AuthProvider;