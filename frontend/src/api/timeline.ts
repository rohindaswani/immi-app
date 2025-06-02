import apiClient from './client';

export interface TimelineEvent {
  event_id: string;
  event_title: string;
  description?: string;
  event_date: string;
  event_type: string;
  // These fields exist in the DB
  event_category?: string;
  event_subtype?: string;
  priority?: string;
  is_milestone?: boolean;
  event_status?: string;
  // UUID fields must be valid UUIDs or null
  reference_id?: string | null;
  reference_table?: string;
  profile_id: string;
  created_at: string;
  updated_at?: string;
  document_id?: string | null;
  travel_record_id?: string;
  immigration_status_id?: string;
  extra_data?: Record<string, any>;
}

export interface TimelineEventCreate {
  event_title: string;
  description?: string;
  event_date: string;
  event_type: string;
  // These fields exist in the DB
  event_category?: string;
  event_subtype?: string;
  priority?: string;
  is_milestone?: boolean;
  event_status?: string;
  // UUID fields must be valid UUIDs or null
  reference_id?: string | null;
  reference_table?: string;
  document_id?: string | null;
  extra_data?: Record<string, any>;
}

export interface TimelineEventUpdate {
  event_title?: string;
  description?: string;
  event_date?: string;
  event_type?: string;
  // These fields exist in the DB
  event_category?: string;
  event_subtype?: string;
  priority?: string;
  is_milestone?: boolean;
  event_status?: string;
  // UUID fields must be valid UUIDs or null
  reference_id?: string | null;
  reference_table?: string;
  document_id?: string | null;
  extra_data?: Record<string, any>;
}

export interface Deadline {
  id: string;
  title: string;
  description?: string;
  deadline_date: string;
  deadline_type: string;
  priority_level: 'low' | 'medium' | 'high' | 'critical';
  is_completed: boolean;
  alert_enabled: boolean;
  alert_days_before: number;
  alert_frequency: 'daily' | 'weekly' | 'monthly';
  completion_notes?: string;
  extra_data?: Record<string, any>;
  user_id: string;
  timeline_event_id?: string;
  created_at: string;
  updated_at?: string;
}

export interface StatusHistory {
  id: string;
  status: string;
  status_description?: string;
  notes?: string;
  extra_data?: Record<string, any>;
  user_id: string;
  timeline_event_id?: string;
  changed_at: string;
  changed_by_user_id?: string;
}

export interface TimelineSummary {
  total_events: number;
  milestones_completed: number;
  total_milestones: number;
  milestone_completion_rate: number;
  upcoming_deadlines: number;
  overdue_deadlines: number;
}

export interface ProgressAnalytics {
  immigration_path?: string;
  total_milestones: number;
  completed_milestones: number;
  remaining_milestones: number;
  progress_percentage: number;
  estimated_completion_months: number;
}

export interface TimelineFilters {
  skip?: number;
  limit?: number;
  event_type?: string;
  category?: string;
  priority?: string;
  start_date?: string;
  end_date?: string;
  is_milestone?: boolean;
  is_deadline?: boolean;
}

class TimelineAPI {
  // Timeline Events
  async getTimelineEvents(filters: TimelineFilters = {}): Promise<TimelineEvent[]> {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString());
      }
    });
    
    const response = await apiClient.get(`/timeline/events?${params.toString()}`);
    return response.data;
  }

  async createTimelineEvent(event: TimelineEventCreate): Promise<TimelineEvent> {
    const response = await apiClient.post('/timeline/events', event);
    return response.data;
  }

  async getTimelineEvent(eventId: string): Promise<TimelineEvent> {
    const response = await apiClient.get(`/timeline/events/${eventId}`);
    return response.data;
  }

  async updateTimelineEvent(eventId: string, updates: TimelineEventUpdate): Promise<TimelineEvent> {
    const response = await apiClient.put(`/timeline/events/${eventId}`, updates);
    return response.data;
  }

  async deleteTimelineEvent(eventId: string): Promise<void> {
    await apiClient.delete(`/timeline/events/${eventId}`);
  }

  // Deadlines
  async getDeadlines(upcomingOnly: boolean = true, daysAhead: number = 30): Promise<Deadline[]> {
    const params = new URLSearchParams({
      upcoming_only: upcomingOnly.toString(),
      days_ahead: daysAhead.toString(),
    });
    
    const response = await apiClient.get(`/timeline/deadlines?${params.toString()}`);
    return response.data;
  }

  async createDeadline(deadline: Partial<Deadline>): Promise<Deadline> {
    const response = await apiClient.post('/timeline/deadlines', deadline);
    return response.data;
  }

  async updateDeadline(deadlineId: string, updates: Partial<Deadline>): Promise<Deadline> {
    const response = await apiClient.put(`/timeline/deadlines/${deadlineId}`, updates);
    return response.data;
  }

  async deleteDeadline(deadlineId: string): Promise<void> {
    await apiClient.delete(`/timeline/deadlines/${deadlineId}`);
  }

  // Status History
  async getStatusHistory(skip: number = 0, limit: number = 100): Promise<StatusHistory[]> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    
    const response = await apiClient.get(`/timeline/status-history?${params.toString()}`);
    return response.data;
  }

  async createStatusChange(statusChange: Partial<StatusHistory>): Promise<StatusHistory> {
    const response = await apiClient.post('/timeline/status-history', statusChange);
    return response.data;
  }

  // Analytics
  async getTimelineSummary(): Promise<TimelineSummary> {
    const response = await apiClient.get('/timeline/analytics/summary');
    return response.data;
  }

  async getProgressAnalytics(immigrationPath?: string): Promise<ProgressAnalytics> {
    const params = immigrationPath ? `?immigration_path=${immigrationPath}` : '';
    const response = await apiClient.get(`/timeline/analytics/progress${params}`);
    return response.data;
  }
}

export const timelineAPI = new TimelineAPI();