import React from 'react';
import { Container } from '@mui/material';
import ProfileList from '../../components/profiles/ProfileList';

const ProfilesPage: React.FC = () => {
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <ProfileList />
    </Container>
  );
};

export default ProfilesPage;