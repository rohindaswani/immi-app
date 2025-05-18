import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  List,
  ListItem,
  Divider,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';

import { RootState } from '../../store';
import { fetchProfiles, deleteProfile } from '../../store/slices/profileSlice';
import { formatDate } from '../../utils/date';

const ProfileList: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { profiles, loading, error } = useSelector((state: RootState) => state.profiles);

  // Fetch profiles on component mount
  useEffect(() => {
    dispatch(fetchProfiles());
  }, [dispatch]);

  const handleCreateProfile = () => {
    navigate('/profiles/new');
  };

  const handleEditProfile = (profileId: string) => {
    navigate(`/profiles/${profileId}/edit`);
  };

  const handleViewProfile = (profileId: string) => {
    navigate(`/profiles/${profileId}`);
  };

  const handleDeleteProfile = (profileId: string) => {
    if (window.confirm('Are you sure you want to delete this profile?')) {
      dispatch(deleteProfile(profileId));
    }
  };

  if (loading && profiles.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h1">
          Immigration Profiles
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleCreateProfile}
        >
          Create Profile
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {profiles.length === 0 ? (
        <Card>
          <CardContent>
            <Typography color="textSecondary" align="center">
              No profiles found. Create your first immigration profile.
            </Typography>
          </CardContent>
          <CardActions sx={{ justifyContent: 'center' }}>
            <Button size="small" color="primary" onClick={handleCreateProfile}>
              Create Profile
            </Button>
          </CardActions>
        </Card>
      ) : (
        <List>
          {profiles.map((profile) => (
            <React.Fragment key={profile.profile_id}>
              <ListItem
                component={Card}
                sx={{ mb: 2, display: 'block', p: 0 }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box>
                      <Typography variant="h6" component="h2">
                        {profile.current_status.status_name}
                      </Typography>
                      <Chip
                        label={profile.current_status.status_code}
                        color="primary"
                        size="small"
                        sx={{ mt: 0.5, mr: 1 }}
                      />
                      <Chip
                        label={profile.current_status.status_category}
                        color="secondary"
                        size="small"
                        sx={{ mt: 0.5 }}
                      />
                    </Box>
                    <Chip
                      label={profile.is_primary_beneficiary ? 'Primary' : 'Dependent'}
                      color={profile.is_primary_beneficiary ? 'success' : 'info'}
                      size="small"
                    />
                  </Box>

                  <Box sx={{ mt: 2 }}>
                    {profile.immigration_goals && (
                      <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                        <strong>Goals:</strong> {profile.immigration_goals}
                      </Typography>
                    )}
                    
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', mt: 1 }}>
                      {profile.most_recent_entry_date && (
                        <Typography variant="body2" color="textSecondary" sx={{ mr: 3 }}>
                          <strong>Last Entry:</strong> {formatDate(profile.most_recent_entry_date)}
                        </Typography>
                      )}
                      
                      {profile.authorized_stay_until && (
                        <Typography variant="body2" color="textSecondary" sx={{ mr: 3 }}>
                          <strong>Authorized Until:</strong> {formatDate(profile.authorized_stay_until)}
                        </Typography>
                      )}
                      
                      {profile.visa_expiry_date && (
                        <Typography variant="body2" color="textSecondary">
                          <strong>Visa Expires:</strong> {formatDate(profile.visa_expiry_date)}
                        </Typography>
                      )}
                    </Box>
                  </Box>
                </CardContent>

                <Divider />

                <CardActions>
                  <Button size="small" onClick={() => handleViewProfile(profile.profile_id)}>
                    View
                  </Button>
                  <Button
                    size="small"
                    startIcon={<EditIcon />}
                    onClick={() => handleEditProfile(profile.profile_id)}
                  >
                    Edit
                  </Button>
                  <Button
                    size="small"
                    color="error"
                    startIcon={<DeleteIcon />}
                    onClick={() => handleDeleteProfile(profile.profile_id)}
                  >
                    Delete
                  </Button>
                </CardActions>
              </ListItem>
            </React.Fragment>
          ))}
        </List>
      )}
    </Box>
  );
};

export default ProfileList;