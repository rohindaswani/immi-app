import React from 'react';
import { useSelector } from 'react-redux';
import { Box, Typography, Paper } from '@mui/material';
import { RootState } from '../../store';

export const AuthDebug: React.FC = () => {
  const authState = useSelector((state: RootState) => state.auth);
  const sessionUser = sessionStorage.getItem('user');
  const sessionAuthMethod = sessionStorage.getItem('authMethod');

  return (
    <Paper sx={{ p: 2, m: 2 }}>
      <Typography variant="h6" gutterBottom>
        Auth Debug Information
      </Typography>
      
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Redux Auth State:
        </Typography>
        <pre style={{ fontSize: '12px', backgroundColor: '#f5f5f5', padding: '8px' }}>
          {JSON.stringify(authState, null, 2)}
        </pre>
      </Box>

      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Session Storage:
        </Typography>
        <Typography variant="body2">
          User: {sessionUser || 'Not found'}
        </Typography>
        <Typography variant="body2">
          Auth Method: {sessionAuthMethod || 'Not found'}
        </Typography>
      </Box>

      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Document Cookies:
        </Typography>
        <Typography variant="body2" style={{ fontSize: '12px' }}>
          {document.cookie || 'No cookies found'}
        </Typography>
      </Box>
    </Paper>
  );
};