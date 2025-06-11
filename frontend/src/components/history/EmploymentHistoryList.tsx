import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  Chip,
  Tooltip,
  Alert,
  CircularProgress,
  TablePagination,
  Badge,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  FileDownload as ExportIcon,
  Business as BusinessIcon,
  CheckCircle as ValidIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../store';
import { 
  fetchEmploymentHistory, 
  deleteEmploymentHistory, 
  exportEmploymentHistory,
  validateH1BEmployment
} from '../../store/slices/historySlice';
import { EmploymentHistory } from '../../api/history';
import { format, parseISO } from 'date-fns';
import EmploymentHistoryForm from './EmploymentHistoryForm';

interface EmploymentHistoryListProps {
  onAddClick?: () => void;
}

const EmploymentHistoryList: React.FC<EmploymentHistoryListProps> = ({
  onAddClick,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const { employmentHistory, loading, error, h1bValidation } = useSelector((state: RootState) => state.history);
  
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selectedEmploymentHistory, setSelectedEmploymentHistory] = useState<EmploymentHistory | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);

  // Load employment history and H1B validation on component mount
  useEffect(() => {
    dispatch(fetchEmploymentHistory());
    dispatch(validateH1BEmployment());
  }, [dispatch]);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleEdit = (employmentHistory: EmploymentHistory) => {
    setSelectedEmploymentHistory(employmentHistory);
    setIsEditDialogOpen(true);
  };

  const handleDelete = async (employmentHistoryId: string) => {
    if (window.confirm('Are you sure you want to delete this employment history record?')) {
      try {
        await dispatch(deleteEmploymentHistory(employmentHistoryId)).unwrap();
        // Refresh H1B validation after deletion
        dispatch(validateH1BEmployment());
      } catch (err) {
        console.error('Failed to delete employment history:', err);
      }
    }
  };

  const handleAddNew = () => {
    setSelectedEmploymentHistory(null);
    setIsEditDialogOpen(true);
    onAddClick?.();
  };

  const handleRefresh = () => {
    dispatch(fetchEmploymentHistory());
    dispatch(validateH1BEmployment());
  };

  const handleExport = async (format: 'pdf' | 'csv') => {
    try {
      setExportLoading(true);
      const blob = await dispatch(exportEmploymentHistory(format)).unwrap();
      
      // Create a download link and trigger the download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `employment-history.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error(`Failed to export employment history as ${format}:`, err);
    } finally {
      setExportLoading(false);
    }
  };

  const handleValidateH1B = async (historyId?: string) => {
    try {
      await dispatch(validateH1BEmployment(historyId)).unwrap();
    } catch (err) {
      console.error('Failed to validate H1-B compliance:', err);
    }
  };

  const formatDateRange = (startDate: string, endDate?: string, isCurrent?: boolean) => {
    const formattedStart = format(parseISO(startDate), 'MMM yyyy');
    
    if (isCurrent) {
      return `${formattedStart} - Present`;
    }
    
    if (endDate) {
      const formattedEnd = format(parseISO(endDate), 'MMM yyyy');
      return `${formattedStart} - ${formattedEnd}`;
    }
    
    return formattedStart;
  };

  const getH1BComplianceStatus = () => {
    if (!h1bValidation) return null;
    
    if (h1bValidation.is_valid) {
      return (
        <Chip 
          icon={<ValidIcon />} 
          label="H1-B Compliant" 
          color="success" 
          size="small"
          sx={{ mb: 2 }}
        />
      );
    } else {
      return (
        <Tooltip title={h1bValidation.issues.join(', ')}>
          <Chip 
            icon={<ErrorIcon />} 
            label="H1-B Compliance Issues" 
            color="error" 
            size="small"
            sx={{ mb: 2 }}
          />
        </Tooltip>
      );
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h6" component="h2">
            Employment History
          </Typography>
          {getH1BComplianceStatus()}
        </Box>
        <Box>
          <Button
            variant="outlined"
            startIcon={<ExportIcon />}
            onClick={() => handleExport('pdf')}
            disabled={exportLoading || employmentHistory.length === 0}
            sx={{ mr: 1 }}
          >
            Export PDF
          </Button>
          <Button
            variant="outlined"
            startIcon={<ExportIcon />}
            onClick={() => handleExport('csv')}
            disabled={exportLoading || employmentHistory.length === 0}
            sx={{ mr: 1 }}
          >
            Export CSV
          </Button>
          <IconButton onClick={handleRefresh} disabled={loading}>
            <RefreshIcon />
          </IconButton>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleAddNew}
          >
            Add Employment
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {h1bValidation && h1bValidation.warnings.length > 0 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="subtitle2">H1-B Compliance Warnings:</Typography>
          <ul>
            {h1bValidation.warnings.map((warning, index) => (
              <li key={index}>{warning}</li>
            ))}
          </ul>
        </Alert>
      )}

      {loading ? (
        <Box display="flex" justifyContent="center" p={3}>
          <CircularProgress />
        </Box>
      ) : employmentHistory.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" color="textSecondary">
            No employment history records found. Click "Add Employment" to create your first record.
          </Typography>
        </Paper>
      ) : (
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Employer</TableCell>
                  <TableCell>Job Title</TableCell>
                  <TableCell>Period</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {employmentHistory
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((history) => (
                    <TableRow key={history.employment_id}>
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <BusinessIcon fontSize="small" sx={{ mr: 1 }} />
                          <Typography variant="body2">
                            {history.employer?.company_name || 'Unknown Employer'}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{history.job_title}</TableCell>
                      <TableCell>
                        {formatDateRange(history.start_date, history.end_date, history.is_current)}
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={history.employment_type || 'Unspecified'} 
                          size="small"
                          color={history.employment_type === 'full-time' ? 'primary' : 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        {history.is_current ? (
                          <Chip label="Current" color="success" size="small" />
                        ) : (
                          <Chip label="Previous" size="small" />
                        )}
                      </TableCell>
                      <TableCell>
                        <Tooltip title="Validate H1-B compliance">
                          <IconButton 
                            size="small" 
                            onClick={() => handleValidateH1B(history.employment_id)}
                            color={
                              (history.is_current && h1bValidation && h1bValidation.is_valid) 
                                ? 'success' 
                                : 'default'
                            }
                          >
                            {history.is_current && h1bValidation && !h1bValidation.is_valid ? (
                              <WarningIcon fontSize="small" color="error" />
                            ) : (
                              <CheckCircle fontSize="small" />
                            )}
                          </IconButton>
                        </Tooltip>
                        <IconButton size="small" onClick={() => handleEdit(history)}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                        <IconButton 
                          size="small" 
                          onClick={() => handleDelete(history.employment_id)}
                          disabled={history.is_current} // Prevent deleting current employment
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={employmentHistory.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>
      )}

      {/* Edit/Add Dialog */}
      <EmploymentHistoryForm
        open={isEditDialogOpen}
        onClose={() => setIsEditDialogOpen(false)}
        employmentHistory={selectedEmploymentHistory || undefined}
        onSuccess={() => {
          setIsEditDialogOpen(false);
          handleRefresh();
        }}
      />
    </Box>
  );
};

export default EmploymentHistoryList;