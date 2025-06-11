import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  FormControlLabel,
  Checkbox,
  Button,
  Grid,
  Alert,
  Typography,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../store';
import { createAddressHistory, updateAddressHistory, fetchAddresses } from '../../store/slices/historySlice';
import { AddressHistory, AddressHistoryCreate, AddressHistoryUpdate, Address } from '../../api/history';
import { format, parseISO } from 'date-fns';

interface AddressHistoryFormProps {
  open: boolean;
  onClose: () => void;
  addressHistory?: AddressHistory;
  onSuccess?: () => void;
}

const AddressHistoryForm: React.FC<AddressHistoryFormProps> = ({
  open,
  onClose,
  addressHistory,
  onSuccess,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const { loading, error, addresses } = useSelector((state: RootState) => state.history);
  const [localError, setLocalError] = useState<string | null>(null);

  const [formData, setFormData] = useState<AddressHistoryCreate>({
    address_id: '',
    start_date: new Date().toISOString().split('T')[0],
    end_date: '',
    is_current: true,
    address_type: 'residential',
    verification_document_id: '',
  });

  // Load addresses if not already loaded
  useEffect(() => {
    if (addresses.length === 0) {
      dispatch(fetchAddresses());
    }
  }, [dispatch, addresses.length]);

  // Initialize form data when editing
  useEffect(() => {
    if (addressHistory) {
      setFormData({
        address_id: addressHistory.address_id,
        start_date: addressHistory.start_date.split('T')[0],
        end_date: addressHistory.end_date ? addressHistory.end_date.split('T')[0] : '',
        is_current: addressHistory.is_current,
        address_type: addressHistory.address_type || 'residential',
        verification_document_id: addressHistory.verification_document_id || '',
      });
    } else {
      // Reset form for new entry
      setFormData({
        address_id: '',
        start_date: new Date().toISOString().split('T')[0],
        end_date: '',
        is_current: true,
        address_type: 'residential',
        verification_document_id: '',
      });
    }
    setLocalError(null);
  }, [addressHistory, open]);

  const addressTypes = [
    { value: 'residential', label: 'Residential' },
    { value: 'mailing', label: 'Mailing' },
    { value: 'work', label: 'Work' },
    { value: 'other', label: 'Other' },
  ];

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    // If setting as current, clear end date
    if (field === 'is_current' && value === true) {
      setFormData((prev) => ({ ...prev, end_date: '' }));
    }
  };

  const formatAddressForDisplay = (address: Address): string => {
    let displayText = address.street_address_1;
    
    if (address.city_name) {
      displayText += `, ${address.city_name}`;
    }
    
    if (address.state_name) {
      displayText += `, ${address.state_name}`;
    }
    
    if (address.zip_code) {
      displayText += ` ${address.zip_code}`;
    }
    
    if (address.country_name) {
      displayText += `, ${address.country_name}`;
    }
    
    return displayText;
  };

  const handleSubmit = async () => {
    // Validate required fields
    if (!formData.address_id || !formData.start_date) {
      setLocalError('Address and start date are required.');
      return;
    }

    // Make sure end date is after start date
    if (formData.end_date && formData.start_date > formData.end_date) {
      setLocalError('End date must be after start date.');
      return;
    }

    try {
      // Clean up the data before submission
      const cleanedData = {
        ...formData,
        // Ensure verification_document_id is null if empty string
        verification_document_id: formData.verification_document_id ? formData.verification_document_id : null,
        // Ensure end_date is null if empty string
        end_date: formData.end_date ? formData.end_date : null,
      };

      if (addressHistory) {
        // Update existing record
        await dispatch(
          updateAddressHistory({
            historyId: addressHistory.address_history_id,
            historyData: cleanedData as AddressHistoryUpdate,
          })
        ).unwrap();
      } else {
        // Create new record
        await dispatch(createAddressHistory(cleanedData)).unwrap();
      }

      console.log('Data submitted successfully:', cleanedData);
      onSuccess?.();
      onClose();
    } catch (err: any) {
      console.error('Error submitting data:', err);
      setLocalError(err.message || 'Failed to save address history.');
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {addressHistory ? 'Edit Address History' : 'Add Address History'}
      </DialogTitle>

      <DialogContent>
        {(error || localError) && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error || localError}
          </Alert>
        )}

        <Grid container spacing={2} sx={{ mt: 1 }}>
          {/* Address */}
          <Grid item xs={12}>
            <FormControl fullWidth required>
              <InputLabel>Address</InputLabel>
              <Select
                value={formData.address_id}
                label="Address"
                onChange={(e) => handleInputChange('address_id', e.target.value)}
              >
                {addresses.map((address) => (
                  <MenuItem key={address.address_id} value={address.address_id}>
                    {formatAddressForDisplay(address)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Address Type */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Address Type</InputLabel>
              <Select
                value={formData.address_type}
                label="Address Type"
                onChange={(e) => handleInputChange('address_type', e.target.value)}
              >
                {addressTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Is Current */}
          <Grid item xs={12} sm={6}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.is_current}
                  onChange={(e) => handleInputChange('is_current', e.target.checked)}
                />
              }
              label="Current Address"
            />
            <Typography variant="caption" display="block">
              Note: If set as current, any other current address of the same type will be updated.
            </Typography>
          </Grid>

          {/* Start Date */}
          <Grid item xs={12} sm={6}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Start Date *"
                value={formData.start_date ? new Date(formData.start_date) : null}
                onChange={(date) => handleInputChange('start_date', date ? format(date, 'yyyy-MM-dd') : '')}
                slotProps={{ textField: { fullWidth: true, required: true } }}
              />
            </LocalizationProvider>
          </Grid>

          {/* End Date - Only shown if not current */}
          <Grid item xs={12} sm={6}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="End Date"
                value={formData.end_date ? new Date(formData.end_date) : null}
                onChange={(date) => handleInputChange('end_date', date ? format(date, 'yyyy-MM-dd') : '')}
                slotProps={{ 
                  textField: { 
                    fullWidth: true,
                    disabled: formData.is_current,
                    helperText: formData.is_current ? 'Not applicable for current address' : undefined
                  } 
                }}
              />
            </LocalizationProvider>
          </Grid>

          {/* Verification Document ID */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Verification Document ID (Optional)"
              value={formData.verification_document_id || ''}
              onChange={(e) => {
                // Only set the UUID if there's a value, otherwise set to undefined/null
                const value = e.target.value.trim() ? e.target.value : null;
                handleInputChange('verification_document_id', value);
              }}
              helperText="Enter a document ID if this address has supporting documentation"
            />
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          color="primary"
          disabled={loading}
        >
          {loading ? 'Saving...' : (addressHistory ? 'Update' : 'Add')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddressHistoryForm;