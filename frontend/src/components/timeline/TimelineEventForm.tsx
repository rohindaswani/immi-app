import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Button,
  Grid,
  Alert,
  Box,
  Slider,
  Typography,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../../store';
import { createTimelineEvent, updateTimelineEvent } from '../../store/slices/timelineSlice';
import { TimelineEvent } from '../../api/timeline';

interface TimelineEventFormProps {
  open: boolean;
  onClose: () => void;
  event?: TimelineEvent;
  onSuccess?: () => void;
}

const TimelineEventForm: React.FC<TimelineEventFormProps> = ({
  open,
  onClose,
  event,
  onSuccess,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    event_title: '',
    description: '',
    event_date: new Date(),
    event_type: 'other',
    reference_id: '',
    reference_table: '',
    document_id: ''
  });

  useEffect(() => {
    if (event) {
      setFormData({
        event_title: event.event_title || '',
        description: event.description || '',
        event_date: new Date(event.event_date),
        event_type: event.event_type || 'other',
        reference_id: event.reference_id || '',
        reference_table: event.reference_table || '',
        document_id: event.document_id || ''
      });
    } else {
      setFormData({
        event_title: '',
        description: '',
        event_date: new Date(),
        event_type: 'other',
        reference_id: '',
        reference_table: '',
        document_id: ''
      });
    }
  }, [event, open]);

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

  // Removed categories, subtypes, priorities, statuses, and immigrationStatuses arrays 
  // since they're not in the database schema

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  // UUID validation function
  const isValidUUID = (uuid: string) => {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    return uuid === '' || uuidRegex.test(uuid);
  };

  const handleSubmit = async () => {
    if (!formData.event_title.trim()) {
      setError('Title is required');
      return;
    }

    // Validate UUID fields
    if (formData.reference_id && !isValidUUID(formData.reference_id)) {
      setError('Reference ID must be a valid UUID or empty');
      return;
    }
    
    if (formData.document_id && !isValidUUID(formData.document_id)) {
      setError('Document ID must be a valid UUID or empty');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const eventData = {
        ...formData,
        event_date: formData.event_date.toISOString(),
        reference_id: formData.reference_id ? formData.reference_id : null,
        reference_table: formData.reference_table || undefined,
        document_id: formData.document_id ? formData.document_id : null,
        // Adding fields from database model
        event_category: "other",  // Default value
        event_subtype: null,
        priority: "medium", // Default value
        is_milestone: false, // Default value
        event_status: "completed" // Default value
      };

      if (event) {
        await dispatch(updateTimelineEvent({ 
          eventId: event.event_id, // Changed from id to event_id to match our schema
          updates: eventData 
        })).unwrap();
      } else {
        await dispatch(createTimelineEvent(eventData)).unwrap();
      }

      onSuccess?.();
      onClose();
    } catch (err: any) {
      setError(err.message || 'An error occurred while saving the event');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {event ? 'Edit Timeline Event' : 'Create New Timeline Event'}
      </DialogTitle>
      
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={2} sx={{ mt: 1 }}>
          {/* Title */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Title"
              required
              value={formData.event_title}
              onChange={(e) => handleInputChange('event_title', e.target.value)}
            />
          </Grid>

          {/* Description */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description"
              multiline
              rows={3}
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
            />
          </Grid>

          {/* Event Date */}
          <Grid item xs={12} sm={6}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Event Date"
                value={formData.event_date}
                onChange={(date) => handleInputChange('event_date', date || new Date())}
                slotProps={{ textField: { fullWidth: true } }}
              />
            </LocalizationProvider>
          </Grid>

          {/* Event Type */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Event Type</InputLabel>
              <Select
                value={formData.event_type}
                label="Event Type"
                onChange={(e) => handleInputChange('event_type', e.target.value)}
              >
                {eventTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Reference ID */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Reference ID (valid UUID or empty)"
              helperText="Must be a valid UUID if provided"
              value={formData.reference_id || ''}
              onChange={(e) => handleInputChange('reference_id', e.target.value)}
            />
          </Grid>

          {/* Reference Table */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Reference Table"
              value={formData.reference_table || ''}
              onChange={(e) => handleInputChange('reference_table', e.target.value)}
            />
          </Grid>

          {/* Document ID */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Document ID (valid UUID or empty)"
              helperText="Must be a valid UUID if provided"
              value={formData.document_id || ''}
              onChange={(e) => handleInputChange('document_id', e.target.value)}
            />
          </Grid>

          {/* Removed Notes field as it's not in the database schema */}
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
        >
          {loading ? 'Saving...' : (event ? 'Update' : 'Create')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TimelineEventForm;