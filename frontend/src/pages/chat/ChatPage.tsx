import React, { useEffect } from 'react';
import { Box, Grid, Paper, useTheme, useMediaQuery, Alert } from '@mui/material';
import { ChatInterface, ConversationList } from '../../components/chat';
import { useNavigate, useParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch } from '../../store';
import {
  fetchConversations,
  fetchConversation,
  createConversation,
  deleteConversation,
  sendMessage,
  clearCurrentConversation,
  selectConversations,
  selectCurrentConversation,
  selectChatLoading,
  selectChatError,
} from '../../store/slices/chatSlice';

const ChatPage: React.FC = () => {
  console.log('ChatPage - Rendering');
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const { conversationId } = useParams<{ conversationId?: string }>();
  
  const conversations = useSelector(selectConversations);
  const currentConversation = useSelector(selectCurrentConversation);
  const loading = useSelector(selectChatLoading);
  const error = useSelector(selectChatError);
  
  console.log('ChatPage - State:', { conversations, loading, error });

  // Load conversations on mount
  useEffect(() => {
    console.log('ChatPage - Loading conversations');
    dispatch(fetchConversations())
      .unwrap()
      .then(() => console.log('ChatPage - Conversations loaded'))
      .catch((err) => console.error('ChatPage - Error loading conversations:', err));
  }, [dispatch]);

  // Load conversation when ID changes
  useEffect(() => {
    if (conversationId) {
      dispatch(fetchConversation(conversationId));
    } else {
      dispatch(clearCurrentConversation());
    }
  }, [conversationId, dispatch]);

  const handleSelectConversation = (id: string) => {
    navigate(`/chat/${id}`);
  };

  const handleCreateConversation = async () => {
    try {
      const result = await dispatch(createConversation({ title: undefined })).unwrap();
      navigate(`/chat/${result.conversation_id}`);
    } catch (err) {
      console.error('Failed to create conversation:', err);
    }
  };

  const handleDeleteConversation = async (id: string) => {
    try {
      await dispatch(deleteConversation(id)).unwrap();
      if (conversationId === id) {
        navigate('/chat');
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!conversationId) return;

    try {
      await dispatch(
        sendMessage({
          conversationId,
          data: { content },
        })
      ).unwrap();
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  return (
    <Box sx={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
      {error && (
        <Alert severity="error" sx={{ m: 2 }}>
          {error}
        </Alert>
      )}
      
      <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <Grid container sx={{ height: '100%' }}>
          {!isMobile && (
            <Grid item xs={12} sm={4} md={3}>
              <Paper
                elevation={0}
                sx={{
                  height: '100%',
                  borderRadius: 0,
                  borderRight: 1,
                  borderColor: 'divider',
                }}
              >
                <ConversationList
                  conversations={conversations}
                  selectedConversationId={conversationId}
                  onSelectConversation={handleSelectConversation}
                  onCreateConversation={handleCreateConversation}
                  onDeleteConversation={handleDeleteConversation}
                />
              </Paper>
            </Grid>
          )}
          
          <Grid item xs={12} sm={8} md={9} sx={{ height: '100%' }}>
            <ChatInterface
              messages={currentConversation?.messages || []}
              isLoading={loading.messages}
              isSending={loading.sending}
              conversationId={conversationId}
              onSendMessage={handleSendMessage}
            />
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default ChatPage;