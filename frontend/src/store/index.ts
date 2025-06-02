import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import profileReducer from './slices/profileSlice';
import documentsReducer from './slices/documentsSlice';
import timelineReducer from './slices/timelineSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    profiles: profileReducer,
    documents: documentsReducer,
    timeline: timelineReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;