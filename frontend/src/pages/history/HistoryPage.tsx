import React, { useState } from 'react';
import {
  Container,
  Paper,
  Tabs,
  Tab,
  Box,
  Typography,
  Button,
  Grid,
  Divider,
  Alert,
} from '@mui/material';
import {
  Home as HomeIcon,
  Business as BusinessIcon,
  PictureAsPdf as PdfIcon,
  SimCardDownload as DownloadIcon,
} from '@mui/icons-material';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import AddressHistoryList from '../../components/history/AddressHistoryList';
import EmploymentHistoryList from '../../components/history/EmploymentHistoryList';
import AddressForm from '../../components/history/AddressForm';
import EmployerForm from '../../components/history/EmployerForm';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`history-tabpanel-${index}`}
      aria-labelledby={`history-tab-${index}`}
      {...other}
    >
      {value === index && <Box p={3}>{children}</Box>}
    </div>
  );
};

const HistoryPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [isAddressFormOpen, setIsAddressFormOpen] = useState(false);
  const [isEmployerFormOpen, setIsEmployerFormOpen] = useState(false);
  const { h1bValidation } = useSelector((state: RootState) => state.history);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={8}>
            <Typography variant="h5" gutterBottom>
              Address & Employment History
            </Typography>
            <Typography variant="body1" color="textSecondary">
              Manage your residence and employment records for immigration purposes.
            </Typography>
          </Grid>
          <Grid item xs={12} md={4} sx={{ textAlign: 'right' }}>
            <Button
              variant="outlined"
              startIcon={<HomeIcon />}
              onClick={() => setIsAddressFormOpen(true)}
              sx={{ mr: 1 }}
            >
              New Address
            </Button>
            <Button
              variant="outlined"
              startIcon={<BusinessIcon />}
              onClick={() => setIsEmployerFormOpen(true)}
            >
              New Employer
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {h1bValidation && h1bValidation.issues.length > 0 && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="subtitle1">H1-B Compliance Issues Detected:</Typography>
          <ul>
            {h1bValidation.issues.map((issue, index) => (
              <li key={index}>{issue}</li>
            ))}
          </ul>
        </Alert>
      )}

      <Paper>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            aria-label="history tabs"
            indicatorColor="primary"
            textColor="primary"
          >
            <Tab
              icon={<HomeIcon />}
              label="Address History"
              id="history-tab-0"
              aria-controls="history-tabpanel-0"
            />
            <Tab
              icon={<BusinessIcon />}
              label="Employment History"
              id="history-tab-1"
              aria-controls="history-tabpanel-1"
            />
          </Tabs>
        </Box>
        <TabPanel value={tabValue} index={0}>
          <AddressHistoryList onAddClick={() => setTabValue(0)} />
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <EmploymentHistoryList onAddClick={() => setTabValue(1)} />
        </TabPanel>
      </Paper>

      {/* Add Address Dialog */}
      <AddressForm
        open={isAddressFormOpen}
        onClose={() => setIsAddressFormOpen(false)}
        onSuccess={() => {
          setIsAddressFormOpen(false);
          setTabValue(0); // Switch to Address History tab
        }}
      />

      {/* Add Employer Dialog */}
      <EmployerForm
        open={isEmployerFormOpen}
        onClose={() => setIsEmployerFormOpen(false)}
        onSuccess={() => {
          setIsEmployerFormOpen(false);
          setTabValue(1); // Switch to Employment History tab
        }}
      />
    </Container>
  );
};

export default HistoryPage;