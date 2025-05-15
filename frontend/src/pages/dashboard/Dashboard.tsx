import React from 'react';
import { 
  Typography, 
  Box, 
  Container, 
  Grid, 
  Card, 
  CardContent, 
  CardHeader,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
  Button,
  Chip,
  Alert
} from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import EventIcon from '@mui/icons-material/Event';

const Dashboard: React.FC = () => {
  // In a real implementation, this data would come from API calls
  const upcomingDeadlines = [
    {
      id: 1,
      title: 'H1-B Visa Expiration',
      date: '2025-08-15',
      status: 'upcoming',
      daysRemaining: 120
    },
    {
      id: 2,
      title: 'I-94 Expiration',
      date: '2024-10-30',
      status: 'warning',
      daysRemaining: 45
    },
    {
      id: 3,
      title: 'Passport Renewal',
      date: '2026-03-22',
      status: 'ok',
      daysRemaining: 520
    }
  ];

  const recentDocuments = [
    {
      id: 1,
      title: 'H1-B Approval Notice',
      date: '2023-06-15',
      type: 'I-797'
    },
    {
      id: 2,
      title: 'Passport',
      date: '2020-05-20',
      type: 'Identification'
    },
    {
      id: 3,
      title: 'I-94 Record',
      date: '2023-09-10',
      type: 'Travel Record'
    }
  ];

  const complianceStatus = {
    status: 'Compliant',
    checks: [
      { name: 'Valid I-94 Record', status: 'passed' },
      { name: 'Employment Authorization', status: 'passed' },
      { name: 'Address on File', status: 'warning', message: 'Last updated 10 months ago' }
    ]
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      
      <Typography variant="subtitle1" color="text.secondary" paragraph>
        Welcome back! Here's an overview of your immigration status and important items.
      </Typography>
      
      <Box sx={{ mb: 4 }}>
        <Alert 
          severity="info" 
          sx={{ mb: 2 }}
        >
          Your next monthly check-in is due on October 15, 2023
        </Alert>
      </Box>
      
      <Grid container spacing={4}>
        {/* Status Summary */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardHeader title="Current Status" />
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="h5" component="div">
                  H1-B Visa Holder
                </Typography>
                <Chip 
                  label="Active" 
                  color="success" 
                  size="small" 
                  sx={{ ml: 2 }} 
                />
              </Box>
              
              <Typography color="text.secondary" gutterBottom>
                Valid until August 15, 2025
              </Typography>
              
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Key Information:
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      I-94 Number: 12345678901
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      Last Entry: September 10, 2023
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      Current Employer: Example Corp
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      USCIS#: A123456789
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Compliance Status */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardHeader title="Compliance Status" />
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h5" component="div">
                  {complianceStatus.status}
                </Typography>
              </Box>
              
              <List>
                {complianceStatus.checks.map((check, index) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemText 
                        primary={check.name}
                        secondary={check.message}
                      />
                      {check.status === 'passed' ? (
                        <CheckCircleIcon color="success" />
                      ) : (
                        <WarningIcon color="warning" />
                      )}
                    </ListItem>
                    {index < complianceStatus.checks.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
              
              <Button 
                variant="outlined" 
                fullWidth 
                sx={{ mt: 2 }}
              >
                View Full Compliance Report
              </Button>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Upcoming Deadlines */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Upcoming Deadlines" />
            <CardContent>
              <List>
                {upcomingDeadlines.map((deadline, index) => (
                  <React.Fragment key={deadline.id}>
                    <ListItem>
                      <ListItemText 
                        primary={deadline.title}
                        secondary={`Due: ${deadline.date}`}
                      />
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <EventIcon sx={{ mr: 1, color: 
                          deadline.daysRemaining < 60 ? 'error.main' : 
                          deadline.daysRemaining < 90 ? 'warning.main' : 
                          'success.main'
                        }} />
                        <Typography 
                          variant="body2"
                          color={
                            deadline.daysRemaining < 60 ? 'error.main' : 
                            deadline.daysRemaining < 90 ? 'warning.main' : 
                            'text.secondary'
                          }
                        >
                          {deadline.daysRemaining} days
                        </Typography>
                      </Box>
                    </ListItem>
                    {index < upcomingDeadlines.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
              
              <Button 
                variant="outlined" 
                fullWidth 
                sx={{ mt: 2 }}
              >
                View All Deadlines
              </Button>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Recent Documents */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Recent Documents" />
            <CardContent>
              <List>
                {recentDocuments.map((document, index) => (
                  <React.Fragment key={document.id}>
                    <ListItem>
                      <ListItemText 
                        primary={document.title}
                        secondary={`Type: ${document.type} | Uploaded: ${document.date}`}
                      />
                    </ListItem>
                    {index < recentDocuments.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
              
              <Button 
                variant="outlined" 
                fullWidth 
                sx={{ mt: 2 }}
              >
                View All Documents
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;