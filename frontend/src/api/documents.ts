import apiClient from './client';

export interface DocumentResponse {
  document_id: string;
  user_id: string;
  document_type: string;
  document_subtype?: string;
  document_number?: string;
  issuing_authority?: string;
  related_immigration_type?: string;
  issue_date?: string;
  expiry_date?: string;
  file_name: string;
  file_size: number;
  file_type: string;
  is_verified: boolean;
  upload_date: string;
  tags: string[];
  extraction_data?: {
    extracted_fields?: Record<string, any>;
    mapped_data?: {
      document_metadata?: Record<string, any>;
      profile_updates?: Record<string, any>;
      warnings?: string[];
      confidence_info?: Record<string, number>;
    };
    confidence_scores?: Record<string, number>;
    warnings?: string[];
    extracted_text?: string;
    document_type_detected?: string;
    extraction_successful?: boolean;
    was_extracted?: boolean;
  };
}

export interface DocumentUpload {
  file: File;
  document_type: string;
  document_subtype?: string;
  document_number?: string;
  issuing_authority?: string;
  related_immigration_type?: string;
  issue_date?: string;
  expiry_date?: string;
  tags?: string[];
}

export interface DocumentUpdate {
  document_type?: string;
  document_subtype?: string;
  document_number?: string;
  issuing_authority?: string;
  related_immigration_type?: string;
  issue_date?: string;
  expiry_date?: string;
  tags?: string[];
  is_verified?: boolean;
}

export interface DocumentFilters {
  document_type?: string;
  expiry_before?: string;
  expiry_after?: string;
}

export const documentsApi = {
  // Get all documents with optional filtering
  getDocuments: async (filters?: DocumentFilters): Promise<DocumentResponse[]> => {
    const params = new URLSearchParams();
    if (filters?.document_type) params.append('document_type', filters.document_type);
    if (filters?.expiry_before) params.append('expiry_before', filters.expiry_before);
    if (filters?.expiry_after) params.append('expiry_after', filters.expiry_after);
    
    const response = await apiClient.get(`/documents?${params.toString()}`);
    return response.data;
  },

  // Get a specific document
  getDocument: async (documentId: string): Promise<DocumentResponse> => {
    const response = await apiClient.get(`/documents/${documentId}`);
    return response.data;
  },

  // Upload a document
  uploadDocument: async (documentData: DocumentUpload): Promise<DocumentResponse> => {
    const formData = new FormData();
    formData.append('file', documentData.file);
    formData.append('document_type', documentData.document_type);
    
    if (documentData.document_subtype) formData.append('document_subtype', documentData.document_subtype);
    if (documentData.document_number) formData.append('document_number', documentData.document_number);
    if (documentData.issuing_authority) formData.append('issuing_authority', documentData.issuing_authority);
    if (documentData.related_immigration_type) formData.append('related_immigration_type', documentData.related_immigration_type);
    if (documentData.issue_date) formData.append('issue_date', documentData.issue_date);
    if (documentData.expiry_date) formData.append('expiry_date', documentData.expiry_date);
    if (documentData.tags && documentData.tags.length > 0) {
      formData.append('tags', documentData.tags.join(','));
    }

    const response = await apiClient.post('/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Update document metadata
  updateDocument: async (documentId: string, updates: DocumentUpdate): Promise<DocumentResponse> => {
    const response = await apiClient.put(`/documents/${documentId}`, updates);
    return response.data;
  },

  // Delete a document
  deleteDocument: async (documentId: string): Promise<void> => {
    await apiClient.delete(`/documents/${documentId}`);
  },

  // Get document download URL
  getDocumentDownloadUrl: async (documentId: string): Promise<string> => {
    const response = await apiClient.get(`/documents/${documentId}/download`);
    return response.data.download_url;
  },

  // Get document preview URL (same as download but will add download=false parameter)
  getDocumentPreviewUrl: async (documentId: string): Promise<string> => {
    const response = await apiClient.get(`/documents/${documentId}/download`);
    const downloadUrl = response.data.download_url;
    // Append download=false parameter for preview
    const url = new URL(downloadUrl);
    url.searchParams.set('download', 'false');
    return url.toString();
  },

  // Extract data from document using OCR
  extractDocumentData: async (documentId: string): Promise<any> => {
    const response = await apiClient.post(`/documents/${documentId}/extract-data`);
    return response.data;
  },
};