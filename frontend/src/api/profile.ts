import apiClient from './client';

// Profile types
export interface ImmigrationStatus {
  status_code: string;
  status_name: string;
  status_category: string;
}

export interface ProfileBase {
  current_status_code: string;
  most_recent_i94_number?: string;
  most_recent_entry_date?: string; // ISO date string
  immigration_goals?: string;
  alien_registration_number?: string;
  authorized_stay_until?: string; // ISO date string
  ead_expiry_date?: string; // ISO date string
  visa_expiry_date?: string; // ISO date string
  passport_number?: string;
  passport_country_id?: string;
  passport_expiry_date?: string; // ISO date string
  is_primary_beneficiary: boolean;
  primary_beneficiary_id?: string;
  profile_type: string; // "primary" or "dependent"
  notes?: string;
}

export interface ProfileCreate extends ProfileBase {}

export interface ProfileUpdate {
  current_status_code?: string;
  most_recent_i94_number?: string;
  most_recent_entry_date?: string;
  immigration_goals?: string;
  alien_registration_number?: string;
  authorized_stay_until?: string;
  ead_expiry_date?: string;
  visa_expiry_date?: string;
  passport_number?: string;
  passport_country_id?: string;
  passport_expiry_date?: string;
  is_primary_beneficiary?: boolean;
  primary_beneficiary_id?: string;
  profile_type?: string;
  notes?: string;
}

export interface ProfileResponse extends ProfileBase {
  profile_id: string;
  user_id: string;
  current_status: ImmigrationStatus;
}

// API calls
const profilesApi = {
  // Get all profiles for the current user
  getProfiles: () => 
    apiClient.get<ProfileResponse[]>('/profiles'),
  
  // Get a specific profile by ID
  getProfile: (profileId: string) => 
    apiClient.get<ProfileResponse>(`/profiles/${profileId}`),
  
  // Create a new profile
  createProfile: (profileData: ProfileCreate) => 
    apiClient.post<ProfileResponse>('/profiles', profileData),
  
  // Update a profile
  updateProfile: (profileId: string, profileData: ProfileUpdate) => 
    apiClient.put<ProfileResponse>(`/profiles/${profileId}`, profileData),
  
  // Delete a profile
  deleteProfile: (profileId: string) => 
    apiClient.delete(`/profiles/${profileId}`)
};

export default profilesApi;