import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Alert,
  CircularProgress,
  FormControlLabel,
  Checkbox,
  Paper,
  Box,
} from '@mui/material';
import {
  PictureAsPdf as PdfIcon,
  SimCardDownload as DownloadIcon,
} from '@mui/icons-material';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../../store';
import { exportAddressHistory, exportEmploymentHistory } from '../../store/slices/historySlice';

interface ExportFormsDialogProps {
  open: boolean;
  onClose: () => void;
}

const ExportFormsDialog: React.FC<ExportFormsDialogProps> = ({
  open,
  onClose,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const [formType, setFormType] = useState('i485');
  const [includeAddress, setIncludeAddress] = useState(true);
  const [includeEmployment, setIncludeEmployment] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // List of common immigration forms
  const immigrationForms = [
    { value: 'i485', label: 'Form I-485 (Adjustment of Status)' },
    { value: 'i765', label: 'Form I-765 (Employment Authorization)' },
    { value: 'i131', label: 'Form I-131 (Travel Document)' },
    { value: 'i129', label: 'Form I-129 (H-1B Petition)' },
    { value: 'i140', label: 'Form I-140 (Employment-Based Immigration)' },
    { value: 'i864', label: 'Form I-864 (Affidavit of Support)' },
    { value: 'i944', label: 'Form I-944 (Declaration of Self-Sufficiency)' },
    { value: 'n400', label: 'Form N-400 (Naturalization)' },
    { value: 'custom', label: 'Custom Export' },
  ];

  const handleExport = async () => {
    try {
      setLoading(true);
      setError(null);

      // Create a download link for our generated PDF
      const a = document.createElement('a');
      document.body.appendChild(a);
      a.style.display = 'none';

      // Export data based on selection
      if (includeAddress) {
        const addressBlob = await dispatch(exportAddressHistory('pdf')).unwrap();
        const addressUrl = window.URL.createObjectURL(addressBlob);
        a.href = addressUrl;
        a.download = `address-history-for-${formType}.pdf`;
        a.click();
        window.URL.revokeObjectURL(addressUrl);
      }

      if (includeEmployment) {
        const employmentBlob = await dispatch(exportEmploymentHistory('pdf')).unwrap();
        const employmentUrl = window.URL.createObjectURL(employmentBlob);
        a.href = employmentUrl;
        a.download = `employment-history-for-${formType}.pdf`;
        a.click();
        window.URL.revokeObjectURL(employmentUrl);
      }

      // Remove the temporary link
      document.body.removeChild(a);
      
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to export forms');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Export for Government Forms</DialogTitle>

      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="body1" gutterBottom>
              Export your address and employment history in a format suitable for USCIS forms.
              The exported PDF can be used as a reference when filling out government forms.
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Select Form</InputLabel>
              <Select
                value={formType}
                label="Select Form"
                onChange={(e) => setFormType(e.target.value)}
              >
                {immigrationForms.map((form) => (
                  <MenuItem key={form.value} value={form.value}>
                    {form.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              Data to Include
            </Typography>
            <FormControlLabel
              control={
                <Checkbox
                  checked={includeAddress}
                  onChange={(e) => setIncludeAddress(e.target.checked)}
                />
              }
              label="Address History"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={includeEmployment}
                  onChange={(e) => setIncludeEmployment(e.target.checked)}
                />
              }
              label="Employment History"
            />
          </Grid>

          <Grid item xs={12}>
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                Form Requirements
              </Typography>
              <Paper variant="outlined" sx={{ p: 2 }}>
                {formType === 'i485' && (
                  <>
                    <Typography variant="subtitle2">Form I-485 Requires:</Typography>
                    <ul>
                      <li>Address history for the past 5 years</li>
                      <li>Employment history for the past 5 years</li>
                    </ul>
                  </>
                )}
                {formType === 'i765' && (
                  <>
                    <Typography variant="subtitle2">Form I-765 Requires:</Typography>
                    <ul>
                      <li>Current address information</li>
                      <li>Previous USCIS employment authorization information</li>
                    </ul>
                  </>
                )}
                {formType === 'i129' && (
                  <>
                    <Typography variant="subtitle2">Form I-129 Requires:</Typography>
                    <ul>
                      <li>Current employer information</li>
                      <li>Work location information</li>
                      <li>Previous H-1B employment history</li>
                    </ul>
                  </>
                )}
                {formType === 'n400' && (
                  <>
                    <Typography variant="subtitle2">Form N-400 Requires:</Typography>
                    <ul>
                      <li>Address history for the past 5 years</li>
                      <li>Employment history for the past 5 years</li>
                      <li>All absences from the U.S. in the past 5 years</li>
                    </ul>
                  </>
                )}
                {(formType !== 'i485' && formType !== 'i765' && formType !== 'i129' && formType !== 'n400') && (
                  <Typography variant="body2">
                    Exporting history for reference when filling out this form.
                  </Typography>
                )}
              </Paper>
            </Box>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={handleExport}
          disabled={loading || (!includeAddress && !includeEmployment)}
          startIcon={loading ? <CircularProgress size={20} /> : <PdfIcon />}
        >
          {loading ? 'Exporting...' : 'Export for Form'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ExportFormsDialog;