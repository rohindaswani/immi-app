import React, { useEffect, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
} from '@mui/lab';
import {
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Warning as WarningIcon,
  Event as EventIcon,
  Assignment as AssignmentIcon,
  Gavel as GavelIcon,
  Description as DescriptionIcon,
  Today as TodayIcon,
  Flight as FlightIcon,
  Help as HelpIcon,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import { fetchTimelineEvents } from '../../store/slices/timelineSlice';
import { TimelineEvent } from '../../api/timeline';
import { format, parseISO } from 'date-fns';

interface TimelineVisualizationProps {
  filters?: any;
  compact?: boolean;
}

const getEventIcon = (eventType: string) => {
  // Removed isCompleted parameter as event_status doesn't exist in DB
  const iconColor = 'primary';
  
  switch (eventType) {
    case 'application':
      return <AssignmentIcon color={iconColor} />;
    case 'interview':
      return <EventIcon color={iconColor} />;
    case 'decision':
      return <GavelIcon color={iconColor} />;
    case 'document_request':
      return <DescriptionIcon color={iconColor} />;
    case 'deadline':
      return <TodayIcon color={iconColor} />;
    case 'status_change':
      return <CheckCircleIcon color={iconColor} />;
    case 'travel':
      return <FlightIcon color={iconColor} />;
    default:
      return <HelpIcon color={iconColor} />;
  }
};

// Removed helper functions for priority and status as they don't exist in the database schema

const TimelineVisualization: React.FC<TimelineVisualizationProps> = ({ 
  filters = {}, 
  compact = false 
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const { events, loading, error } = useSelector((state: RootState) => state.timeline);

  useEffect(() => {
    dispatch(fetchTimelineEvents(filters));
  }, [dispatch, filters]);

  const sortedEvents = useMemo(() => {
    return [...events].sort((a, b) => 
      new Date(b.event_date).getTime() - new Date(a.event_date).getTime()
    );
  }, [events]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={300}>
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

  if (events.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Immigration Timeline
          </Typography>
          <Typography color="text.secondary">
            No timeline events found. Start by adding your first immigration milestone!
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ScheduleIcon />
          Immigration Timeline
          <Chip 
            label={`${events.length} events`} 
            size="small" 
            color="primary" 
            variant="outlined" 
          />
        </Typography>
        
        <Timeline position="left">
          {sortedEvents.map((event, index) => {
            // Removed isCompleted since event_status doesn't exist in DB
            const isLastItem = index === sortedEvents.length - 1;
            
            return (
              <TimelineItem key={event.event_id}>
                <TimelineSeparator>
                  <TimelineDot 
                    sx={{ 
                      bgcolor: 'primary.main',
                      // Removed is_milestone styling as it doesn't exist in DB
                    }}
                  >
                    {getEventIcon(event.event_type)}
                  </TimelineDot>
                  {!isLastItem && <TimelineConnector />}
                </TimelineSeparator>
                
                <TimelineContent>
                  <Box sx={{ mb: compact ? 1 : 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Typography variant={compact ? "subtitle2" : "h6"} component="h3">
                        {event.event_title}
                      </Typography>
                      
                      {/* Removed is_milestone and priority chip displays as they don't exist in DB */}
                    </Box>
                    
                    <Typography 
                      variant="body2" 
                      color="text.secondary" 
                      sx={{ mb: 1 }}
                    >
                      {format(parseISO(event.event_date), 'PPP')}
                    </Typography>
                    
                    {event.description && !compact && (
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        {event.description}
                      </Typography>
                    )}
                    
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {/* Removed chips for event_status, event_category and immigration_status as they don't exist in DB */}
                      {event.reference_id && (
                        <Chip 
                          label={`Ref: ${event.reference_id}`}
                          size="small"
                          variant="outlined"
                        />
                      )}
                      
                      {event.document_id && (
                        <Chip 
                          label="Has Document"
                          size="small"
                          color="info"
                          variant="outlined"
                        />
                      )}
                    </Box>
                    
                  </Box>
                </TimelineContent>
              </TimelineItem>
            );
          })}
        </Timeline>
      </CardContent>
    </Card>
  );
};

export default TimelineVisualization;