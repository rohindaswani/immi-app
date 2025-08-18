import React, { useState, useCallback, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  Alert,
  LinearProgress,
  IconButton,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Delete as DeleteIcon,
  InsertDriveFile as FileIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

import { RootState, AppDispatch } from '../../store';
import { uploadDocument } from '../../store/slices/documentsSlice';
import { DocumentUpload as DocumentUploadType } from '../../api/documents';

const DropzoneContainer = styled(Box)(({ theme }) => ({
  border: `2px dashed ${theme.palette.grey[300]}`,
  borderRadius: theme.shape.borderRadius,
  padding: theme.spacing(4),
  textAlign: 'center',
  cursor: 'pointer',
  transition: 'border-color 0.3s ease',
  '&:hover': {
    borderColor: theme.palette.primary.main,
  },
  '&.drag-active': {
    borderColor: theme.palette.primary.main,
    backgroundColor: theme.palette.action.hover,
  },
}));

const ACCEPTED_FILE_TYPES = '.pdf,.jpg,.jpeg,.png,.tiff,.tif,.webp';
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

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

const IMMIGRATION_TYPES = [
  'H1-B',
  'L-1',
  'O-1',
  'E-2',
  'F-1',
  'J-1',
  'B-1/B-2',
  'TN',
  'Green Card',
  'Citizenship',
  'Other',
];

interface DocumentUploadProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  open,
  onClose,
  onSuccess,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const { uploading, error } = useSelector((state: RootState) => state.documents);

  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [documentType, setDocumentType] = useState('');
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): boolean => {
    const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      alert(`Invalid file type: ${file.type}. Please select PDF, JPG, PNG, TIFF, or WebP files.`);
      return false;
    }
    if (file.size > MAX_FILE_SIZE) {
      alert(`File size too large: ${(file.size / 1024 / 1024).toFixed(2)}MB. Maximum size is 10MB.`);
      return false;
    }
    return true;
  };

  const handleFileSelect = (files: FileList) => {
    const validFiles: File[] = [];
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (validateFile(file)) {
        validFiles.push(file);
      }
    }
    if (validFiles.length > 0) {
      setSelectedFiles(prev => [...prev, ...validFiles]);
    }
  };

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
    const files = e.dataTransfer.files;
    handleFileSelect(files);
  }, []);

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      handleFileSelect(files);
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (selectedFiles.length === 0 || !documentType) {
      return;
    }

    const uploadPromises = selectedFiles.map(file => {
      const documentData: DocumentUploadType = {
        file,
        document_type: documentType,
        // All other fields will be extracted automatically
      };

      return dispatch(uploadDocument(documentData));
    });

    try {
      await Promise.all(uploadPromises);
      handleClose();
      onSuccess?.();
    } catch (error) {
      // Error handling is done in the Redux slice
    }
  };

  const handleClose = () => {
    setSelectedFiles([]);
    setDocumentType('');
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Upload Documents</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {uploading && <LinearProgress sx={{ mb: 2 }} />}

        {/* File Drop Zone */}
        <DropzoneContainer
          className={isDragActive ? 'drag-active' : ''}
          sx={{ mb: 3 }}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={openFileDialog}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept={ACCEPTED_FILE_TYPES}
            onChange={handleFileInputChange}
            style={{ display: 'none' }}
          />
          <CloudUploadIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {isDragActive
              ? 'Drop files here...'
              : 'Drag & drop files here, or click to select'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Supported formats: PDF, JPG, PNG, TIFF, WebP (max 10MB each)
          </Typography>
        </DropzoneContainer>

        {/* Selected Files */}
        {selectedFiles.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              Selected Files:
            </Typography>
            {selectedFiles.map((file, index) => (
              <Card key={index} sx={{ mb: 1 }}>
                <CardContent sx={{ display: 'flex', alignItems: 'center', py: 1 }}>
                  <FileIcon sx={{ mr: 1 }} />
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="body2">{file.name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </Typography>
                  </Box>
                  <IconButton
                    size="small"
                    onClick={() => removeFile(index)}
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                </CardContent>
              </Card>
            ))}
          </Box>
        )}

        {/* Document Type Selection */}
        <Box sx={{ mb: 3 }}>
          <FormControl fullWidth required>
            <InputLabel>Document Type</InputLabel>
            <Select
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value)}
              label="Document Type"
            >
              {DOCUMENT_TYPES.map((type) => (
                <MenuItem key={type} value={type}>
                  {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <Alert severity="info" sx={{ mt: 2 }}>
            📄 All document details (number, dates, issuing authority, etc.) will be automatically extracted from your uploaded document using AI-powered OCR.
          </Alert>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={uploading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={uploading || selectedFiles.length === 0 || !documentType}
        >
          Upload {selectedFiles.length > 0 && `${selectedFiles.length} file${selectedFiles.length > 1 ? 's' : ''}`}
        </Button>
      </DialogActions>
    </Dialog>
  );
};