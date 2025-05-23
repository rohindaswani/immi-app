import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Box from '@mui/material/Box';

import MainLayout from './components/layouts/MainLayout';
import AuthProvider from './components/auth/AuthProvider';
import ProtectedRoute from './components/auth/ProtectedRoute';
import Home from './pages/Home';
import Login from './pages/auth/Login';
import AuthSuccess from './pages/auth/AuthSuccess';
import Dashboard from './pages/dashboard/Dashboard';
import ProfilesPage from './pages/profiles/ProfilesPage';
import ProfileDetailPage from './pages/profiles/ProfileDetailPage';
import { DocumentsPage } from './pages/documents/DocumentsPage';
import NotFound from './pages/NotFound';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/auth/success" element={<AuthSuccess />} />
          
          {/* Base layout for all routes */}
          <Route path="/" element={<MainLayout />}>
            {/* Public home page */}
            <Route index element={<Home />} />
            
            {/* Protected routes */}
            <Route element={<ProtectedRoute />}>
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="profiles" element={<ProfilesPage />} />
              <Route path="profiles/:profileId" element={<ProfileDetailPage />} />
              <Route path="documents" element={<DocumentsPage />} />
              {/* Add more protected routes here */}
            </Route>
            
            {/* Not found route */}
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </Box>
    </AuthProvider>
  );
};

export default App;