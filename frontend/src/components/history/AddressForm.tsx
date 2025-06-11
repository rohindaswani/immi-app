import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Alert,
  Typography,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../store';
import { createAddress, updateAddress } from '../../store/slices/historySlice';
import { Address, AddressCreate, AddressUpdate } from '../../api/history';

interface AddressFormProps {
  open: boolean;
  onClose: () => void;
  address?: Address;
  onSuccess?: () => void;
}

const AddressForm: React.FC<AddressFormProps> = ({
  open,
  onClose,
  address,
  onSuccess,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const { loading, error } = useSelector((state: RootState) => state.history);
  const [localError, setLocalError] = useState<string | null>(null);

  const [formData, setFormData] = useState<AddressCreate>({
    street_address_1: '',
    street_address_2: '',
    city_id: '',
    state_id: '',
    zip_code: '',
    country_id: '',
    latitude: undefined,
    longitude: undefined,
    address_type: '',
    is_verified: false,
    verification_date: undefined,
  });

  // Mock data for dropdowns - in a real app, these would come from API
  const countries = [
    { id: '123e4567-e89b-12d3-a456-426614174000', name: 'United States' },
    { id: '223e4567-e89b-12d3-a456-426614174000', name: 'Canada' },
    { id: '323e4567-e89b-12d3-a456-426614174000', name: 'Mexico' },
  ];

  const states = [
    { id: '423e4567-e89b-12d3-a456-426614174000', name: 'California', country_id: '123e4567-e89b-12d3-a456-426614174000' },
    { id: '523e4567-e89b-12d3-a456-426614174000', name: 'New York', country_id: '123e4567-e89b-12d3-a456-426614174000' },
    { id: '623e4567-e89b-12d3-a456-426614174000', name: 'Texas', country_id: '123e4567-e89b-12d3-a456-426614174000' },
    { id: '723e4567-e89b-12d3-a456-426614174000', name: 'Ontario', country_id: '223e4567-e89b-12d3-a456-426614174000' },
    { id: '823e4567-e89b-12d3-a456-426614174000', name: 'Quebec', country_id: '223e4567-e89b-12d3-a456-426614174000' },
  ];

  const cities = [
    { id: '923e4567-e89b-12d3-a456-426614174000', name: 'Los Angeles', state_id: '423e4567-e89b-12d3-a456-426614174000' },
    { id: 'a23e4567-e89b-12d3-a456-426614174000', name: 'San Francisco', state_id: '423e4567-e89b-12d3-a456-426614174000' },
    { id: 'b23e4567-e89b-12d3-a456-426614174000', name: 'New York City', state_id: '523e4567-e89b-12d3-a456-426614174000' },
    { id: 'c23e4567-e89b-12d3-a456-426614174000', name: 'Buffalo', state_id: '523e4567-e89b-12d3-a456-426614174000' },
    { id: 'd23e4567-e89b-12d3-a456-426614174000', name: 'Austin', state_id: '623e4567-e89b-12d3-a456-426614174000' },
    { id: 'e23e4567-e89b-12d3-a456-426614174000', name: 'Houston', state_id: '623e4567-e89b-12d3-a456-426614174000' },
    { id: 'f23e4567-e89b-12d3-a456-426614174000', name: 'Toronto', state_id: '723e4567-e89b-12d3-a456-426614174000' },
    { id: '023e4567-e89b-12d3-a456-426614174000', name: 'Montreal', state_id: '823e4567-e89b-12d3-a456-426614174000' },
  ];

  const addressTypes = [
    { value: 'residential', label: 'Residential' },
    { value: 'mailing', label: 'Mailing' },
    { value: 'work', label: 'Work' },
    { value: 'other', label: 'Other' },
  ];

  useEffect(() => {
    if (address) {
      setFormData({
        street_address_1: address.street_address_1,
        street_address_2: address.street_address_2 || '',
        city_id: address.city_id || '',
        state_id: address.state_id || '',
        zip_code: address.zip_code || '',
        country_id: address.country_id,
        latitude: address.latitude,
        longitude: address.longitude,
        address_type: address.address_type || '',
        is_verified: address.is_verified || false,
        verification_date: address.verification_date ? new Date(address.verification_date) : undefined,
      });
    } else {
      // Reset form data for new address
      setFormData({
        street_address_1: '',
        street_address_2: '',
        city_id: '',
        state_id: '',
        zip_code: '',
        country_id: '',
        latitude: undefined,
        longitude: undefined,
        address_type: '',
        is_verified: false,
        verification_date: undefined,
      });
    }
    setLocalError(null);
  }, [address, open]);

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    // Handle country/state changes to reset dependent fields
    if (field === 'country_id') {
      setFormData((prev) => ({ ...prev, state_id: '', city_id: '' }));
    } else if (field === 'state_id') {
      setFormData((prev) => ({ ...prev, city_id: '' }));
    }
  };

  const handleSubmit = async () => {
    // Validate required fields
    if (!formData.street_address_1 || !formData.country_id) {
      setLocalError('Street address and country are required.');
      return;
    }

    try {
      if (address) {
        // Update existing address
        await dispatch(
          updateAddress({
            addressId: address.address_id,
            addressData: formData as AddressUpdate,
          })
        ).unwrap();
      } else {
        // Create new address
        await dispatch(createAddress(formData)).unwrap();
      }

      onSuccess?.();
      onClose();
    } catch (err: any) {
      setLocalError(err.message || 'Failed to save address.');
    }
  };

  // Filter states by selected country
  const filteredStates = states.filter(
    (state) => state.country_id === formData.country_id
  );

  // Filter cities by selected state
  const filteredCities = cities.filter(
    (city) => city.state_id === formData.state_id
  );

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {address ? 'Edit Address' : 'Add New Address'}
      </DialogTitle>

      <DialogContent>
        {(error || localError) && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error || localError}
          </Alert>
        )}

        <Grid container spacing={2} sx={{ mt: 1 }}>
          {/* Street Address 1 */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              required
              label="Street Address 1"
              value={formData.street_address_1}
              onChange={(e) => handleInputChange('street_address_1', e.target.value)}
            />
          </Grid>

          {/* Street Address 2 */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Street Address 2"
              value={formData.street_address_2}
              onChange={(e) => handleInputChange('street_address_2', e.target.value)}
            />
          </Grid>

          {/* Country */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth required>
              <InputLabel>Country</InputLabel>
              <Select
                value={formData.country_id}
                label="Country"
                onChange={(e) => handleInputChange('country_id', e.target.value)}
              >
                {countries.map((country) => (
                  <MenuItem key={country.id} value={country.id}>
                    {country.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* State/Province */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth disabled={!formData.country_id}>
              <InputLabel>State/Province</InputLabel>
              <Select
                value={formData.state_id}
                label="State/Province"
                onChange={(e) => handleInputChange('state_id', e.target.value)}
              >
                {filteredStates.map((state) => (
                  <MenuItem key={state.id} value={state.id}>
                    {state.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* City */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth disabled={!formData.state_id}>
              <InputLabel>City</InputLabel>
              <Select
                value={formData.city_id}
                label="City"
                onChange={(e) => handleInputChange('city_id', e.target.value)}
              >
                {filteredCities.map((city) => (
                  <MenuItem key={city.id} value={city.id}>
                    {city.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Zip/Postal Code */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Zip/Postal Code"
              value={formData.zip_code}
              onChange={(e) => handleInputChange('zip_code', e.target.value)}
            />
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

          {/* Verification */}
          <Grid item xs={12} sm={6}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.is_verified}
                  onChange={(e) => handleInputChange('is_verified', e.target.checked)}
                />
              }
              label="Address Verified"
            />
            {formData.is_verified && (
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="Verification Date"
                  value={formData.verification_date ? new Date(formData.verification_date) : null}
                  onChange={(date) => handleInputChange('verification_date', date)}
                  slotProps={{ textField: { fullWidth: true, size: 'small', sx: { mt: 1 } } }}
                />
              </LocalizationProvider>
            )}
          </Grid>

          {/* Latitude & Longitude */}
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" gutterBottom>
              Coordinates (Optional)
            </Typography>
            <Grid container spacing={1}>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  size="small"
                  label="Latitude"
                  type="number"
                  value={formData.latitude || ''}
                  onChange={(e) => handleInputChange('latitude', parseFloat(e.target.value) || undefined)}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  size="small"
                  label="Longitude"
                  type="number"
                  value={formData.longitude || ''}
                  onChange={(e) => handleInputChange('longitude', parseFloat(e.target.value) || undefined)}
                />
              </Grid>
            </Grid>
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
          {loading ? 'Saving...' : (address ? 'Update' : 'Create')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddressForm;