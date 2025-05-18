import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import profilesApi, { ProfileResponse, ProfileCreate, ProfileUpdate } from '../../api/profile';

interface ProfileState {
  profiles: ProfileResponse[];
  selectedProfile: ProfileResponse | null;
  loading: boolean;
  error: string | null;
}

const initialState: ProfileState = {
  profiles: [],
  selectedProfile: null,
  loading: false,
  error: null
};

// Async thunks
export const fetchProfiles = createAsyncThunk('profiles/fetchProfiles', async (_, { rejectWithValue }) => {
  try {
    const response = await profilesApi.getProfiles();
    return response.data;
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch profiles');
  }
});

export const fetchProfileById = createAsyncThunk(
  'profiles/fetchProfileById', 
  async (profileId: string, { rejectWithValue }) => {
    try {
      const response = await profilesApi.getProfile(profileId);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch profile');
    }
  }
);

export const createProfile = createAsyncThunk(
  'profiles/createProfile',
  async (profileData: ProfileCreate, { rejectWithValue }) => {
    try {
      const response = await profilesApi.createProfile(profileData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create profile');
    }
  }
);

export const updateProfile = createAsyncThunk(
  'profiles/updateProfile',
  async ({ profileId, profileData }: { profileId: string; profileData: ProfileUpdate }, { rejectWithValue }) => {
    try {
      const response = await profilesApi.updateProfile(profileId, profileData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update profile');
    }
  }
);

export const deleteProfile = createAsyncThunk(
  'profiles/deleteProfile',
  async (profileId: string, { rejectWithValue }) => {
    try {
      await profilesApi.deleteProfile(profileId);
      return profileId;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete profile');
    }
  }
);

// Slice
const profileSlice = createSlice({
  name: 'profiles',
  initialState,
  reducers: {
    clearSelectedProfile: (state) => {
      state.selectedProfile = null;
    },
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    // Fetch all profiles
    builder.addCase(fetchProfiles.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchProfiles.fulfilled, (state, action: PayloadAction<ProfileResponse[]>) => {
      state.loading = false;
      state.profiles = action.payload;
    });
    builder.addCase(fetchProfiles.rejected, (state, action) => {
      state.loading = false;
      state.error = action.payload as string;
    });

    // Fetch profile by ID
    builder.addCase(fetchProfileById.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchProfileById.fulfilled, (state, action: PayloadAction<ProfileResponse>) => {
      state.loading = false;
      state.selectedProfile = action.payload;
    });
    builder.addCase(fetchProfileById.rejected, (state, action) => {
      state.loading = false;
      state.error = action.payload as string;
    });

    // Create profile
    builder.addCase(createProfile.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(createProfile.fulfilled, (state, action: PayloadAction<ProfileResponse>) => {
      state.loading = false;
      state.profiles.push(action.payload);
      state.selectedProfile = action.payload;
    });
    builder.addCase(createProfile.rejected, (state, action) => {
      state.loading = false;
      state.error = action.payload as string;
    });

    // Update profile
    builder.addCase(updateProfile.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(updateProfile.fulfilled, (state, action: PayloadAction<ProfileResponse>) => {
      state.loading = false;
      
      // Update in profiles array
      const index = state.profiles.findIndex(p => p.profile_id === action.payload.profile_id);
      if (index !== -1) {
        state.profiles[index] = action.payload;
      }
      
      // Update selected profile if it matches
      if (state.selectedProfile?.profile_id === action.payload.profile_id) {
        state.selectedProfile = action.payload;
      }
    });
    builder.addCase(updateProfile.rejected, (state, action) => {
      state.loading = false;
      state.error = action.payload as string;
    });

    // Delete profile
    builder.addCase(deleteProfile.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(deleteProfile.fulfilled, (state, action: PayloadAction<string>) => {
      state.loading = false;
      state.profiles = state.profiles.filter(p => p.profile_id !== action.payload);
      
      // Clear selected profile if it was deleted
      if (state.selectedProfile?.profile_id === action.payload) {
        state.selectedProfile = null;
      }
    });
    builder.addCase(deleteProfile.rejected, (state, action) => {
      state.loading = false;
      state.error = action.payload as string;
    });
  }
});

export const { clearSelectedProfile, clearError } = profileSlice.actions;
export default profileSlice.reducer;