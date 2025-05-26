import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Card,
  CardContent,
  Chip,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Tooltip,
  Stack,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Edit as EditIcon,
  Verified as VerifiedIcon,
  Warning as WarningIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
  Visibility as PreviewIcon,
} from '@mui/icons-material';

import { RootState, AppDispatch } from '../../store';
import { DocumentPreview } from './DocumentPreview';
import {
  fetchDocuments,
  deleteDocument,
  setFilters,
  clearError,
} from '../../store/slices/documentsSlice';
import { documentsApi, DocumentResponse } from '../../api/documents';

const DOCUMENT_TYPES = [
  'passport',
  'visa',
  'i797',
  'i94',
  'ead',
  'green_card',
  'drivers_license',
  'birth_certificate',
  'marriage_certificate',
  'diploma',
  'transcript',
  'employment_letter',
  'pay_stub',
  'tax_return',
  'bank_statement',
  'lease_agreement',
  'utility_bill',
  'medical_record',
  'vaccination_record',
  'other',
];

interface DocumentListProps {
  onEditDocument?: (document: DocumentResponse) => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({ onEditDocument }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { documents, loading, error, filters } = useSelector(
    (state: RootState) => state.documents
  );

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState<DocumentResponse | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [previewDocument, setPreviewDocument] = useState<DocumentResponse | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);

  useEffect(() => {
    dispatch(fetchDocuments(filters));
  }, [dispatch, filters]);

  const handleDeleteClick = (document: DocumentResponse) => {
    setDocumentToDelete(document);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (documentToDelete) {
      await dispatch(deleteDocument(documentToDelete.document_id));
      setDeleteDialogOpen(false);
      setDocumentToDelete(null);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setDocumentToDelete(null);
  };

  const handleDownload = async (document: DocumentResponse) => {
    try {
      const downloadUrl = await documentsApi.getDocumentDownloadUrl(document.document_id);
      // Append download=true parameter to force download
      const url = new URL(downloadUrl);
      url.searchParams.set('download', 'true');
      window.open(url.toString(), '_blank');
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const handlePreview = (document: DocumentResponse) => {
    setPreviewDocument(document);
    setPreviewOpen(true);
  };

  const handlePreviewClose = () => {
    setPreviewOpen(false);
    setPreviewDocument(null);
  };

  const handleFilterChange = (filterType: string, value: any) => {
    const newFilters = { ...filters, [filterType]: value };
    if (!value) {
      delete newFilters[filterType as keyof typeof newFilters];
    }
    dispatch(setFilters(newFilters));
  };

  const clearFilters = () => {
    dispatch(setFilters({}));
    setSearchTerm('');
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const isExpiringSoon = (expiryDate: string | undefined) => {
    if (!expiryDate) return false;
    const expiry = new Date(expiryDate);
    const thirtyDaysFromNow = new Date();
    thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30);
    return expiry < thirtyDaysFromNow && expiry > new Date();
  };

  const isExpired = (expiryDate: string | undefined) => {
    if (!expiryDate) return false;
    return new Date(expiryDate) < new Date();
  };

  const filteredDocuments = documents.filter((doc) => {
    if (!searchTerm) return true;
    const searchLower = searchTerm.toLowerCase();
    return (
      doc.document_type.toLowerCase().includes(searchLower) ||
      doc.document_number?.toLowerCase().includes(searchLower) ||
      doc.issuing_authority?.toLowerCase().includes(searchLower) ||
      doc.file_name.toLowerCase().includes(searchLower) ||
      doc.tags.some(tag => tag.toLowerCase().includes(searchLower))
    );
  });

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {error && (
        <Alert
          severity="error"
          sx={{ mb: 2 }}
          onClose={() => dispatch(clearError())}
        >
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Filters
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
                placeholder="Search documents..."
              />
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Document Type</InputLabel>
                <Select
                  value={filters.document_type || ''}
                  onChange={(e) => handleFilterChange('document_type', e.target.value)}
                  label="Document Type"
                >
                  <MenuItem value="">All Types</MenuItem>
                  {DOCUMENT_TYPES.map((type) => (
                    <MenuItem key={type} value={type}>
                      {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                label="Expires Before"
                type="date"
                value={filters.expiry_before || ''}
                onChange={(e) => handleFilterChange('expiry_before', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                label="Expires After"
                type="date"
                value={filters.expiry_after || ''}
                onChange={(e) => handleFilterChange('expiry_after', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                onClick={clearFilters}
                startIcon={<ClearIcon />}
              >
                Clear Filters
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Documents Grid */}
      {filteredDocuments.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="body1" color="text.secondary" textAlign="center">
              {documents.length === 0 
                ? 'No documents uploaded yet.' 
                : 'No documents match the current filters.'}
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={2}>
          {filteredDocuments.map((document) => (
            <Grid item xs={12} sm={6} md={4} key={document.document_id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                    <Typography variant="h6" component="div" noWrap>
                      {document.document_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Typography>
                    <Stack direction="row" spacing={1}>
                      {document.is_verified && (
                        <Tooltip title="Verified">
                          <VerifiedIcon color="primary" fontSize="small" />
                        </Tooltip>
                      )}
                      {isExpired(document.expiry_date) && (
                        <Tooltip title="Expired">
                          <WarningIcon color="error" fontSize="small" />
                        </Tooltip>
                      )}
                      {isExpiringSoon(document.expiry_date) && !isExpired(document.expiry_date) && (
                        <Tooltip title="Expiring Soon">
                          <WarningIcon color="warning" fontSize="small" />
                        </Tooltip>
                      )}
                    </Stack>
                  </Box>

                  {document.document_subtype && (
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {document.document_subtype}
                    </Typography>
                  )}

                  {document.document_number && (
                    <Typography variant="body2" gutterBottom>
                      <strong>Number:</strong> {document.document_number}
                    </Typography>
                  )}

                  {document.issuing_authority && (
                    <Typography variant="body2" gutterBottom>
                      <strong>Issued by:</strong> {document.issuing_authority}
                    </Typography>
                  )}

                  {document.expiry_date && (
                    <Typography variant="body2" gutterBottom>
                      <strong>Expires:</strong> {formatDate(document.expiry_date)}
                    </Typography>
                  )}

                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>File:</strong> {document.file_name}
                  </Typography>

                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Size:</strong> {(document.file_size / 1024 / 1024).toFixed(2)} MB
                  </Typography>

                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Uploaded:</strong> {formatDate(document.upload_date)}
                  </Typography>

                  {document.tags.length > 0 && (
                    <Box mt={2}>
                      <Stack direction="row" spacing={0.5} flexWrap="wrap">
                        {document.tags.map((tag) => (
                          <Chip key={tag} label={tag} size="small" />
                        ))}
                      </Stack>
                    </Box>
                  )}
                </CardContent>

                <Box sx={{ p: 1, pt: 0 }}>
                  <Stack direction="row" spacing={1} justifyContent="flex-end">
                    <Tooltip title="Preview">
                      <IconButton
                        size="small"
                        onClick={() => handlePreview(document)}
                        color="primary"
                      >
                        <PreviewIcon />
                      </IconButton>
                    </Tooltip>
                    
                    <Tooltip title="Download">
                      <IconButton
                        size="small"
                        onClick={() => handleDownload(document)}
                        color="primary"
                      >
                        <DownloadIcon />
                      </IconButton>
                    </Tooltip>
                    
                    {onEditDocument && (
                      <Tooltip title="Edit">
                        <IconButton
                          size="small"
                          onClick={() => onEditDocument(document)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteClick(document)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Stack>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleDeleteCancel}>
        <DialogTitle>Delete Document</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete "{documentToDelete?.file_name}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Document Preview Dialog */}
      <DocumentPreview
        document={previewDocument}
        open={previewOpen}
        onClose={handlePreviewClose}
      />
    </Box>
  );
};