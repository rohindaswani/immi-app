import React from 'react';
import { Container } from '@mui/material';
import ProfileDetail from './ProfileDetail';

const ProfileDetailPage: React.FC = () => {
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <ProfileDetail />
    </Container>
  );
};

export default ProfileDetailPage;