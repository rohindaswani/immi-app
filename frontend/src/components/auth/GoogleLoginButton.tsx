import React from 'react';
import { Button, Box, Typography } from '@mui/material';
import GoogleIcon from '@mui/icons-material/Google';
import authApi from '../../api/auth';

interface GoogleLoginButtonProps {
  fullWidth?: boolean;
  variant?: 'text' | 'outlined' | 'contained';
  size?: 'small' | 'medium' | 'large';
}

const GoogleLoginButton: React.FC<GoogleLoginButtonProps> = ({
  fullWidth = true,
  variant = 'contained',
  size = 'medium'
}) => {
  const handleGoogleLogin = () => {
    authApi.googleLogin();
  };

  return (
    <Button
      variant={variant}
      color="primary"
      fullWidth={fullWidth}
      size={size}
      onClick={handleGoogleLogin}
      startIcon={<GoogleIcon />}
      sx={{
        backgroundColor: '#fff',
        color: '#757575',
        border: '1px solid #ddd',
        '&:hover': {
          backgroundColor: '#f5f5f5',
        },
        textTransform: 'none'
      }}
    >
      <Typography variant="button">Sign in with Google</Typography>
    </Button>
  );
};

export default GoogleLoginButton;