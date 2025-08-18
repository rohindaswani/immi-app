import React, { useState } from 'react';
import {
  Box,
  Button,
  Collapse,
  Paper,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Grid,
  Alert,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  AdminPanelSettings as AdminIcon,
  DataObject as DataIcon,
  Psychology as AiIcon,
  Warning as WarningIcon,
  CheckCircle as SuccessIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material';

interface ExtractedData {
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
}

interface ExtractionDataPanelProps {
  documentId: string;
  onExtract?: (documentId: string) => Promise<ExtractedData | null>;
  initialData?: ExtractedData;
}

export const ExtractionDataPanel: React.FC<ExtractionDataPanelProps> = ({
  documentId,
  onExtract,
  initialData,
}) => {
  const [open, setOpen] = useState(false);
  const [extractionData, setExtractionData] = useState<ExtractedData | null>(initialData || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExtract = async () => {
    if (!onExtract) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await onExtract(documentId);
      setExtractionData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Extraction failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return 'null';
    if (typeof value === 'object') return JSON.stringify(value, null, 2);
    return String(value);
  };

  const renderDataSection = (title: string, data: Record<string, any> | undefined, icon: React.ReactNode) => {
    if (!data || Object.keys(data).length === 0) {
      return (
        <Box sx={{ mb: 2 }}>
          <Box display="flex" alignItems="center" gap={1} mb={1}>
            {icon}
            <Typography variant="h6" color="text.secondary">
              {title}
            </Typography>
          </Box>
          <Alert severity="info" sx={{ py: 1 }}>
            No {title.toLowerCase()} available
          </Alert>
        </Box>
      );
    }

    return (
      <Box sx={{ mb: 2 }}>
        <Box display="flex" alignItems="center" gap={1} mb={1}>
          {icon}
          <Typography variant="h6">
            {title}
          </Typography>
          <Chip label={`${Object.keys(data).length} fields`} size="small" />
        </Box>
        <Paper variant="outlined" sx={{ p: 2, backgroundColor: 'grey.50' }}>
          <Grid container spacing={1}>
            {Object.entries(data).map(([key, value]) => (
              <Grid item xs={12} key={key}>
                <Box display="flex" alignItems="flex-start" gap={1}>
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: 'bold',
                      color: 'primary.main',
                      minWidth: '120px',
                      fontFamily: 'monospace',
                    }}
                  >
                    {key}:
                  </Typography>
                  <Typography
                    variant="body2"
                    sx={{
                      flexGrow: 1,
                      fontFamily: 'monospace',
                      backgroundColor: 'white',
                      p: 0.5,
                      borderRadius: 0.5,
                      border: '1px solid',
                      borderColor: 'grey.300',
                    }}
                  >
                    {formatValue(value)}
                  </Typography>
                  <Tooltip title="Copy to clipboard">
                    <IconButton
                      size="small"
                      onClick={() => handleCopyToClipboard(formatValue(value))}
                    >
                      <CopyIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Paper>
      </Box>
    );
  };

  return (
    <Box>
      <Button
        variant="outlined"
        size="small"
        startIcon={<AdminIcon />}
        onClick={() => setOpen(!open)}
        sx={{
          mb: 1,
          borderColor: 'orange.main',
          color: 'orange.main',
          '&:hover': {
            borderColor: 'orange.dark',
            backgroundColor: 'orange.50',
          },
        }}
      >
        Staff: Extraction Data
      </Button>

      <Collapse in={open}>
        <Paper
          variant="outlined"
          sx={{
            p: 2,
            mt: 1,
            backgroundColor: 'warning.50',
            borderColor: 'warning.main',
            borderWidth: 2,
          }}
        >
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <AdminIcon color="warning" />
            <Typography variant="h6" color="warning.dark">
              Staff Panel - Document Extraction Data
            </Typography>
            {!extractionData && onExtract && (
              <Button
                variant="contained"
                size="small"
                onClick={handleExtract}
                disabled={loading}
                startIcon={<AiIcon />}
              >
                {loading ? 'Extracting...' : 'Extract Data'}
              </Button>
            )}
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {extractionData ? (
            <Box>
              {/* Extraction Status */}
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                {extractionData.extraction_successful ? (
                  <SuccessIcon color="success" />
                ) : (
                  <WarningIcon color="error" />
                )}
                <Typography variant="subtitle1">
                  Extraction Status: {extractionData.extraction_successful ? 'Success' : 'Failed'}
                </Typography>
                {extractionData.document_type_detected && (
                  <Chip
                    label={`Detected: ${extractionData.document_type_detected}`}
                    size="small"
                    color="primary"
                  />
                )}
              </Box>

              {/* Warnings */}
              {extractionData.warnings && extractionData.warnings.length > 0 && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Extraction Warnings:
                  </Typography>
                  <ul style={{ margin: 0, paddingLeft: '20px' }}>
                    {extractionData.warnings.map((warning, index) => (
                      <li key={index}>
                        <Typography variant="body2">{warning}</Typography>
                      </li>
                    ))}
                  </ul>
                </Alert>
              )}

              {/* Mapped Data Sections */}
              <Divider sx={{ my: 2 }} />

              {extractionData.mapped_data ? (
                <>
                  {renderDataSection(
                    'Document Metadata Updates',
                    extractionData.mapped_data.document_metadata,
                    <DataIcon color="primary" />
                  )}

                  {renderDataSection(
                    'Profile Updates',
                    extractionData.mapped_data.profile_updates,
                    <AdminIcon color="secondary" />
                  )}

                  {extractionData.mapped_data.confidence_info && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="h6" gutterBottom>
                        Confidence Scores
                      </Typography>
                      <Box display="flex" gap={1} flexWrap="wrap">
                        {Object.entries(extractionData.mapped_data.confidence_info).map(([key, value]) => (
                          <Chip
                            key={key}
                            label={`${key}: ${(value * 100).toFixed(0)}%`}
                            size="small"
                            color={value > 0.7 ? 'success' : value > 0.5 ? 'warning' : 'error'}
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                </>
              ) : (
                renderDataSection(
                  'Raw Extracted Fields',
                  extractionData.extracted_fields,
                  <DataIcon color="primary" />
                )
              )}

              {/* Raw Extracted Text */}
              {extractionData.extracted_text && (
                <Accordion sx={{ mt: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="h6">Raw OCR Text ({extractionData.extracted_text.length} chars)</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box
                      sx={{
                        backgroundColor: 'grey.100',
                        p: 2,
                        borderRadius: 1,
                        fontFamily: 'monospace',
                        fontSize: '12px',
                        maxHeight: '300px',
                        overflow: 'auto',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                      }}
                    >
                      {extractionData.extracted_text}
                    </Box>
                    <Box mt={1}>
                      <Button
                        size="small"
                        startIcon={<CopyIcon />}
                        onClick={() => handleCopyToClipboard(extractionData.extracted_text || '')}
                      >
                        Copy Text
                      </Button>
                    </Box>
                  </AccordionDetails>
                </Accordion>
              )}
            </Box>
          ) : (
            <Alert severity="info">
              No extraction data available. Click "Extract Data" to analyze this document.
            </Alert>
          )}
        </Paper>
      </Collapse>
    </Box>
  );
};