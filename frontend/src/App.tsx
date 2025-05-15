import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Box from '@mui/material/Box';

import MainLayout from './components/layouts/MainLayout';
import Home from './pages/Home';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import Dashboard from './pages/dashboard/Dashboard';
import NotFound from './pages/NotFound';

const App: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Home />} />
          <Route path="dashboard" element={<Dashboard />} />
          {/* Add more routes as they are implemented */}
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </Box>
  );
};

export default App;