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
  
  // Get the location they came from
  const from = location.state?.from?.pathname || '/dashboard';
  
  // If already authenticated, redirect to where they came from or dashboard
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