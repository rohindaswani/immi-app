import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { Box, CircularProgress, Typography, Container, Paper } from '@mui/material';

import authApi from '../../api/auth';
import { loginSuccess } from '../../store/slices/authSlice';

const AuthSuccess: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const processAuthCallback = () => {
      try {
        // Extract query parameters from the URL
        const queryParams = new URLSearchParams(location.search);
        
        // Check if auth was successful
        const authenticated = queryParams.get('authenticated');
        
        if (authenticated === 'true') {
          // Process the user data
          const user = authApi.handleAuthSuccess(queryParams);
          
          // Dispatch user data to the auth store
          dispatch(loginSuccess({
            user,
            authMethod: 'google'
          }));
          
          // Redirect to dashboard
          setTimeout(() => {
            navigate('/dashboard');
          }, 1500);
        } else {
          setError('Authentication failed');
          setTimeout(() => {
            navigate('/login');
          }, 3000);
        }
      } catch (err) {
        console.error('Error processing authentication', err);
        setError('Authentication failed');
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      }
    };
    
    processAuthCallback();
  }, [dispatch, location.search, navigate]);

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, width: '100%', textAlign: 'center' }}>
          {error ? (
            <Typography variant="h6" color="error">
              {error}
            </Typography>
          ) : (
            <>
              <CircularProgress sx={{ mb: 3 }} />
              <Typography variant="h6">
                Authentication successful!
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Redirecting to dashboard...
              </Typography>
            </>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default AuthSuccess;