import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Divider,
  Chip,
  CircularProgress,
  Alert,
  Button,
  Grid,
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
} from '@mui/lab';
import {
  Home as HomeIcon,
  Business as BusinessIcon,
  Event as EventIcon,
  History as HistoryIcon,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../store';
import { 
  fetchAddressHistory, 
  fetchEmploymentHistory 
} from '../../store/slices/historySlice';
import { format, parseISO, compareDesc } from 'date-fns';
import { Link } from 'react-router-dom';

type TimelineEvent = {
  id: string;
  type: 'address' | 'employment';
  title: string;
  subtitle: string;
  date: Date;
  isCurrent: boolean;
  color: 'primary' | 'secondary' | 'info' | 'success' | 'warning' | 'error' | 'default';
};

const HistoryTimelineView: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { 
    addressHistory, 
    employmentHistory, 
    loading, 
    error 
  } = useSelector((state: RootState) => state.history);
  const [timelineEvents, setTimelineEvents] = useState<TimelineEvent[]>([]);
  
  // Load history data when component mounts
  useEffect(() => {
    dispatch(fetchAddressHistory());
    dispatch(fetchEmploymentHistory());
  }, [dispatch]);
  
  // Convert address and employment history to unified timeline events
  useEffect(() => {
    const events: TimelineEvent[] = [];
    
    // Add address history events
    addressHistory.forEach((address) => {
      // Add start date event
      events.push({
        id: `address-start-${address.address_history_id}`,
        type: 'address',
        title: `Moved to ${address.address?.city_name || 'new address'}`,
        subtitle: address.address ? 
          `${address.address.street_address_1}, ${address.address.city_name || ''} ${address.address.state_name || ''}` : 
          'Address details not available',
        date: parseISO(address.start_date),
        isCurrent: address.is_current,
        color: 'info',
      });
      
      // Add end date event if not current and has end date
      if (!address.is_current && address.end_date) {
        events.push({
          id: `address-end-${address.address_history_id}`,
          type: 'address',
          title: `Moved from ${address.address?.city_name || 'address'}`,
          subtitle: address.address ? 
            `${address.address.street_address_1}, ${address.address.city_name || ''} ${address.address.state_name || ''}` : 
            'Address details not available',
          date: parseISO(address.end_date),
          isCurrent: false,
          color: 'default',
        });
      }
    });
    
    // Add employment history events
    employmentHistory.forEach((employment) => {
      // Add start date event
      events.push({
        id: `employment-start-${employment.employment_id}`,
        type: 'employment',
        title: `Started as ${employment.job_title}`,
        subtitle: `at ${employment.employer?.company_name || 'employer'}`,
        date: parseISO(employment.start_date),
        isCurrent: employment.is_current,
        color: 'success',
      });
      
      // Add end date event if not current and has end date
      if (!employment.is_current && employment.end_date) {
        events.push({
          id: `employment-end-${employment.employment_id}`,
          type: 'employment',
          title: `Left position as ${employment.job_title}`,
          subtitle: `at ${employment.employer?.company_name || 'employer'}`,
          date: parseISO(employment.end_date),
          isCurrent: false,
          color: 'default',
        });
      }
    });
    
    // Sort events by date in descending order (newest first)
    events.sort((a, b) => compareDesc(a.date, b.date));
    
    setTimelineEvents(events);
  }, [addressHistory, employmentHistory]);
  
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }
  
  if (timelineEvents.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="textSecondary" gutterBottom>
          No address or employment history found.
        </Typography>
        <Button 
          component={Link} 
          to="/history" 
          variant="contained" 
          color="primary"
          startIcon={<HistoryIcon />}
        >
          Add History Records
        </Button>
      </Paper>
    );
  }
  
  const getIcon = (type: string) => {
    switch (type) {
      case 'address':
        return <HomeIcon />;
      case 'employment':
        return <BusinessIcon />;
      default:
        return <EventIcon />;
    }
  };
  
  return (
    <Paper sx={{ p: 2 }}>
      <Grid container spacing={2} alignItems="center" sx={{ mb: 2 }}>
        <Grid item xs>
          <Typography variant="h6" component="h2">
            Address & Employment Timeline
          </Typography>
        </Grid>
        <Grid item>
          <Button 
            component={Link} 
            to="/history" 
            variant="outlined"
            startIcon={<HistoryIcon />}
          >
            Manage History
          </Button>
        </Grid>
      </Grid>
      
      <Divider sx={{ mb: 2 }} />
      
      <Timeline position="alternate">
        {timelineEvents.map((event) => (
          <TimelineItem key={event.id}>
            <TimelineOppositeContent color="text.secondary">
              {format(event.date, 'MMM d, yyyy')}
              {event.isCurrent && (
                <Chip 
                  label="Current" 
                  size="small" 
                  color="primary" 
                  sx={{ ml: 1 }}
                />
              )}
            </TimelineOppositeContent>
            <TimelineSeparator>
              <TimelineDot color={event.color}>
                {getIcon(event.type)}
              </TimelineDot>
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="h6" component="span">
                {event.title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {event.subtitle}
              </Typography>
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>
    </Paper>
  );
};

export default HistoryTimelineView;