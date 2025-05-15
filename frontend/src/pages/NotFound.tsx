import React from 'react';
import { 
  Typography, 
  Box, 
  Container, 
  Button,
  Paper
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

const NotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="md" sx={{ mt: 8 }}>
      <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h1" component="h1" gutterBottom>
          404
        </Typography>
        <Typography variant="h4" component="h2" gutterBottom>
          Page Not Found
        </Typography>
        <Typography variant="body1" paragraph>
          The page you are looking for doesn't exist or has been moved.
        </Typography>
        <Box mt={4}>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={() => navigate('/')}
          >
            Return to Home
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default NotFound;