import apiClient from './client';

export interface Notification {
  notification_id: string;
  user_id: string;
  type: string;
  title: string;
  content: string;
  is_read: boolean;
  priority: string;
  related_entity_type?: string;
  related_entity_id?: string;
  created_at: string;
  scheduled_for?: string;
  expires_at?: string;
}

export interface NotificationListResponse {
  notifications: Notification[];
  total_count: number;
  unread_count: number;
  page: number;
  page_size: number;
}

export interface NotificationStats {
  total_notifications: number;
  unread_count: number;
  critical_count: number;
  upcoming_deadlines_count: number;
  overdue_count: number;
}

export interface NotificationFilters {
  page?: number;
  page_size?: number;
  unread_only?: boolean;
  priority_filter?: string;
}

export interface NotificationPreferences {
  email_notifications: boolean;
  deadline_alerts: boolean;
  checkin_reminders: boolean;
  document_expiry_alerts: boolean;
  status_change_notifications: boolean;
}

export const notificationApi = {
  // Get notifications with filters
  getNotifications: async (filters: NotificationFilters = {}): Promise<NotificationListResponse> => {
    const params = new URLSearchParams();
    
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.page_size) params.append('page_size', filters.page_size.toString());
    if (filters.unread_only) params.append('unread_only', filters.unread_only.toString());
    if (filters.priority_filter) params.append('priority_filter', filters.priority_filter);

    const response = await apiClient.get(`/notifications?${params.toString()}`);
    return response.data;
  },

  // Get notification statistics
  getStats: async (): Promise<NotificationStats> => {
    const response = await apiClient.get('/notifications/stats');
    return response.data;
  },

  // Mark single notification as read
  markAsRead: async (notificationId: string): Promise<void> => {
    await apiClient.patch(`/notifications/${notificationId}/read`);
  },

  // Mark all notifications as read
  markAllAsRead: async (): Promise<void> => {
    await apiClient.patch('/notifications/read-all');
  },

  // Delete notification
  deleteNotification: async (notificationId: string): Promise<void> => {
    await apiClient.delete(`/notifications/${notificationId}`);
  },

  // Create notification (admin/system use)
  createNotification: async (notificationData: {
    type: string;
    title: string;
    content?: string;
    priority?: string;
    related_entity_type?: string;
    related_entity_id?: string;
    scheduled_for?: string;
    expires_at?: string;
  }): Promise<Notification> => {
    const response = await apiClient.post('/notifications', notificationData);
    return response.data;
  },

  // Create deadline notification
  createDeadlineNotification: async (
    profileId: string,
    deadlineData: {
      deadline_type: string;
      deadline_date: string;
      deadline_title: string;
      deadline_description?: string;
      alert_days_before?: number[];
      is_critical?: boolean;
    }
  ): Promise<Notification> => {
    const response = await apiClient.post(
      `/notifications/deadline?profile_id=${profileId}`,
      deadlineData
    );
    return response.data;
  },

  // Create check-in reminder
  createCheckinReminder: async (reminderData: {
    reminder_type?: string;
    frequency_days?: number;
    next_reminder_date: string;
    is_active?: boolean;
  }): Promise<Notification> => {
    const response = await apiClient.post('/notifications/checkin', reminderData);
    return response.data;
  },

  // Get notification preferences
  getPreferences: async (): Promise<NotificationPreferences> => {
    const response = await apiClient.get('/notifications/preferences');
    return response.data.preferences;
  },

  // Update notification preferences
  updatePreferences: async (preferences: Partial<NotificationPreferences>): Promise<void> => {
    await apiClient.patch('/notifications/preferences', preferences);
  },

  // Trigger notification rules (testing/admin)
  runNotificationRules: async (): Promise<void> => {
    await apiClient.post('/notifications/run-rules');
  },

  // Cleanup expired notifications
  cleanupNotifications: async (): Promise<void> => {
    await apiClient.delete('/notifications/cleanup');
  },
};