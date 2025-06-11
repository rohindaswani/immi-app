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
import { createEmployer, updateEmployer, fetchAddresses } from '../../store/slices/historySlice';
import { Employer, EmployerCreate, EmployerUpdate, Address } from '../../api/history';
import { format } from 'date-fns';

interface EmployerFormProps {
  open: boolean;
  onClose: () => void;
  employer?: Employer;
  onSuccess?: () => void;
}

const EmployerForm: React.FC<EmployerFormProps> = ({
  open,
  onClose,
  employer,
  onSuccess,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const { loading, error, addresses } = useSelector((state: RootState) => state.history);
  const [localError, setLocalError] = useState<string | null>(null);

  const [formData, setFormData] = useState<EmployerCreate>({
    company_name: '',
    company_ein: '',
    company_type: '',
    industry: '',
    address_id: '',
    contact_name: '',
    contact_email: '',
    contact_phone: '',
    is_verified: false,
    verification_date: '',
  });

  // Load addresses if not already loaded
  useEffect(() => {
    if (addresses.length === 0) {
      dispatch(fetchAddresses());
    }
  }, [dispatch, addresses.length]);

  // Initialize form data when editing
  useEffect(() => {
    if (employer) {
      setFormData({
        company_name: employer.company_name,
        company_ein: employer.company_ein || '',
        company_type: employer.company_type || '',
        industry: employer.industry || '',
        address_id: employer.address_id || '',
        contact_name: employer.contact_name || '',
        contact_email: employer.contact_email || '',
        contact_phone: employer.contact_phone || '',
        is_verified: employer.is_verified || false,
        verification_date: employer.verification_date ? employer.verification_date.split('T')[0] : '',
      });
    } else {
      // Reset form for new employer
      setFormData({
        company_name: '',
        company_ein: '',
        company_type: '',
        industry: '',
        address_id: '',
        contact_name: '',
        contact_email: '',
        contact_phone: '',
        is_verified: false,
        verification_date: '',
      });
    }
    setLocalError(null);
  }, [employer, open]);

  const companyTypes = [
    { value: 'corporation', label: 'Corporation' },
    { value: 'llc', label: 'Limited Liability Company (LLC)' },
    { value: 'partnership', label: 'Partnership' },
    { value: 'sole_proprietorship', label: 'Sole Proprietorship' },
    { value: 'non_profit', label: 'Non-Profit Organization' },
    { value: 'government', label: 'Government Entity' },
    { value: 'other', label: 'Other' },
  ];

  const industries = [
    { value: 'technology', label: 'Technology' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'finance', label: 'Finance & Banking' },
    { value: 'education', label: 'Education' },
    { value: 'retail', label: 'Retail' },
    { value: 'manufacturing', label: 'Manufacturing' },
    { value: 'construction', label: 'Construction' },
    { value: 'hospitality', label: 'Hospitality & Tourism' },
    { value: 'legal', label: 'Legal Services' },
    { value: 'media', label: 'Media & Entertainment' },
    { value: 'transportation', label: 'Transportation & Logistics' },
    { value: 'agriculture', label: 'Agriculture' },
    { value: 'energy', label: 'Energy & Utilities' },
    { value: 'government', label: 'Government' },
    { value: 'nonprofit', label: 'Non-Profit' },
    { value: 'other', label: 'Other' },
  ];

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
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

  // EIN format validation
  const validateEIN = (ein: string): boolean => {
    // Basic validation for EIN format (XX-XXXXXXX)
    const einRegex = /^\d{2}-\d{7}$/;
    return ein === '' || einRegex.test(ein);
  };

  // Email validation
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return email === '' || emailRegex.test(email);
  };

  // Phone validation
  const validatePhone = (phone: string): boolean => {
    // Basic validation for phone numbers
    const phoneRegex = /^[\d\s()+\-]{10,15}$/;
    return phone === '' || phoneRegex.test(phone);
  };

  const handleSubmit = async () => {
    // Validate required fields
    if (!formData.company_name) {
      setLocalError('Company name is required.');
      return;
    }

    // Validate EIN format if provided
    if (formData.company_ein && !validateEIN(formData.company_ein)) {
      setLocalError('EIN must be in format XX-XXXXXXX (e.g., 12-3456789).');
      return;
    }

    // Validate email if provided
    if (formData.contact_email && !validateEmail(formData.contact_email)) {
      setLocalError('Please enter a valid email address.');
      return;
    }

    // Validate phone if provided
    if (formData.contact_phone && !validatePhone(formData.contact_phone)) {
      setLocalError('Please enter a valid phone number.');
      return;
    }

    try {
      if (employer) {
        // Update existing employer
        await dispatch(
          updateEmployer({
            employerId: employer.employer_id,
            employerData: formData as EmployerUpdate,
          })
        ).unwrap();
      } else {
        // Create new employer
        await dispatch(createEmployer(formData)).unwrap();
      }

      onSuccess?.();
      onClose();
    } catch (err: any) {
      setLocalError(err.message || 'Failed to save employer.');
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {employer ? 'Edit Employer' : 'Add New Employer'}
      </DialogTitle>

      <DialogContent>
        {(error || localError) && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error || localError}
          </Alert>
        )}

        <Grid container spacing={2} sx={{ mt: 1 }}>
          {/* Company Name */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              required
              label="Company Name"
              value={formData.company_name}
              onChange={(e) => handleInputChange('company_name', e.target.value)}
            />
          </Grid>

          {/* Company EIN */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Employer Identification Number (EIN)"
              value={formData.company_ein}
              onChange={(e) => handleInputChange('company_ein', e.target.value)}
              placeholder="XX-XXXXXXX"
              helperText="Format: XX-XXXXXXX (e.g., 12-3456789)"
            />
          </Grid>

          {/* Company Type */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Company Type</InputLabel>
              <Select
                value={formData.company_type}
                label="Company Type"
                onChange={(e) => handleInputChange('company_type', e.target.value)}
              >
                <MenuItem value="">
                  <em>Not Specified</em>
                </MenuItem>
                {companyTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Industry */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Industry</InputLabel>
              <Select
                value={formData.industry}
                label="Industry"
                onChange={(e) => handleInputChange('industry', e.target.value)}
              >
                <MenuItem value="">
                  <em>Not Specified</em>
                </MenuItem>
                {industries.map((industry) => (
                  <MenuItem key={industry.value} value={industry.value}>
                    {industry.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Address */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Company Address</InputLabel>
              <Select
                value={formData.address_id}
                label="Company Address"
                onChange={(e) => handleInputChange('address_id', e.target.value)}
              >
                <MenuItem value="">
                  <em>No Address Selected</em>
                </MenuItem>
                {addresses.map((address) => (
                  <MenuItem key={address.address_id} value={address.address_id}>
                    {formatAddressForDisplay(address)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              Contact Information
            </Typography>
          </Grid>

          {/* Contact Name */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Contact Name"
              value={formData.contact_name}
              onChange={(e) => handleInputChange('contact_name', e.target.value)}
            />
          </Grid>

          {/* Contact Email */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Contact Email"
              type="email"
              value={formData.contact_email}
              onChange={(e) => handleInputChange('contact_email', e.target.value)}
            />
          </Grid>

          {/* Contact Phone */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Contact Phone"
              value={formData.contact_phone}
              onChange={(e) => handleInputChange('contact_phone', e.target.value)}
            />
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
              label="Employer Verified"
            />
            {formData.is_verified && (
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="Verification Date"
                  value={formData.verification_date ? new Date(formData.verification_date) : null}
                  onChange={(date) => handleInputChange('verification_date', date ? format(date, 'yyyy-MM-dd') : '')}
                  slotProps={{ textField: { fullWidth: true, size: 'small', sx: { mt: 1 } } }}
                />
              </LocalizationProvider>
            )}
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
          {loading ? 'Saving...' : (employer ? 'Update' : 'Create')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EmployerForm;