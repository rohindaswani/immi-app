import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  FormControlLabel,
  Checkbox,
  Button,
  Grid,
  Chip,
  Collapse,
  IconButton,
} from '@mui/material';
import {
  FilterList as FilterListIcon,
  Clear as ClearIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import { setFilters, clearFilters, fetchTimelineEvents } from '../../store/slices/timelineSlice';

interface TimelineFiltersProps {
  onFilterChange?: (filters: any) => void;
}

const TimelineFilters: React.FC<TimelineFiltersProps> = ({ onFilterChange }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { filters } = useSelector((state: RootState) => state.timeline);
  
  const [localFilters, setLocalFilters] = useState(filters);
  const [expanded, setExpanded] = useState(false);

  const eventTypes = [
    { value: 'application', label: 'Application' },
    { value: 'interview', label: 'Interview' },
    { value: 'decision', label: 'Decision' },
    { value: 'document_request', label: 'Document Request' },
    { value: 'deadline', label: 'Deadline' },
    { value: 'status_change', label: 'Status Change' },
    { value: 'travel', label: 'Travel' },
    { value: 'other', label: 'Other' },
  ];

  // Removed categories and priorities arrays as they don't exist in DB

  const handleFilterChange = (field: string, value: any) => {
    const newFilters = { ...localFilters, [field]: value };
    setLocalFilters(newFilters);
  };

  const applyFilters = () => {
    dispatch(setFilters(localFilters));
    dispatch(fetchTimelineEvents(localFilters));
    onFilterChange?.(localFilters);
  };

  const clearAllFilters = () => {
    const clearedFilters = { skip: 0, limit: 100 };
    setLocalFilters(clearedFilters);
    dispatch(clearFilters());
    dispatch(fetchTimelineEvents(clearedFilters));
    onFilterChange?.(clearedFilters);
  };

  const getActiveFilterCount = () => {
    return Object.keys(localFilters).filter(key => 
      key !== 'skip' && 
      key !== 'limit' && 
      localFilters[key] !== undefined && 
      localFilters[key] !== null && 
      localFilters[key] !== ''
    ).length;
  };

  const activeFilterCount = getActiveFilterCount();

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FilterListIcon />
            Timeline Filters
            {activeFilterCount > 0 && (
              <Chip 
                label={`${activeFilterCount} active`} 
                size="small" 
                color="primary" 
                variant="outlined" 
              />
            )}
          </Typography>
          
          <Box>
            <IconButton onClick={() => setExpanded(!expanded)} size="small">
              {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        </Box>

        {/* Removed Quick Filters as is_milestone and is_deadline don't exist in DB */}
        <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
          {/* No quick filters available with the simplified schema */}
        </Box>

        <Collapse in={expanded}>
          <Grid container spacing={2}>
            {/* Event Type */}
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Event Type</InputLabel>
                <Select
                  value={localFilters.event_type || ''}
                  label="Event Type"
                  onChange={(e) => handleFilterChange('event_type', e.target.value || undefined)}
                >
                  <MenuItem value="">All Types</MenuItem>
                  {eventTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Removed Category and Priority filters as they don't exist in DB */}
            {/* Reference Table Filter */}
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Reference Table"
                value={localFilters.reference_table || ''}
                onChange={(e) => handleFilterChange('reference_table', e.target.value || undefined)}
              />
            </Grid>

            {/* Limit */}
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Show Results</InputLabel>
                <Select
                  value={localFilters.limit || 100}
                  label="Show Results"
                  onChange={(e) => handleFilterChange('limit', e.target.value)}
                >
                  <MenuItem value={25}>25 items</MenuItem>
                  <MenuItem value={50}>50 items</MenuItem>
                  <MenuItem value={100}>100 items</MenuItem>
                  <MenuItem value={200}>200 items</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Date Range */}
            <Grid item xs={12} sm={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="Start Date"
                  value={localFilters.start_date ? new Date(localFilters.start_date) : null}
                  onChange={(date) => handleFilterChange('start_date', date?.toISOString().split('T')[0])}
                  slotProps={{ textField: { size: 'small', fullWidth: true } }}
                />
              </LocalizationProvider>
            </Grid>

            <Grid item xs={12} sm={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="End Date"
                  value={localFilters.end_date ? new Date(localFilters.end_date) : null}
                  onChange={(date) => handleFilterChange('end_date', date?.toISOString().split('T')[0])}
                  slotProps={{ textField: { size: 'small', fullWidth: true } }}
                />
              </LocalizationProvider>
            </Grid>
          </Grid>
        </Collapse>

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 1, mt: 2, justifyContent: 'flex-end' }}>
          <Button
            variant="outlined"
            startIcon={<ClearIcon />}
            onClick={clearAllFilters}
            disabled={activeFilterCount === 0}
            size="small"
          >
            Clear All
          </Button>
          <Button
            variant="contained"
            startIcon={<FilterListIcon />}
            onClick={applyFilters}
            size="small"
          >
            Apply Filters
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default TimelineFilters;