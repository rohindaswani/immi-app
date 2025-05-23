import React, { useState } from 'react';
import {
  Box,
  Button,
  Container,
  Fab,
  Typography,
} from '@mui/material';
import {
  Add as AddIcon,
  CloudUpload as UploadIcon,
} from '@mui/icons-material';

import { DocumentUpload } from '../../components/documents/DocumentUpload';
import { DocumentList } from '../../components/documents/DocumentList';
import { DocumentResponse } from '../../api/documents';

export const DocumentsPage: React.FC = () => {
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);

  const handleUploadSuccess = () => {
    // Documents will be automatically refreshed via Redux
    console.log('Upload successful');
  };

  const handleEditDocument = (document: DocumentResponse) => {
    // This could open an edit dialog or navigate to an edit page
    console.log('Edit document:', document.document_id);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          sx={{ mb: 4 }}
        >
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Documents
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Manage your immigration and personal documents securely
            </Typography>
          </Box>
          
          <Button
            variant="contained"
            startIcon={<UploadIcon />}
            onClick={() => setUploadDialogOpen(true)}
            size="large"
          >
            Upload Documents
          </Button>
        </Box>

        {/* Document List */}
        <DocumentList onEditDocument={handleEditDocument} />

        {/* Floating Action Button (alternative upload button) */}
        <Fab
          color="primary"
          aria-label="upload documents"
          sx={{
            position: 'fixed',
            bottom: 16,
            right: 16,
            display: { xs: 'flex', sm: 'none' }, // Only show on mobile
          }}
          onClick={() => setUploadDialogOpen(true)}
        >
          <AddIcon />
        </Fab>

        {/* Upload Dialog */}
        <DocumentUpload
          open={uploadDialogOpen}
          onClose={() => setUploadDialogOpen(false)}
          onSuccess={handleUploadSuccess}
        />
      </Box>
    </Container>
  );
};