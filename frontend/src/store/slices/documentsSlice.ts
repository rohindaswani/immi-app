import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { documentsApi, DocumentResponse, DocumentUpload, DocumentUpdate, DocumentFilters } from '../../api/documents';

interface DocumentsState {
  documents: DocumentResponse[];
  currentDocument: DocumentResponse | null;
  loading: boolean;
  uploading: boolean;
  error: string | null;
  filters: DocumentFilters;
}

const initialState: DocumentsState = {
  documents: [],
  currentDocument: null,
  loading: false,
  uploading: false,
  error: null,
  filters: {},
};

// Async thunks
export const fetchDocuments = createAsyncThunk(
  'documents/fetchDocuments',
  async (filters?: DocumentFilters) => {
    return await documentsApi.getDocuments(filters);
  }
);

export const fetchDocument = createAsyncThunk(
  'documents/fetchDocument',
  async (documentId: string) => {
    return await documentsApi.getDocument(documentId);
  }
);

export const uploadDocument = createAsyncThunk(
  'documents/uploadDocument',
  async (documentData: DocumentUpload) => {
    return await documentsApi.uploadDocument(documentData);
  }
);

export const updateDocument = createAsyncThunk(
  'documents/updateDocument',
  async ({ documentId, updates }: { documentId: string; updates: DocumentUpdate }) => {
    return await documentsApi.updateDocument(documentId, updates);
  }
);

export const deleteDocument = createAsyncThunk(
  'documents/deleteDocument',
  async (documentId: string) => {
    await documentsApi.deleteDocument(documentId);
    return documentId;
  }
);

export const getDocumentDownloadUrl = createAsyncThunk(
  'documents/getDocumentDownloadUrl',
  async (documentId: string) => {
    return await documentsApi.getDocumentDownloadUrl(documentId);
  }
);

const documentsSlice = createSlice({
  name: 'documents',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<DocumentFilters>) => {
      state.filters = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentDocument: (state) => {
      state.currentDocument = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch documents
      .addCase(fetchDocuments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocuments.fulfilled, (state, action) => {
        state.loading = false;
        state.documents = action.payload;
      })
      .addCase(fetchDocuments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch documents';
      })
      
      // Fetch single document
      .addCase(fetchDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocument.fulfilled, (state, action) => {
        state.loading = false;
        state.currentDocument = action.payload;
      })
      .addCase(fetchDocument.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch document';
      })
      
      // Upload document
      .addCase(uploadDocument.pending, (state) => {
        state.uploading = true;
        state.error = null;
      })
      .addCase(uploadDocument.fulfilled, (state, action) => {
        state.uploading = false;
        state.documents.unshift(action.payload);
      })
      .addCase(uploadDocument.rejected, (state, action) => {
        state.uploading = false;
        state.error = action.error.message || 'Failed to upload document';
      })
      
      // Update document
      .addCase(updateDocument.fulfilled, (state, action) => {
        const index = state.documents.findIndex(doc => doc.document_id === action.payload.document_id);
        if (index !== -1) {
          state.documents[index] = action.payload;
        }
        if (state.currentDocument?.document_id === action.payload.document_id) {
          state.currentDocument = action.payload;
        }
      })
      .addCase(updateDocument.rejected, (state, action) => {
        state.error = action.error.message || 'Failed to update document';
      })
      
      // Delete document
      .addCase(deleteDocument.fulfilled, (state, action) => {
        state.documents = state.documents.filter(doc => doc.document_id !== action.payload);
        if (state.currentDocument?.document_id === action.payload) {
          state.currentDocument = null;
        }
      })
      .addCase(deleteDocument.rejected, (state, action) => {
        state.error = action.error.message || 'Failed to delete document';
      });
  },
});

export const { setFilters, clearError, clearCurrentDocument } = documentsSlice.actions;
export default documentsSlice.reducer;