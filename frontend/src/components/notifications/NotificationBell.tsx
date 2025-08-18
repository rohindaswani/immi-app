import React, { useState, useRef, useEffect } from 'react';
import {
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Typography,
  Box,
  Divider,
  Button,
  CircularProgress,
  Chip
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  NotificationsNone as NotificationsNoneIcon,
  Circle as CircleIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { notificationApi } from '../../api/notifications';
import { formatDistanceToNow } from 'date-fns';

interface Notification {
  notification_id: string;
  type: string;
  title: string;
  content: string;
  is_read: boolean;
  priority: string;
  created_at: string;
  related_entity_type?: string;
  related_entity_id?: string;
}

interface NotificationStats {
  total_notifications: number;
  unread_count: number;
  critical_count: number;
}

const NotificationBell: React.FC = () => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [stats, setStats] = useState<NotificationStats | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const navigate = useNavigate();
  const isMounted = useRef(true);

  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  // Fetch notification stats
  const fetchStats = async () => {
    try {
      const statsData = await notificationApi.getStats();
      if (isMounted.current) {
        setStats(statsData);
      }
    } catch (error) {
      console.error('Failed to fetch notification stats:', error);
    }
  };

  // Fetch recent notifications for preview
  const fetchNotifications = async () => {
    if (!anchorEl) return; // Only fetch when menu is open
    
    setIsLoading(true);
    try {
      const response = await notificationApi.getNotifications({ page: 1, page_size: 5 });
      if (isMounted.current) {
        setNotifications(response.notifications);
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      if (isMounted.current) {
        setIsLoading(false);
      }
    }
  };

  // Mark notification as read
  const markAsRead = async (notificationId: string) => {
    setIsUpdating(true);
    try {
      await notificationApi.markAsRead(notificationId);
      // Refresh data
      await fetchStats();
      await fetchNotifications();
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  // Mark all as read
  const markAllAsRead = async () => {
    setIsUpdating(true);
    try {
      await notificationApi.markAllAsRead();
      // Refresh data
      await fetchStats();
      await fetchNotifications();
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  // Fetch stats on mount and set up interval
  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Fetch notifications when menu opens
  useEffect(() => {
    if (anchorEl) {
      fetchNotifications();
    }
  }, [anchorEl]);

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationClick = async (notification: Notification) => {
    // Mark as read if not already read
    if (!notification.is_read) {
      await markAsRead(notification.notification_id);
    }

    // Navigate to relevant page based on notification type
    handleNavigateToNotification(notification);
    handleClose();
  };

  const handleNavigateToNotification = (notification: Notification) => {
    switch (notification.type) {
      case 'deadline':
      case 'i94_expiry':
        navigate('/timeline');
        break;
      case 'document_expiry':
        navigate('/documents');
        break;
      case 'checkin':
        navigate('/profile');
        break;
      default:
        navigate('/notifications');
    }
  };

  const handleViewAll = () => {
    navigate('/notifications');
    handleClose();
  };

  const handleMarkAllAsRead = () => {
    markAllAsRead();
  };

  // Removed unused function

  const getNotificationTypeIcon = (_type: string, priority: string) => {
    const color = priority === 'high' ? 'error' : 'action';
    return <CircleIcon sx={{ fontSize: 8, color: `${color}.main` }} />;
  };

  const unreadCount = stats?.unread_count || 0;

  return (
    <>
      <IconButton
        color="inherit"
        onClick={handleClick}
        size="large"
        sx={{
          p: 1,
          '&:hover': {
            backgroundColor: 'action.hover',
          },
        }}
      >
        <Badge badgeContent={unreadCount} color="error" max={99}>
          {unreadCount > 0 ? (
            <NotificationsIcon />
          ) : (
            <NotificationsNoneIcon />
          )}
        </Badge>
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        PaperProps={{
          sx: {
            width: 360,
            maxHeight: 500,
            mt: 1.5,
            '& .MuiMenuItem-root': {
              px: 2,
              py: 1.5,
            },
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        {/* Header */}
        <Box sx={{ px: 2, py: 1.5, borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              Notifications
            </Typography>
            {unreadCount > 0 && (
              <Button
                size="small"
                onClick={handleMarkAllAsRead}
                disabled={isUpdating}
              >
                Mark all read
              </Button>
            )}
          </Box>
          {stats && (
            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
              {stats.critical_count > 0 && (
                <Chip
                  size="small"
                  label={`${stats.critical_count} urgent`}
                  color="error"
                  variant="outlined"
                />
              )}
              {unreadCount > 0 && (
                <Chip
                  size="small"
                  label={`${unreadCount} unread`}
                  color="primary"
                  variant="outlined"
                />
              )}
            </Box>
          )}
        </Box>

        {/* Loading state */}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}

        {/* Notifications list */}
        {!isLoading && notifications.length > 0 && (
          <Box sx={{ maxHeight: 300, overflowY: 'auto' }}>
            {notifications.map((notification) => (
              <MenuItem
                key={notification.notification_id}
                onClick={() => handleNotificationClick(notification)}
                sx={{
                  backgroundColor: notification.is_read ? 'transparent' : 'action.hover',
                  borderLeft: notification.priority === 'high' ? 3 : 0,
                  borderLeftColor: 'error.main',
                  '&:hover': {
                    backgroundColor: 'action.selected',
                  },
                }}
              >
                <Box sx={{ width: '100%' }}>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                    <Box sx={{ mt: 1, display: 'flex', alignItems: 'center' }}>
                      {!notification.is_read && getNotificationTypeIcon(notification.type, notification.priority)}
                      {notification.is_read && (
                        <CheckCircleIcon sx={{ fontSize: 8, color: 'text.disabled' }} />
                      )}
                    </Box>
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <Typography
                        variant="subtitle2"
                        sx={{
                          fontWeight: notification.is_read ? 'normal' : 'bold',
                          color: notification.is_read ? 'text.secondary' : 'text.primary',
                        }}
                        noWrap
                      >
                        {notification.title}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                          fontSize: '0.875rem',
                          lineHeight: 1.2,
                        }}
                      >
                        {notification.content}
                      </Typography>
                      <Typography variant="caption" color="text.disabled" sx={{ mt: 0.5 }}>
                        {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                      </Typography>
                    </Box>
                    {notification.priority === 'high' && (
                      <Chip
                        size="small"
                        label="Urgent"
                        color="error"
                        variant="outlined"
                        sx={{ fontSize: '0.625rem', height: 20 }}
                      />
                    )}
                  </Box>
                </Box>
              </MenuItem>
            ))}
          </Box>
        )}

        {/* Empty state */}
        {!isLoading && notifications.length === 0 && (
          <Box sx={{ py: 4, textAlign: 'center' }}>
            <NotificationsNoneIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography variant="body2" color="text.secondary">
              No notifications
            </Typography>
          </Box>
        )}

        {/* Footer */}
        <Divider />
        <MenuItem onClick={handleViewAll} sx={{ justifyContent: 'center', py: 1.5 }}>
          <Typography variant="button" color="primary">
            View All Notifications
          </Typography>
        </MenuItem>
      </Menu>
    </>
  );
};

export default NotificationBell;