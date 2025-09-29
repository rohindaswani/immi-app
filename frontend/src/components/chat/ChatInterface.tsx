import React from 'react';
import { Box, Paper, Typography, CircularProgress } from '@mui/material';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

interface Message {
  message_id: string;
  content: string;
  role: 'user' | 'assistant';
  created_at: string;
  is_error?: boolean;
  error_message?: string;
}

interface ChatInterfaceProps {
  messages: Message[];
  isLoading?: boolean;
  isSending?: boolean;
  conversationId?: string;
  onSendMessage: (message: string) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  isLoading = false,
  isSending = false,
  conversationId,
  onSendMessage,
}) => {
  if (!conversationId) {
    return (
      <Box
        sx={{
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 4,
        }}
      >
        <Typography variant="h6" color="text.secondary" textAlign="center">
          Select a conversation or create a new one to start chatting
        </Typography>
      </Box>
    );
  }

  return (
    <Paper
      elevation={1}
      sx={{
        height: '600px',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 2,
        overflow: 'hidden',
        m: 2,
      }}
    >
      <Box
        sx={{
          p: 2,
          borderBottom: 1,
          borderColor: 'divider',
          bgcolor: 'primary.main',
          color: 'primary.contrastText',
        }}
      >
        <Typography variant="h6">Immigration Assistant</Typography>
        <Typography variant="caption">
          Ask questions about your immigration status, documents, and timeline
        </Typography>
      </Box>

      {isLoading ? (
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <CircularProgress />
        </Box>
      ) : (
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <MessageList messages={messages} conversationId={conversationId} />
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
            <MessageInput 
              onSendMessage={onSendMessage} 
              isLoading={isSending}
              disabled={!conversationId}
            />
          </Box>
        </Box>
      )}
    </Paper>
  );
};

export default ChatInterface;