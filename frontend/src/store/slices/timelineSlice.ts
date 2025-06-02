import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { timelineAPI, TimelineEvent, Deadline, StatusHistory, TimelineSummary, ProgressAnalytics, TimelineFilters } from '../../api/timeline';

interface TimelineState {
  events: TimelineEvent[];
  deadlines: Deadline[];
  statusHistory: StatusHistory[];
  summary: TimelineSummary | null;
  progressAnalytics: ProgressAnalytics | null;
  loading: boolean;
  error: string | null;
  filters: TimelineFilters;
}

const initialState: TimelineState = {
  events: [],
  deadlines: [],
  statusHistory: [],
  summary: null,
  progressAnalytics: null,
  loading: false,
  error: null,
  filters: {
    skip: 0,
    limit: 100,
    // Removed event_category, priority, is_milestone filters as they don't exist in DB
  },
};

// Timeline Events Thunks
export const fetchTimelineEvents = createAsyncThunk(
  'timeline/fetchEvents',
  async (filters: TimelineFilters = {}) => {
    return await timelineAPI.getTimelineEvents(filters);
  }
);

export const createTimelineEvent = createAsyncThunk(
  'timeline/createEvent',
  async (eventData: any) => {
    return await timelineAPI.createTimelineEvent(eventData);
  }
);

export const updateTimelineEvent = createAsyncThunk(
  'timeline/updateEvent',
  async ({ eventId, updates }: { eventId: string; updates: any }) => {
    return await timelineAPI.updateTimelineEvent(eventId, updates);
  }
);

export const deleteTimelineEvent = createAsyncThunk(
  'timeline/deleteEvent',
  async (eventId: string) => {
    await timelineAPI.deleteTimelineEvent(eventId);
    return eventId;
  }
);

// Deadlines Thunks
export const fetchDeadlines = createAsyncThunk(
  'timeline/fetchDeadlines',
  async ({ upcomingOnly = true, daysAhead = 30 }: { upcomingOnly?: boolean; daysAhead?: number } = {}) => {
    return await timelineAPI.getDeadlines(upcomingOnly, daysAhead);
  }
);

export const createDeadline = createAsyncThunk(
  'timeline/createDeadline',
  async (deadlineData: Partial<Deadline>) => {
    return await timelineAPI.createDeadline(deadlineData);
  }
);

export const updateDeadline = createAsyncThunk(
  'timeline/updateDeadline',
  async ({ deadlineId, updates }: { deadlineId: string; updates: Partial<Deadline> }) => {
    return await timelineAPI.updateDeadline(deadlineId, updates);
  }
);

export const deleteDeadline = createAsyncThunk(
  'timeline/deleteDeadline',
  async (deadlineId: string) => {
    await timelineAPI.deleteDeadline(deadlineId);
    return deadlineId;
  }
);

// Status History Thunks
export const fetchStatusHistory = createAsyncThunk(
  'timeline/fetchStatusHistory',
  async ({ skip = 0, limit = 100 }: { skip?: number; limit?: number } = {}) => {
    return await timelineAPI.getStatusHistory(skip, limit);
  }
);

export const createStatusChange = createAsyncThunk(
  'timeline/createStatusChange',
  async (statusData: Partial<StatusHistory>) => {
    return await timelineAPI.createStatusChange(statusData);
  }
);

// Analytics Thunks
export const fetchTimelineSummary = createAsyncThunk(
  'timeline/fetchSummary',
  async () => {
    return await timelineAPI.getTimelineSummary();
  }
);

export const fetchProgressAnalytics = createAsyncThunk(
  'timeline/fetchProgressAnalytics',
  async (immigrationPath?: string) => {
    return await timelineAPI.getProgressAnalytics(immigrationPath);
  }
);

const timelineSlice = createSlice({
  name: 'timeline',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<Partial<TimelineFilters>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = {
        skip: 0,
        limit: 100,
      };
    },
    clearError: (state) => {
      state.error = null;
    },
    resetTimeline: (state) => {
      return initialState;
    },
  },
  extraReducers: (builder) => {
    builder
      // Timeline Events
      .addCase(fetchTimelineEvents.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTimelineEvents.fulfilled, (state, action) => {
        state.loading = false;
        state.events = action.payload;
      })
      .addCase(fetchTimelineEvents.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch timeline events';
      })
      .addCase(createTimelineEvent.fulfilled, (state, action) => {
        state.events.unshift(action.payload);
      })
      .addCase(updateTimelineEvent.fulfilled, (state, action) => {
        const index = state.events.findIndex(event => event.event_id === action.payload.event_id);
        if (index !== -1) {
          state.events[index] = action.payload;
        }
      })
      .addCase(deleteTimelineEvent.fulfilled, (state, action) => {
        state.events = state.events.filter(event => event.event_id !== action.payload);
      })
      
      // Deadlines
      .addCase(fetchDeadlines.fulfilled, (state, action) => {
        state.deadlines = action.payload;
      })
      .addCase(createDeadline.fulfilled, (state, action) => {
        state.deadlines.unshift(action.payload);
      })
      .addCase(updateDeadline.fulfilled, (state, action) => {
        const index = state.deadlines.findIndex(deadline => deadline.id === action.payload.id);
        if (index !== -1) {
          state.deadlines[index] = action.payload;
        }
      })
      .addCase(deleteDeadline.fulfilled, (state, action) => {
        state.deadlines = state.deadlines.filter(deadline => deadline.id !== action.payload);
      })
      // Note: No changes needed here since Deadline still uses 'id' field
      
      // Status History
      .addCase(fetchStatusHistory.fulfilled, (state, action) => {
        state.statusHistory = action.payload;
      })
      .addCase(createStatusChange.fulfilled, (state, action) => {
        state.statusHistory.unshift(action.payload);
      })
      
      // Analytics
      .addCase(fetchTimelineSummary.fulfilled, (state, action) => {
        state.summary = action.payload;
      })
      .addCase(fetchProgressAnalytics.fulfilled, (state, action) => {
        state.progressAnalytics = action.payload;
      })
      
      // Error handling for all async actions
      .addMatcher(
        (action) => action.type.endsWith('/rejected'),
        (state, action) => {
          state.loading = false;
          state.error = action.error.message || 'An error occurred';
        }
      );
  },
});

export const { setFilters, clearFilters, clearError, resetTimeline } = timelineSlice.actions;
export default timelineSlice.reducer;