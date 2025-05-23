import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  CircularProgress,
  Alert,
  IconButton,
} from '@mui/material';
import {
  Close as CloseIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';

import { documentsApi, DocumentResponse } from '../../api/documents';

interface DocumentPreviewProps {
  document: DocumentResponse | null;
  open: boolean;
  onClose: () => void;
}

export const DocumentPreview: React.FC<DocumentPreviewProps> = ({
  document,
  open,
  onClose,
}) => {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (document && open) {
      loadPreview();
    } else {
      setPreviewUrl(null);
      setError(null);
    }
  }, [document, open]);

  const loadPreview = async () => {
    if (!document) return;

    setLoading(true);
    setError(null);

    try {
      const downloadUrl = await documentsApi.getDocumentDownloadUrl(document.document_id);
      setPreviewUrl(downloadUrl);
    } catch (err) {
      setError('Failed to load document for preview');
      console.error('Preview load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (previewUrl) {
      window.open(previewUrl, '_blank');
    }
  };

  const isPdf = document?.file_type === 'application/pdf';
  const isImage = document?.file_type.startsWith('image/');

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: { height: '90vh' },
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h6" component="div">
              {document?.file_name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {document?.document_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              {document?.document_number && ` • ${document.document_number}`}
            </Typography>
          </Box>
          <Box>
            <IconButton onClick={handleDownload} disabled={!previewUrl}>
              <DownloadIcon />
            </IconButton>
            <IconButton onClick={onClose}>
              <CloseIcon />
            </IconButton>
          </Box>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 0, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
        {loading && (
          <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            flex={1}
          >
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Box p={2}>
            <Alert severity="error">{error}</Alert>
          </Box>
        )}

        {previewUrl && !loading && !error && (
          <Box flex={1} display="flex" flexDirection="column">
            {isPdf && (
              <Box flex={1} sx={{ minHeight: 0 }}>
                <iframe
                  src={previewUrl}
                  width="100%"
                  height="100%"
                  style={{ border: 'none' }}
                  title={`Preview of ${document?.file_name}`}
                />
              </Box>
            )}

            {isImage && (
              <Box
                flex={1}
                display="flex"
                justifyContent="center"
                alignItems="center"
                p={2}
                sx={{ minHeight: 0 }}
              >
                <img
                  src={previewUrl}
                  alt={document?.file_name}
                  style={{
                    maxWidth: '100%',
                    maxHeight: '100%',
                    objectFit: 'contain',
                  }}
                />
              </Box>
            )}

            {!isPdf && !isImage && (
              <Box p={2}>
                <Alert severity="info">
                  Preview not available for this file type. You can download the file to view it.
                </Alert>
              </Box>
            )}
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        <Button
          onClick={handleDownload}
          variant="contained"
          disabled={!previewUrl}
          startIcon={<DownloadIcon />}
        >
          Download
        </Button>
      </DialogActions>
    </Dialog>
  );
};