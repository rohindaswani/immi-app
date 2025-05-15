import React from 'react';
import { 
  Typography, 
  Box, 
  Container, 
  Button, 
  Grid, 
  Card, 
  CardContent, 
  CardActions,
  CardMedia
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Box>
      {/* Hero Section */}
      <Box sx={{ 
        bgcolor: 'primary.main', 
        color: 'white', 
        py: 8,
        borderRadius: 2,
        mb: 6
      }}>
        <Container maxWidth="md">
          <Typography variant="h2" component="h1" gutterBottom>
            Simplify Your Immigration Journey
          </Typography>
          <Typography variant="h5" component="p" paragraph>
            Manage your immigration documents, track visa status, and stay compliant with our comprehensive immigration advisor.
          </Typography>
          <Button 
            variant="contained" 
            color="secondary" 
            size="large"
            onClick={() => navigate('/register')}
            sx={{ mr: 2 }}
          >
            Get Started
          </Button>
          <Button 
            variant="outlined" 
            color="inherit" 
            size="large"
            onClick={() => navigate('/login')}
          >
            Sign In
          </Button>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg">
        <Typography variant="h3" component="h2" gutterBottom align="center" sx={{ mb: 6 }}>
          Key Features
        </Typography>
        
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardMedia
                component="div"
                sx={{
                  height: 160,
                  bgcolor: 'primary.light',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                }}
              >
                {/* Icon would go here */}
              </CardMedia>
              <CardContent>
                <Typography gutterBottom variant="h5" component="h2">
                  Document Management
                </Typography>
                <Typography>
                  Securely store and organize all your immigration documents in one place. Never lose track of important paperwork again.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardMedia
                component="div"
                sx={{
                  height: 160,
                  bgcolor: 'secondary.light',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                }}
              >
                {/* Icon would go here */}
              </CardMedia>
              <CardContent>
                <Typography gutterBottom variant="h5" component="h2">
                  Status Tracking
                </Typography>
                <Typography>
                  Stay on top of your immigration status with automated expiration reminders and compliance tracking.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardMedia
                component="div"
                sx={{
                  height: 160,
                  bgcolor: 'info.light',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                }}
              >
                {/* Icon would go here */}
              </CardMedia>
              <CardContent>
                <Typography gutterBottom variant="h5" component="h2">
                  AI Assistant
                </Typography>
                <Typography>
                  Get personalized immigration guidance with our AI-powered chat assistant. Ask questions and receive timely advice.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Home;