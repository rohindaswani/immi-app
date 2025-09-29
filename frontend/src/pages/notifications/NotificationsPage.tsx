import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Switch,
  FormControlLabel,
  Pagination,
  Alert,
  CircularProgress,
  Grid,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  FilterList as FilterIcon,
  Delete as DeleteIcon,
  Settings as SettingsIcon,
  CheckCircle as CheckCircleIcon,
  Circle as CircleIcon,
  Notifications as NotificationsIcon,
  Schedule as ScheduleIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { formatDistanceToNow, format } from 'date-fns';
import { notificationApi, type NotificationFilters, type NotificationPreferences } from '../../api/notifications';

const NotificationsPage: React.FC = () => {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<NotificationFilters>({
    page_size: 20,
    unread_only: false,
    priority_filter: undefined,
  });
  const [filterAnchorEl, setFilterAnchorEl] = useState<null | HTMLElement>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);

  // State for data
  const [notificationsResponse, setNotificationsResponse] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch notifications
  const fetchNotifications = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await notificationApi.getNotifications({ ...filters, page });
      setNotificationsResponse(response);
    } catch (err) {
      setError('Failed to load notifications');
      console.error('Failed to fetch notifications:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch stats
  const fetchStats = async () => {
    try {
      const statsData = await notificationApi.getStats();
      setStats(statsData);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  // Fetch preferences
  const fetchPreferences = async () => {
    if (!settingsOpen) return;
    try {
      const prefsData = await notificationApi.getPreferences();
      setPreferences(prefsData);
    } catch (err) {
      console.error('Failed to fetch preferences:', err);
    }
  };

  // Mark as read
  const handleMarkAsRead = async (notificationId: string) => {
    setIsUpdating(true);
    try {
      await notificationApi.markAsRead(notificationId);
      await fetchNotifications();
      await fetchStats();
    } catch (err) {
      console.error('Failed to mark as read:', err);
    } finally {
      setIsUpdating(false);
    }
  };

  // Mark all as read
  const handleMarkAllAsRead = async () => {
    setIsUpdating(true);
    try {
      await notificationApi.markAllAsRead();
      await fetchNotifications();
      await fetchStats();
    } catch (err) {
      console.error('Failed to mark all as read:', err);
    } finally {
      setIsUpdating(false);
    }
  };

  // Delete notification
  const handleDelete = async (notificationId: string) => {
    setIsUpdating(true);
    try {
      await notificationApi.deleteNotification(notificationId);
      await fetchNotifications();
      await fetchStats();
    } catch (err) {
      console.error('Failed to delete notification:', err);
    } finally {
      setIsUpdating(false);
    }
  };

  // Update preferences
  const handlePreferenceChange = async (key: keyof NotificationPreferences, value: boolean) => {
    try {
      await notificationApi.updatePreferences({ [key]: value });
      await fetchPreferences();
    } catch (err) {
      console.error('Failed to update preferences:', err);
    }
  };

  // Effects
  useEffect(() => {
    fetchNotifications();
  }, [page, filters]);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    fetchPreferences();
  }, [settingsOpen]);

  const handlePageChange = (_event: React.ChangeEvent<unknown>, newPage: number) => {
    setPage(newPage);
  };

  const handleFilterChange = (newFilters: Partial<NotificationFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setPage(1); // Reset to first page when filters change
    setFilterAnchorEl(null);
  };


  // Removed unused function

  const getPriorityColor = (priority: string): 'error' | 'warning' | 'info' | 'default' => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'deadline':
      case 'i94_expiry':
        return <ScheduleIcon />;
      case 'document_expiry':
        return <WarningIcon />;
      case 'checkin':
        return <CheckCircleIcon />;
      default:
        return <NotificationsIcon />;
    }
  };

  const notifications = notificationsResponse?.notifications || [];
  const totalPages = Math.ceil((notificationsResponse?.total_count || 0) / (filters.page_size || 20));

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <div>
            <Typography variant="h4" component="h1" gutterBottom>
              Notifications
            </Typography>
            {stats && (
              <Typography variant="body2" color="text.secondary">
                {stats.unread_count} unread of {stats.total_notifications} total
              </Typography>
            )}
          </div>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <IconButton onClick={(e) => setFilterAnchorEl(e.currentTarget)}>
              <FilterIcon />
            </IconButton>
            <IconButton onClick={() => setSettingsOpen(true)}>
              <SettingsIcon />
            </IconButton>
          </Box>
        </Box>

        {/* Stats Cards */}
        {stats && (
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary">
                    {stats.unread_count}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Unread
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="error">
                    {stats.critical_count}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Urgent
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="warning">
                    {stats.upcoming_deadlines_count}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Upcoming Deadlines
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="text.secondary">
                    {stats.overdue_count}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Overdue
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Action Buttons */}
        {notifications.some((n: any) => !n.is_read) && (
          <Box sx={{ mb: 2 }}>
            <Button
              variant="outlined"
              onClick={handleMarkAllAsRead}
              disabled={isUpdating}
            >
              Mark All as Read
            </Button>
          </Box>
        )}
      </Box>

      {/* Loading State */}
      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Notifications List */}
      {!isLoading && (
        <Box sx={{ mb: 4 }}>
          {notifications.length === 0 ? (
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 6 }}>
                <NotificationsIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No notifications
                </Typography>
                <Typography variant="body2" color="text.disabled">
                  You're all caught up!
                </Typography>
              </CardContent>
            </Card>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {notifications.map((notification: any) => (
                <Card
                  key={notification.notification_id}
                  sx={{
                    backgroundColor: notification.is_read ? 'transparent' : 'action.hover',
                    borderLeft: notification.priority === 'high' ? 4 : 0,
                    borderLeftColor: 'error.main',
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                        {getTypeIcon(notification.type)}
                      </Box>
                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 1 }}>
                          <Typography
                            variant="h6"
                            sx={{
                              fontWeight: notification.is_read ? 'normal' : 'bold',
                              fontSize: '1.1rem',
                            }}
                          >
                            {notification.title}
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 2 }}>
                            <Chip
                              size="small"
                              label={notification.priority}
                              color={getPriorityColor(notification.priority)}
                              variant="outlined"
                            />
                            {!notification.is_read && (
                              <CircleIcon sx={{ fontSize: 8, color: 'primary.main' }} />
                            )}
                          </Box>
                        </Box>
                        <Typography variant="body1" color="text.secondary" paragraph>
                          {notification.content}
                        </Typography>
                        <Typography variant="caption" color="text.disabled">
                          {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })} •{' '}
                          {format(new Date(notification.created_at), 'MMM dd, yyyy h:mm a')}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                  <CardActions sx={{ justifyContent: 'space-between' }}>
                    <Box>
                      {!notification.is_read && (
                        <Button
                          size="small"
                          startIcon={<CheckCircleIcon />}
                          onClick={() => handleMarkAsRead(notification.notification_id)}
                          disabled={isUpdating}
                        >
                          Mark as Read
                        </Button>
                      )}
                    </Box>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDelete(notification.notification_id)}
                      disabled={isUpdating}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </CardActions>
                </Card>
              ))}
            </Box>
          )}
        </Box>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={handlePageChange}
            color="primary"
            showFirstButton
            showLastButton
          />
        </Box>
      )}

      {/* Filter Menu */}
      <Menu
        anchorEl={filterAnchorEl}
        open={Boolean(filterAnchorEl)}
        onClose={() => setFilterAnchorEl(null)}
        PaperProps={{ sx: { minWidth: 200 } }}
      >
        <MenuItem>
          <FormControlLabel
            control={
              <Switch
                checked={filters.unread_only || false}
                onChange={(e) => handleFilterChange({ unread_only: e.target.checked })}
              />
            }
            label="Unread only"
          />
        </MenuItem>
        <Divider />
        <MenuItem>
          <FormControl size="small" fullWidth>
            <InputLabel>Priority</InputLabel>
            <Select
              value={filters.priority_filter || ''}
              label="Priority"
              onChange={(e) => handleFilterChange({ priority_filter: e.target.value || undefined })}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="low">Low</MenuItem>
            </Select>
          </FormControl>
        </MenuItem>
      </Menu>

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Notification Preferences</DialogTitle>
        <DialogContent>
          {preferences && (
            <Box sx={{ pt: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={preferences.email_notifications}
                    onChange={(e) => handlePreferenceChange('email_notifications', e.target.checked)}
                  />
                }
                label="Email notifications"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={preferences.deadline_alerts}
                    onChange={(e) => handlePreferenceChange('deadline_alerts', e.target.checked)}
                  />
                }
                label="Deadline alerts"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={preferences.checkin_reminders}
                    onChange={(e) => handlePreferenceChange('checkin_reminders', e.target.checked)}
                  />
                }
                label="Monthly check-in reminders"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={preferences.document_expiry_alerts}
                    onChange={(e) => handlePreferenceChange('document_expiry_alerts', e.target.checked)}
                  />
                }
                label="Document expiry alerts"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={preferences.status_change_notifications}
                    onChange={(e) => handlePreferenceChange('status_change_notifications', e.target.checked)}
                  />
                }
                label="Status change notifications"
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default NotificationsPage;