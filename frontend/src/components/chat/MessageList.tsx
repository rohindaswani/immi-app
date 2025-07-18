import React from 'react';
import { Box, Typography, Avatar, Paper } from '@mui/material';
import { format } from 'date-fns';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';

interface Message {
  message_id: string;
  content: string;
  role: 'user' | 'assistant';
  created_at: string;
  is_error?: boolean;
  error_message?: string;
}

interface MessageListProps {
  messages: Message[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  return (
    <Box sx={{ flex: 1, overflowY: 'auto', p: 2 }}>
      {messages.map((message) => (
        <Box
          key={message.message_id}
          sx={{
            display: 'flex',
            justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
            mb: 2,
          }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'flex-start',
              maxWidth: '70%',
              flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
            }}
          >
            <Avatar
              sx={{
                bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main',
                mx: 1,
              }}
            >
              {message.role === 'user' ? <PersonIcon /> : <SmartToyIcon />}
            </Avatar>
            <Paper
              elevation={1}
              sx={{
                p: 2,
                bgcolor: message.role === 'user' ? 'primary.light' : 'grey.100',
                color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
              }}
            >
              {message.is_error ? (
                <Typography color="error" variant="body2">
                  Error: {message.error_message || 'Failed to send message'}
                </Typography>
              ) : (
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {message.content}
                </Typography>
              )}
              <Typography
                variant="caption"
                sx={{
                  display: 'block',
                  mt: 1,
                  opacity: 0.8,
                }}
              >
                {format(new Date(message.created_at), 'MMM d, h:mm a')}
              </Typography>
            </Paper>
          </Box>
        </Box>
      ))}
    </Box>
  );
};

export default MessageList;