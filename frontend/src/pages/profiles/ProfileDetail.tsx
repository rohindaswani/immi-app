import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import DeleteIcon from '@mui/icons-material/Delete';
import WarningIcon from '@mui/icons-material/Warning';

import { RootState } from '../../store';
import { fetchProfileById, deleteProfile } from '../../store/slices/profileSlice';
import { formatDate, getDaysRemaining, isDateWithinDays } from '../../utils/date';

const ProfileDetail: React.FC = () => {
  const { profileId } = useParams<{ profileId: string }>();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { selectedProfile: profile, loading, error } = useSelector((state: RootState) => state.profiles);

  useEffect(() => {
    if (profileId) {
      dispatch(fetchProfileById(profileId));
    }
  }, [dispatch, profileId]);

  const handleEdit = () => {
    navigate(`/profiles/${profileId}/edit`);
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this profile?')) {
      dispatch(deleteProfile(profileId!));
      navigate('/profiles');
    }
  };

  const handleBack = () => {
    navigate('/profiles');
  };

  if (loading && !profile) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="error">{error}</Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={handleBack}
          sx={{ mt: 2 }}
        >
          Back to Profiles
        </Button>
      </Box>
    );
  }

  if (!profile) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="info">Profile not found</Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={handleBack}
          sx={{ mt: 2 }}
        >
          Back to Profiles
        </Button>
      </Box>
    );
  }

  // Check for upcoming expirations
  const visaExpiring = profile.visa_expiry_date && isDateWithinDays(profile.visa_expiry_date, 90);
  const stayExpiring = profile.authorized_stay_until && isDateWithinDays(profile.authorized_stay_until, 90);
  const passportExpiring = profile.passport_expiry_date && isDateWithinDays(profile.passport_expiry_date, 180);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Button startIcon={<ArrowBackIcon />} onClick={handleBack}>
          Back to Profiles
        </Button>
        <Box>
          <Button
            variant="contained"
            color="primary"
            startIcon={<EditIcon />}
            onClick={handleEdit}
            sx={{ mr: 1 }}
          >
            Edit Profile
          </Button>
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleDelete}
          >
            Delete
          </Button>
        </Box>
      </Box>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <Box>
                <Typography variant="h5" component="h1">
                  {profile.current_status.status_name}
                </Typography>
                <Box sx={{ mt: 1 }}>
                  <Chip
                    label={profile.current_status.status_code}
                    color="primary"
                    sx={{ mr: 1 }}
                  />
                  <Chip
                    label={profile.current_status.status_category}
                    color="secondary"
                  />
                  <Chip
                    label={profile.is_primary_beneficiary ? 'Primary Beneficiary' : 'Dependent'}
                    color={profile.is_primary_beneficiary ? 'success' : 'info'}
                    sx={{ ml: 1 }}
                  />
                </Box>
              </Box>
            </Box>
          </Grid>

          {(visaExpiring || stayExpiring || passportExpiring) && (
            <Grid item xs={12}>
              <Alert severity="warning" icon={<WarningIcon />}>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                  Upcoming Expirations:
                </Typography>
                <Box sx={{ ml: 2 }}>
                  {visaExpiring && (
                    <Typography variant="body2">
                      • Visa expires on {formatDate(profile.visa_expiry_date!)} 
                      ({getDaysRemaining(profile.visa_expiry_date!)} days remaining)
                    </Typography>
                  )}
                  {stayExpiring && (
                    <Typography variant="body2">
                      • Authorized stay ends on {formatDate(profile.authorized_stay_until!)} 
                      ({getDaysRemaining(profile.authorized_stay_until!)} days remaining)
                    </Typography>
                  )}
                  {passportExpiring && (
                    <Typography variant="body2">
                      • Passport expires on {formatDate(profile.passport_expiry_date!)} 
                      ({getDaysRemaining(profile.passport_expiry_date!)} days remaining)
                    </Typography>
                  )}
                </Box>
              </Alert>
            </Grid>
          )}

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="h6" gutterBottom>
              Immigration Details
            </Typography>

            <List>
              {profile.immigration_goals && (
                <ListItem divider>
                  <ListItemText
                    primary="Immigration Goals"
                    secondary={profile.immigration_goals}
                  />
                </ListItem>
              )}

              {profile.most_recent_i94_number && (
                <ListItem divider>
                  <ListItemText
                    primary="Most Recent I-94 Number"
                    secondary={profile.most_recent_i94_number}
                  />
                </ListItem>
              )}

              {profile.most_recent_entry_date && (
                <ListItem divider>
                  <ListItemText
                    primary="Most Recent Entry Date"
                    secondary={formatDate(profile.most_recent_entry_date)}
                  />
                </ListItem>
              )}

              {profile.authorized_stay_until && (
                <ListItem divider>
                  <ListItemText
                    primary="Authorized Stay Until"
                    secondary={formatDate(profile.authorized_stay_until)}
                  />
                </ListItem>
              )}

              {profile.visa_expiry_date && (
                <ListItem divider>
                  <ListItemText
                    primary="Visa Expiry Date"
                    secondary={formatDate(profile.visa_expiry_date)}
                  />
                </ListItem>
              )}

              {profile.ead_expiry_date && (
                <ListItem divider>
                  <ListItemText
                    primary="EAD Expiry Date"
                    secondary={formatDate(profile.ead_expiry_date)}
                  />
                </ListItem>
              )}

              {profile.alien_registration_number && (
                <ListItem divider>
                  <ListItemText
                    primary="Alien Registration Number"
                    secondary={profile.alien_registration_number}
                  />
                </ListItem>
              )}
            </List>
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="h6" gutterBottom>
              Passport Details
            </Typography>

            <List>
              {profile.passport_number && (
                <ListItem divider>
                  <ListItemText
                    primary="Passport Number"
                    secondary={profile.passport_number}
                  />
                </ListItem>
              )}

              {profile.passport_expiry_date && (
                <ListItem divider>
                  <ListItemText
                    primary="Passport Expiry Date"
                    secondary={formatDate(profile.passport_expiry_date)}
                  />
                </ListItem>
              )}
            </List>
          </Grid>

          {profile.notes && (
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Notes
              </Typography>
              <Typography variant="body1">{profile.notes}</Typography>
            </Grid>
          )}
        </Grid>
      </Paper>
    </Box>
  );
};

export default ProfileDetail;