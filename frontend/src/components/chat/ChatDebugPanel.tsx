import React, { useState, useEffect } from 'react';
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
  IconButton,
  Alert,
  CircularProgress,
  Tooltip,
  Divider,
  Grid,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  AdminPanelSettings as AdminIcon,
  BugReport as DebugIcon,
  ContentCopy as CopyIcon,
  Refresh as RefreshIcon,
  Code as CodeIcon,
  Description as DocumentIcon,
  Psychology as AiIcon,
} from '@mui/icons-material';
import { chatApi } from '../../api/chat';

interface ChatDebugPanelProps {
  conversationId: string;
  messageId: string;
  isStaff?: boolean;
}

interface DebugInfo {
  message_id: string;
  conversation_id: string;
  role: string;
  content: string;
  model_used?: string;
  tokens_used?: number;
  response_time_ms?: number;
  created_at: string;
  debug_info: {
    system_prompt?: string;
    document_context?: any;
    messages_sent?: any[];
    response?: any;
    rule_matched?: boolean;
    response_type?: string;
    total_messages?: number;
    model?: string;
  };
}

export const ChatDebugPanel: React.FC<ChatDebugPanelProps> = ({
  conversationId,
  messageId,
  isStaff = true,
}) => {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [debugInfo, setDebugInfo] = useState<DebugInfo | null>(null);

  const fetchDebugInfo = async () => {
    if (!conversationId || !messageId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await chatApi.getMessageDebugInfo(conversationId, messageId);
      setDebugInfo(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch debug info');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open && !debugInfo) {
      fetchDebugInfo();
    }
  }, [open, conversationId, messageId]);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const formatJson = (obj: any) => {
    return JSON.stringify(obj, null, 2);
  };

  if (!isStaff) {
    return null;
  }

  return (
    <Box sx={{ mt: 2 }}>
      <Button
        variant="outlined"
        size="small"
        startIcon={<AdminIcon />}
        onClick={() => setOpen(!open)}
        sx={{
          borderColor: 'orange.main',
          color: 'orange.main',
          '&:hover': {
            borderColor: 'orange.dark',
            backgroundColor: 'orange.50',
          },
        }}
      >
        Staff: AI Debug Info
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
              Staff Debug Panel - AI Chat Analysis
            </Typography>
            <Box flexGrow={1} />
            <Tooltip title="Refresh">
              <IconButton onClick={fetchDebugInfo} disabled={loading} size="small">
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {loading && (
            <Box display="flex" justifyContent="center" p={3}>
              <CircularProgress />
            </Box>
          )}

          {debugInfo && (
            <Box>
              {/* Message Metadata */}
              <Box mb={3}>
                <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                  Message Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="body2" color="text.secondary">Role</Typography>
                    <Chip label={debugInfo.role} size="small" color={debugInfo.role === 'assistant' ? 'primary' : 'default'} />
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="body2" color="text.secondary">Model Used</Typography>
                    <Chip label={debugInfo.model_used || 'N/A'} size="small" />
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="body2" color="text.secondary">Tokens</Typography>
                    <Chip label={debugInfo.tokens_used || 0} size="small" />
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="body2" color="text.secondary">Response Time</Typography>
                    <Chip label={`${debugInfo.response_time_ms || 0}ms`} size="small" />
                  </Grid>
                </Grid>
              </Box>

              <Divider sx={{ my: 2 }} />

              {/* System Prompt */}
              {debugInfo.debug_info?.system_prompt && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <CodeIcon />
                      <Typography>System Prompt ({debugInfo.debug_info.system_prompt.length} chars)</Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box
                      sx={{
                        backgroundColor: 'grey.100',
                        p: 2,
                        borderRadius: 1,
                        fontFamily: 'monospace',
                        fontSize: '12px',
                        whiteSpace: 'pre-wrap',
                        maxHeight: '400px',
                        overflow: 'auto',
                      }}
                    >
                      {debugInfo.debug_info.system_prompt}
                    </Box>
                    <Box mt={1}>
                      <Button
                        size="small"
                        startIcon={<CopyIcon />}
                        onClick={() => handleCopy(debugInfo.debug_info.system_prompt!)}
                      >
                        Copy System Prompt
                      </Button>
                    </Box>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Document Context */}
              {debugInfo.debug_info?.document_context && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <DocumentIcon />
                      <Typography>Document Context</Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box
                      sx={{
                        backgroundColor: 'grey.100',
                        p: 2,
                        borderRadius: 1,
                        fontFamily: 'monospace',
                        fontSize: '12px',
                        whiteSpace: 'pre',
                        maxHeight: '400px',
                        overflow: 'auto',
                      }}
                    >
                      {formatJson(debugInfo.debug_info.document_context)}
                    </Box>
                    <Box mt={1}>
                      <Button
                        size="small"
                        startIcon={<CopyIcon />}
                        onClick={() => handleCopy(formatJson(debugInfo.debug_info.document_context))}
                      >
                        Copy Document Context
                      </Button>
                    </Box>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Messages Sent to AI */}
              {debugInfo.debug_info?.messages_sent && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <AiIcon />
                      <Typography>Messages Sent to AI ({debugInfo.debug_info.messages_sent.length})</Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    {debugInfo.debug_info.messages_sent.map((msg, index) => (
                      <Box key={index} mb={2}>
                        <Chip 
                          label={`${msg.role} (${index + 1}/${debugInfo.debug_info.messages_sent!.length})`} 
                          size="small" 
                          sx={{ mb: 1 }}
                        />
                        <Box
                          sx={{
                            backgroundColor: msg.role === 'system' ? 'info.50' : 'grey.50',
                            p: 2,
                            borderRadius: 1,
                            fontFamily: 'monospace',
                            fontSize: '12px',
                            whiteSpace: 'pre-wrap',
                            maxHeight: '200px',
                            overflow: 'auto',
                            border: '1px solid',
                            borderColor: msg.role === 'system' ? 'info.main' : 'grey.300',
                          }}
                        >
                          {msg.content}
                        </Box>
                      </Box>
                    ))}
                  </AccordionDetails>
                </Accordion>
              )}

              {/* AI Response Details */}
              {debugInfo.debug_info?.response && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <DebugIcon />
                      <Typography>AI Response Details</Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box
                      sx={{
                        backgroundColor: 'grey.100',
                        p: 2,
                        borderRadius: 1,
                        fontFamily: 'monospace',
                        fontSize: '12px',
                        whiteSpace: 'pre',
                        maxHeight: '400px',
                        overflow: 'auto',
                      }}
                    >
                      {formatJson(debugInfo.debug_info.response)}
                    </Box>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Response Type Info */}
              {(debugInfo.debug_info?.rule_matched || debugInfo.debug_info?.response_type) && (
                <Box mt={2}>
                  <Alert severity="info">
                    <Typography variant="body2">
                      <strong>Response Type:</strong> {debugInfo.debug_info.response_type || 'AI Generated'}
                      {debugInfo.debug_info.rule_matched && ' (Rule-based pattern matched)'}
                    </Typography>
                  </Alert>
                </Box>
              )}
            </Box>
          )}
        </Paper>
      </Collapse>
    </Box>
  );
};