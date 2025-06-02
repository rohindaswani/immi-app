import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Grid,
  Fab,
  useTheme,
  useMediaQuery,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add as AddIcon,
  Timeline as TimelineIcon,
  Dashboard as DashboardIcon,
  FilterList as FilterListIcon,
} from '@mui/icons-material';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../../store';
import TimelineVisualization from '../../components/timeline/TimelineVisualization';
import TimelineDashboard from '../../components/timeline/TimelineDashboard';
import TimelineFilters from '../../components/timeline/TimelineFilters';
import TimelineEventForm from '../../components/timeline/TimelineEventForm';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`timeline-tabpanel-${index}`}
      aria-labelledby={`timeline-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const TimelinePage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const dispatch = useDispatch<AppDispatch>();
  
  const [currentTab, setCurrentTab] = useState(0);
  const [eventFormOpen, setEventFormOpen] = useState(false);
  const [filters, setFilters] = useState({});

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const handleCreateEvent = () => {
    setEventFormOpen(true);
  };

  const handleEventFormClose = () => {
    setEventFormOpen(false);
  };

  const handleEventFormSuccess = () => {
    // Refresh data if needed
    setEventFormOpen(false);
  };

  const handleFilterChange = (newFilters: any) => {
    setFilters(newFilters);
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TimelineIcon fontSize="large" />
          Immigration Timeline
        </Typography>
        
        {!isMobile && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateEvent}
            size="large"
          >
            Add Event
          </Button>
        )}
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs 
          value={currentTab} 
          onChange={handleTabChange} 
          aria-label="timeline tabs"
          variant={isMobile ? "fullWidth" : "standard"}
        >
          <Tab 
            icon={<DashboardIcon />} 
            label="Dashboard" 
            id="timeline-tab-0"
            aria-controls="timeline-tabpanel-0"
          />
          <Tab 
            icon={<TimelineIcon />} 
            label="Timeline" 
            id="timeline-tab-1"
            aria-controls="timeline-tabpanel-1"
          />
          <Tab 
            icon={<FilterListIcon />} 
            label="Filters" 
            id="timeline-tab-2"
            aria-controls="timeline-tabpanel-2"
          />
        </Tabs>
      </Box>

      {/* Tab Panels */}
      <TabPanel value={currentTab} index={0}>
        <TimelineDashboard />
      </TabPanel>

      <TabPanel value={currentTab} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TimelineVisualization filters={filters} />
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={currentTab} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} lg={4}>
            <TimelineFilters onFilterChange={handleFilterChange} />
          </Grid>
          <Grid item xs={12} lg={8}>
            <TimelineVisualization filters={filters} compact />
          </Grid>
        </Grid>
      </TabPanel>

      {/* Floating Action Button for Mobile */}
      {isMobile && (
        <Fab
          color="primary"
          aria-label="add timeline event"
          onClick={handleCreateEvent}
          sx={{
            position: 'fixed',
            bottom: 16,
            right: 16,
          }}
        >
          <AddIcon />
        </Fab>
      )}

      {/* Event Form Dialog */}
      <TimelineEventForm
        open={eventFormOpen}
        onClose={handleEventFormClose}
        onSuccess={handleEventFormSuccess}
      />
    </Box>
  );
};

export default TimelinePage;