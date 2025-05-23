import React, { useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Container, 
  Paper,
  Alert
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';

import { RootState } from '../../store';
import GoogleLoginButton from '../../components/auth/GoogleLoginButton';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { error, isAuthenticated } = useSelector((state: RootState) => state.auth);
  
  // Get the destination from location state, or default to dashboard
  const from = (location.state as any)?.from || '/dashboard';
  
  // If already authenticated, redirect to dashboard
  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

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
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography component="h1" variant="h5" align="center" gutterBottom>
            Sign in to Immigration Advisor
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <Box sx={{ mt: 3 }}>
            <GoogleLoginButton fullWidth variant="contained" />
          </Box>
          
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 3 }}>
            Secure authentication with Google
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;