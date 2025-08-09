import React from 'react';
import {
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
  Box,
  IconButton,
  Divider,
  Fab,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { format } from 'date-fns';

interface Conversation {
  conversation_id: string;
  title?: string;
  updated_at: string;
  message_count: number;
  last_message?: {
    content: string;
  };
}

interface ConversationListProps {
  conversations: Conversation[];
  selectedConversationId?: string;
  onSelectConversation: (conversationId: string) => void;
  onCreateConversation: () => void;
  onDeleteConversation: (conversationId: string) => void;
}

const ConversationList: React.FC<ConversationListProps> = ({
  conversations,
  selectedConversationId,
  onSelectConversation,
  onCreateConversation,
  onDeleteConversation,
}) => {
  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6">Conversations</Typography>
      </Box>
      
      <List sx={{ flex: 1, overflowY: 'auto' }}>
        {conversations.length === 0 ? (
          <Box sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              No conversations yet. Start a new one!
            </Typography>
          </Box>
        ) : (
          conversations.map((conversation) => (
            <React.Fragment key={conversation.conversation_id}>
              <ListItem
                disablePadding
                secondaryAction={
                  <IconButton
                    edge="end"
                    aria-label="delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteConversation(conversation.conversation_id);
                    }}
                    size="small"
                  >
                    <DeleteIcon />
                  </IconButton>
                }
              >
                <ListItemButton
                  selected={selectedConversationId === conversation.conversation_id}
                  onClick={() => onSelectConversation(conversation.conversation_id)}
                >
                  <ListItemText
                    primary={
                      conversation.title || 
                      (conversation.last_message 
                        ? truncateText(conversation.last_message.content, 50)
                        : 'New Conversation')
                    }
                    secondary={
                      <>
                        <Typography variant="caption" component="span">
                          {format(new Date(conversation.updated_at), 'MMM d, h:mm a')}
                        </Typography>
                        <Typography variant="caption" component="span" sx={{ mx: 1 }}>
                          •
                        </Typography>
                        <Typography variant="caption" component="span">
                          {conversation.message_count} messages
                        </Typography>
                      </>
                    }
                  />
                </ListItemButton>
              </ListItem>
              <Divider />
            </React.Fragment>
          ))
        )}
      </List>

      <Box sx={{ p: 2 }}>
        <Fab
          color="primary"
          variant="extended"
          fullWidth
          onClick={onCreateConversation}
          sx={{ width: '100%' }}
        >
          <AddIcon sx={{ mr: 1 }} />
          New Conversation
        </Fab>
      </Box>
    </Box>
  );
};

export default ConversationList;