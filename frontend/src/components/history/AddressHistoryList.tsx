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
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  FileDownload as ExportIcon,
  Home as HomeIcon,
  Business as BusinessIcon,
  Mail as MailIcon,
  Help as HelpIcon,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../store';
import { 
  fetchAddressHistory, 
  deleteAddressHistory, 
  exportAddressHistory 
} from '../../store/slices/historySlice';
import { AddressHistory } from '../../api/history';
import { format, parseISO } from 'date-fns';
import AddressHistoryForm from './AddressHistoryForm';

interface AddressHistoryListProps {
  onAddClick?: () => void;
}

const AddressHistoryList: React.FC<AddressHistoryListProps> = ({
  onAddClick,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const { addressHistory, loading, error } = useSelector((state: RootState) => state.history);
  
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selectedAddressHistory, setSelectedAddressHistory] = useState<AddressHistory | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);

  // Load address history on component mount
  useEffect(() => {
    dispatch(fetchAddressHistory());
  }, [dispatch]);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleEdit = (addressHistory: AddressHistory) => {
    setSelectedAddressHistory(addressHistory);
    setIsEditDialogOpen(true);
  };

  const handleDelete = async (addressHistoryId: string) => {
    if (window.confirm('Are you sure you want to delete this address history record?')) {
      try {
        await dispatch(deleteAddressHistory(addressHistoryId)).unwrap();
      } catch (err) {
        console.error('Failed to delete address history:', err);
      }
    }
  };

  const handleAddNew = () => {
    setSelectedAddressHistory(null);
    setIsEditDialogOpen(true);
    onAddClick?.();
  };

  const handleRefresh = () => {
    dispatch(fetchAddressHistory());
  };

  const handleExport = async (format: 'pdf' | 'csv') => {
    try {
      setExportLoading(true);
      const blob = await dispatch(exportAddressHistory(format)).unwrap();
      
      // Create a download link and trigger the download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `address-history.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error(`Failed to export address history as ${format}:`, err);
    } finally {
      setExportLoading(false);
    }
  };

  const getAddressTypeIcon = (type?: string) => {
    switch (type) {
      case 'residential':
        return <HomeIcon fontSize="small" />;
      case 'work':
        return <BusinessIcon fontSize="small" />;
      case 'mailing':
        return <MailIcon fontSize="small" />;
      default:
        return <HelpIcon fontSize="small" />;
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

  const formatAddress = (addressHistory: AddressHistory) => {
    if (!addressHistory.address) return 'Unknown Address';
    
    const address = addressHistory.address;
    let formattedAddress = address.street_address_1;
    
    if (address.street_address_2) {
      formattedAddress += `, ${address.street_address_2}`;
    }
    
    if (address.city_name) {
      formattedAddress += `, ${address.city_name}`;
    }
    
    if (address.state_name) {
      formattedAddress += `, ${address.state_name}`;
    }
    
    if (address.zip_code) {
      formattedAddress += ` ${address.zip_code}`;
    }
    
    if (address.country_name) {
      formattedAddress += `, ${address.country_name}`;
    }
    
    return formattedAddress;
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" component="h2">
          Address History
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<ExportIcon />}
            onClick={() => handleExport('pdf')}
            disabled={exportLoading || addressHistory.length === 0}
            sx={{ mr: 1 }}
          >
            Export PDF
          </Button>
          <Button
            variant="outlined"
            startIcon={<ExportIcon />}
            onClick={() => handleExport('csv')}
            disabled={exportLoading || addressHistory.length === 0}
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
            Add New Address
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box display="flex" justifyContent="center" p={3}>
          <CircularProgress />
        </Box>
      ) : addressHistory.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" color="textSecondary">
            No address history records found. Click "Add New Address" to create your first record.
          </Typography>
        </Paper>
      ) : (
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Type</TableCell>
                  <TableCell>Address</TableCell>
                  <TableCell>Period</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {addressHistory
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((history) => (
                    <TableRow key={history.address_history_id}>
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <Tooltip title={history.address_type || 'Unspecified'}>
                            {getAddressTypeIcon(history.address_type)}
                          </Tooltip>
                          <Typography variant="body2" sx={{ ml: 1 }}>
                            {history.address_type || 'Unspecified'}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{formatAddress(history)}</TableCell>
                      <TableCell>
                        {formatDateRange(history.start_date, history.end_date, history.is_current)}
                      </TableCell>
                      <TableCell>
                        {history.is_current ? (
                          <Chip label="Current" color="primary" size="small" />
                        ) : (
                          <Chip label="Previous" size="small" />
                        )}
                      </TableCell>
                      <TableCell>
                        <IconButton size="small" onClick={() => handleEdit(history)}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                        <IconButton 
                          size="small" 
                          onClick={() => handleDelete(history.address_history_id)}
                          disabled={history.is_current} // Prevent deleting current address
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
            count={addressHistory.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>
      )}

      {/* Edit/Add Dialog */}
      <AddressHistoryForm
        open={isEditDialogOpen}
        onClose={() => setIsEditDialogOpen(false)}
        addressHistory={selectedAddressHistory || undefined}
        onSuccess={() => {
          setIsEditDialogOpen(false);
          handleRefresh();
        }}
      />
    </Box>
  );
};

export default AddressHistoryList;