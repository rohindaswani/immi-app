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
  Divider,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../store';
import { 
  createEmploymentHistory, 
  updateEmploymentHistory, 
  fetchEmployers, 
  fetchAddresses 
} from '../../store/slices/historySlice';
import { 
  EmploymentHistory, 
  EmploymentHistoryCreate, 
  EmploymentHistoryUpdate,
  Employer,
  Address 
} from '../../api/history';
import { format } from 'date-fns';

interface EmploymentHistoryFormProps {
  open: boolean;
  onClose: () => void;
  employmentHistory?: EmploymentHistory;
  onSuccess?: () => void;
}

const EmploymentHistoryForm: React.FC<EmploymentHistoryFormProps> = ({
  open,
  onClose,
  employmentHistory,
  onSuccess,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const { loading, error, employers, addresses } = useSelector((state: RootState) => state.history);
  const [localError, setLocalError] = useState<string | null>(null);

  const [formData, setFormData] = useState<EmploymentHistoryCreate>({
    employer_id: '',
    job_title: '',
    job_description: '',
    department: '',
    employment_type: 'full-time',
    start_date: new Date().toISOString().split('T')[0],
    end_date: '',
    is_current: true,
    salary: undefined,
    salary_frequency: 'annual',
    working_hours_per_week: 40,
    work_location_id: '',
    supervisor_name: '',
    supervisor_title: '',
    supervisor_phone: '',
    supervisor_email: '',
    termination_reason: '',
    is_verified: false,
    verification_document_id: '',
  });

  // Load employers and addresses if not already loaded
  useEffect(() => {
    if (employers.length === 0) {
      dispatch(fetchEmployers());
    }
    if (addresses.length === 0) {
      dispatch(fetchAddresses());
    }
  }, [dispatch, employers.length, addresses.length]);

  // Initialize form data when editing
  useEffect(() => {
    if (employmentHistory) {
      setFormData({
        employer_id: employmentHistory.employer_id,
        job_title: employmentHistory.job_title,
        job_description: employmentHistory.job_description || '',
        department: employmentHistory.department || '',
        employment_type: employmentHistory.employment_type || 'full-time',
        start_date: employmentHistory.start_date.split('T')[0],
        end_date: employmentHistory.end_date ? employmentHistory.end_date.split('T')[0] : '',
        is_current: employmentHistory.is_current,
        salary: employmentHistory.salary,
        salary_frequency: employmentHistory.salary_frequency || 'annual',
        working_hours_per_week: employmentHistory.working_hours_per_week || 40,
        work_location_id: employmentHistory.work_location_id || '',
        supervisor_name: employmentHistory.supervisor_name || '',
        supervisor_title: employmentHistory.supervisor_title || '',
        supervisor_phone: employmentHistory.supervisor_phone || '',
        supervisor_email: employmentHistory.supervisor_email || '',
        termination_reason: employmentHistory.termination_reason || '',
        is_verified: employmentHistory.is_verified || false,
        verification_document_id: employmentHistory.verification_document_id || '',
      });
    } else {
      // Reset form for new entry
      setFormData({
        employer_id: '',
        job_title: '',
        job_description: '',
        department: '',
        employment_type: 'full-time',
        start_date: new Date().toISOString().split('T')[0],
        end_date: '',
        is_current: true,
        salary: undefined,
        salary_frequency: 'annual',
        working_hours_per_week: 40,
        work_location_id: '',
        supervisor_name: '',
        supervisor_title: '',
        supervisor_phone: '',
        supervisor_email: '',
        termination_reason: '',
        is_verified: false,
        verification_document_id: '',
      });
    }
    setLocalError(null);
  }, [employmentHistory, open]);

  const employmentTypes = [
    { value: 'full-time', label: 'Full-time' },
    { value: 'part-time', label: 'Part-time' },
    { value: 'contract', label: 'Contract' },
    { value: 'temporary', label: 'Temporary' },
    { value: 'internship', label: 'Internship' },
    { value: 'seasonal', label: 'Seasonal' },
    { value: 'self-employed', label: 'Self-employed' },
    { value: 'other', label: 'Other' },
  ];

  const salaryFrequencies = [
    { value: 'hourly', label: 'Hourly' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'biweekly', label: 'Bi-weekly' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'annual', label: 'Annual' },
  ];

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    // If setting as current, clear end date and termination reason
    if (field === 'is_current' && value === true) {
      setFormData((prev) => ({ ...prev, end_date: '', termination_reason: '' }));
    }
  };

  const formatEmployerForDisplay = (employer: Employer): string => {
    return employer.company_name;
  };

  const formatAddressForDisplay = (address: Address): string => {
    let displayText = address.street_address_1;
    
    if (address.city_name) {
      displayText += `, ${address.city_name}`;
    }
    
    if (address.state_name) {
      displayText += `, ${address.state_name}`;
    }
    
    if (address.country_name) {
      displayText += `, ${address.country_name}`;
    }
    
    return displayText;
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
    if (!formData.employer_id || !formData.job_title || !formData.start_date) {
      setLocalError('Employer, job title, and start date are required.');
      return;
    }

    // Make sure end date is after start date
    if (formData.end_date && formData.start_date > formData.end_date) {
      setLocalError('End date must be after start date.');
      return;
    }

    // Validate email if provided
    if (formData.supervisor_email && !validateEmail(formData.supervisor_email)) {
      setLocalError('Please enter a valid supervisor email address.');
      return;
    }

    // Validate phone if provided
    if (formData.supervisor_phone && !validatePhone(formData.supervisor_phone)) {
      setLocalError('Please enter a valid supervisor phone number.');
      return;
    }

    // Validate hours for H1-B
    if (formData.employment_type === 'full-time' && formData.working_hours_per_week && formData.working_hours_per_week < 35) {
      setLocalError('For H-1B compliance, full-time employment should be at least 35 hours per week.');
      return;
    }

    try {
      if (employmentHistory) {
        // Update existing record
        await dispatch(
          updateEmploymentHistory({
            historyId: employmentHistory.employment_id,
            historyData: formData as EmploymentHistoryUpdate,
          })
        ).unwrap();
      } else {
        // Create new record
        await dispatch(createEmploymentHistory(formData)).unwrap();
      }

      onSuccess?.();
      onClose();
    } catch (err: any) {
      setLocalError(err.message || 'Failed to save employment history.');
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {employmentHistory ? 'Edit Employment History' : 'Add Employment History'}
      </DialogTitle>

      <DialogContent>
        {(error || localError) && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error || localError}
          </Alert>
        )}

        <Grid container spacing={2} sx={{ mt: 1 }}>
          {/* Basic Job Information */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" fontWeight="bold">
              Basic Job Information
            </Typography>
          </Grid>

          {/* Employer */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth required>
              <InputLabel>Employer</InputLabel>
              <Select
                value={formData.employer_id}
                label="Employer"
                onChange={(e) => handleInputChange('employer_id', e.target.value)}
              >
                {employers.map((employer) => (
                  <MenuItem key={employer.employer_id} value={employer.employer_id}>
                    {formatEmployerForDisplay(employer)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Job Title */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="Job Title"
              value={formData.job_title}
              onChange={(e) => handleInputChange('job_title', e.target.value)}
            />
          </Grid>

          {/* Department */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Department"
              value={formData.department}
              onChange={(e) => handleInputChange('department', e.target.value)}
            />
          </Grid>

          {/* Employment Type */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth required>
              <InputLabel>Employment Type</InputLabel>
              <Select
                value={formData.employment_type}
                label="Employment Type"
                onChange={(e) => handleInputChange('employment_type', e.target.value)}
              >
                {employmentTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Job Description */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Job Description"
              value={formData.job_description}
              onChange={(e) => handleInputChange('job_description', e.target.value)}
            />
          </Grid>

          {/* Employment Dates */}
          <Grid item xs={12}>
            <Divider sx={{ my: 1 }} />
            <Typography variant="subtitle1" fontWeight="bold">
              Employment Dates
            </Typography>
          </Grid>

          {/* Is Current */}
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.is_current}
                  onChange={(e) => handleInputChange('is_current', e.target.checked)}
                />
              }
              label="Current Employment"
            />
            <Typography variant="caption" display="block">
              Note: If set as current, any other current employment will be updated.
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
                    helperText: formData.is_current ? 'Not applicable for current employment' : undefined
                  } 
                }}
              />
            </LocalizationProvider>
          </Grid>

          {/* Termination Reason - Only shown if not current and end date exists */}
          {!formData.is_current && formData.end_date && (
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Reason for Leaving"
                value={formData.termination_reason}
                onChange={(e) => handleInputChange('termination_reason', e.target.value)}
              />
            </Grid>
          )}

          {/* Salary Information */}
          <Grid item xs={12}>
            <Divider sx={{ my: 1 }} />
            <Typography variant="subtitle1" fontWeight="bold">
              Compensation & Hours
            </Typography>
          </Grid>

          {/* Salary */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Salary"
              type="number"
              value={formData.salary || ''}
              onChange={(e) => handleInputChange('salary', e.target.value ? parseFloat(e.target.value) : undefined)}
            />
          </Grid>

          {/* Salary Frequency */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Salary Frequency</InputLabel>
              <Select
                value={formData.salary_frequency}
                label="Salary Frequency"
                onChange={(e) => handleInputChange('salary_frequency', e.target.value)}
              >
                {salaryFrequencies.map((frequency) => (
                  <MenuItem key={frequency.value} value={frequency.value}>
                    {frequency.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Working Hours Per Week */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Working Hours Per Week"
              type="number"
              value={formData.working_hours_per_week || ''}
              onChange={(e) => handleInputChange('working_hours_per_week', e.target.value ? parseFloat(e.target.value) : undefined)}
              helperText={formData.employment_type === 'full-time' ? 'H-1B compliance requires at least 35 hours/week for full-time' : undefined}
            />
          </Grid>

          {/* Work Location */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Work Location</InputLabel>
              <Select
                value={formData.work_location_id}
                label="Work Location"
                onChange={(e) => handleInputChange('work_location_id', e.target.value)}
              >
                <MenuItem value="">
                  <em>Not Specified</em>
                </MenuItem>
                {addresses.map((address) => (
                  <MenuItem key={address.address_id} value={address.address_id}>
                    {formatAddressForDisplay(address)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Supervisor Information */}
          <Grid item xs={12}>
            <Divider sx={{ my: 1 }} />
            <Typography variant="subtitle1" fontWeight="bold">
              Supervisor Information
            </Typography>
          </Grid>

          {/* Supervisor Name */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Supervisor Name"
              value={formData.supervisor_name}
              onChange={(e) => handleInputChange('supervisor_name', e.target.value)}
            />
          </Grid>

          {/* Supervisor Title */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Supervisor Title"
              value={formData.supervisor_title}
              onChange={(e) => handleInputChange('supervisor_title', e.target.value)}
            />
          </Grid>

          {/* Supervisor Email */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Supervisor Email"
              type="email"
              value={formData.supervisor_email}
              onChange={(e) => handleInputChange('supervisor_email', e.target.value)}
            />
          </Grid>

          {/* Supervisor Phone */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Supervisor Phone"
              value={formData.supervisor_phone}
              onChange={(e) => handleInputChange('supervisor_phone', e.target.value)}
            />
          </Grid>

          {/* Verification */}
          <Grid item xs={12}>
            <Divider sx={{ my: 1 }} />
            <Typography variant="subtitle1" fontWeight="bold">
              Verification
            </Typography>
          </Grid>

          {/* Verification Checkbox */}
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.is_verified}
                  onChange={(e) => handleInputChange('is_verified', e.target.checked)}
                />
              }
              label="Employment Verified"
            />
          </Grid>

          {/* Verification Document ID */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Verification Document ID (Optional)"
              value={formData.verification_document_id || ''}
              onChange={(e) => handleInputChange('verification_document_id', e.target.value)}
              helperText="Enter a document ID if this employment has supporting documentation"
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
          {loading ? 'Saving...' : (employmentHistory ? 'Update' : 'Add')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EmploymentHistoryForm;