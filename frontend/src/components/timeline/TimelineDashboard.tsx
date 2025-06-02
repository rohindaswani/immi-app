import React, { useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Avatar,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
  Assignment as AssignmentIcon,
  Event as EventIcon,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import { 
  fetchTimelineSummary, 
  fetchProgressAnalytics, 
  fetchDeadlines 
} from '../../store/slices/timelineSlice';
import { format, parseISO, differenceInDays } from 'date-fns';

interface TimelineDashboardProps {
  immigrationPath?: string;
}

const TimelineDashboard: React.FC<TimelineDashboardProps> = ({ immigrationPath }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { 
    summary, 
    progressAnalytics, 
    deadlines, 
    loading, 
    error 
  } = useSelector((state: RootState) => state.timeline);

  useEffect(() => {
    dispatch(fetchTimelineSummary());
    dispatch(fetchProgressAnalytics(immigrationPath));
    dispatch(fetchDeadlines({ upcomingOnly: true, daysAhead: 30 }));
  }, [dispatch, immigrationPath]);

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

  const getDeadlineUrgency = (deadlineDate: string) => {
    const daysUntil = differenceInDays(parseISO(deadlineDate), new Date());
    if (daysUntil < 0) return 'overdue';
    if (daysUntil <= 3) return 'critical';
    if (daysUntil <= 7) return 'urgent';
    if (daysUntil <= 14) return 'important';
    return 'normal';
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'overdue':
        return 'error';
      case 'critical':
        return 'error';
      case 'urgent':
        return 'warning';
      case 'important':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <TimelineIcon />
        Timeline Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Summary Statistics */}
        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                  <EventIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" component="div">
                    {summary?.total_events || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Events
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                  <CheckCircleIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" component="div">
                    {summary?.milestones_completed || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Milestones Completed
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'warning.main', mr: 2 }}>
                  <ScheduleIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" component="div">
                    {summary?.upcoming_deadlines || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Upcoming Deadlines
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'error.main', mr: 2 }}>
                  <WarningIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" component="div">
                    {summary?.overdue_deadlines || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Overdue Items
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Progress Analytics */}
        {progressAnalytics && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TrendingUpIcon />
                  Progress Analytics
                  {progressAnalytics.immigration_path && (
                    <Chip 
                      label={progressAnalytics.immigration_path} 
                      size="small" 
                      color="primary" 
                      variant="outlined" 
                    />
                  )}
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">
                      Milestone Progress
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {progressAnalytics.completed_milestones}/{progressAnalytics.total_milestones}
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={progressAnalytics.progress_percentage} 
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {progressAnalytics.progress_percentage.toFixed(1)}% Complete
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                  <Box>
                    <Typography variant="h6" color="success.main">
                      {progressAnalytics.completed_milestones}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Completed
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="h6" color="warning.main">
                      {progressAnalytics.remaining_milestones}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Remaining
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="h6" color="info.main">
                      {progressAnalytics.estimated_completion_months}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Est. Months
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Upcoming Deadlines */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <ScheduleIcon />
                Upcoming Deadlines
                {deadlines.length > 0 && (
                  <Chip 
                    label={`${deadlines.length} items`} 
                    size="small" 
                    color="warning" 
                    variant="outlined" 
                  />
                )}
              </Typography>
              
              {deadlines.length === 0 ? (
                <Typography color="text.secondary">
                  No upcoming deadlines
                </Typography>
              ) : (
                <List dense>
                  {deadlines.slice(0, 5).map((deadline, index) => {
                    const urgency = getDeadlineUrgency(deadline.deadline_date);
                    const daysUntil = differenceInDays(parseISO(deadline.deadline_date), new Date());
                    
                    return (
                      <React.Fragment key={deadline.id}>
                        <ListItem sx={{ px: 0 }}>
                          <ListItemIcon>
                            <Avatar 
                              sx={{ 
                                width: 32, 
                                height: 32, 
                                bgcolor: `${getUrgencyColor(urgency)}.main` 
                              }}
                            >
                              <AssignmentIcon fontSize="small" />
                            </Avatar>
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="body2" sx={{ flexGrow: 1 }}>
                                  {deadline.title}
                                </Typography>
                                <Chip 
                                  label={
                                    daysUntil < 0 
                                      ? `${Math.abs(daysUntil)} days overdue`
                                      : daysUntil === 0 
                                        ? 'Due today'
                                        : `${daysUntil} days left`
                                  }
                                  size="small"
                                  color={getUrgencyColor(urgency) as any}
                                  variant={urgency === 'overdue' || urgency === 'critical' ? 'filled' : 'outlined'}
                                />
                              </Box>
                            }
                            secondary={format(parseISO(deadline.deadline_date), 'PPP')}
                          />
                        </ListItem>
                        {index < Math.min(deadlines.length - 1, 4) && <Divider />}
                      </React.Fragment>
                    );
                  })}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TimelineDashboard;