import React, { useState, useEffect } from 'react';
import { Box, Grid, Paper, useTheme, useMediaQuery } from '@mui/material';
import { ChatInterface, ConversationList } from '../../components/chat';
import { useNavigate, useParams } from 'react-router-dom';

// Temporary mock data - will be replaced with Redux in PR4
const mockConversations = [
  {
    conversation_id: '1',
    title: 'H1-B Status Questions',
    updated_at: new Date().toISOString(),
    message_count: 5,
    last_message: {
      content: 'What documents do I need for H1-B renewal?',
    },
  },
];

const mockMessages = [
  {
    message_id: '1',
    content: 'What documents do I need for H1-B renewal?',
    role: 'user' as const,
    created_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    message_id: '2',
    content: 'For H1-B renewal, you typically need: valid passport, current I-94, employment verification letter, recent pay stubs, and Form I-797. Based on your profile, your current H1-B expires in 6 months.',
    role: 'assistant' as const,
    created_at: new Date(Date.now() - 3000000).toISOString(),
  },
];

const ChatPage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();
  const { conversationId } = useParams<{ conversationId?: string }>();
  
  const [conversations, setConversations] = useState(mockConversations);
  const [messages, setMessages] = useState(mockMessages);
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    // TODO: Load conversations from Redux store
  }, []);

  useEffect(() => {
    if (conversationId) {
      // TODO: Load messages for the selected conversation
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
      }, 500);
    }
  }, [conversationId]);

  const handleSelectConversation = (id: string) => {
    navigate(`/chat/${id}`);
  };

  const handleCreateConversation = () => {
    // TODO: Create new conversation via Redux
    const newConversation = {
      conversation_id: Date.now().toString(),
      title: undefined,
      updated_at: new Date().toISOString(),
      message_count: 0,
    };
    setConversations([newConversation, ...conversations]);
    navigate(`/chat/${newConversation.conversation_id}`);
  };

  const handleDeleteConversation = (id: string) => {
    // TODO: Delete conversation via Redux
    setConversations(conversations.filter(c => c.conversation_id !== id));
    if (conversationId === id) {
      navigate('/chat');
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!conversationId) return;

    setIsSending(true);
    
    // TODO: Send message via Redux
    const userMessage = {
      message_id: Date.now().toString(),
      content,
      role: 'user' as const,
      created_at: new Date().toISOString(),
    };
    
    setMessages([...messages, userMessage]);
    
    // Simulate AI response
    setTimeout(() => {
      const assistantMessage = {
        message_id: (Date.now() + 1).toString(),
        content: 'This is a placeholder response. Full AI integration will be implemented in PR5.',
        role: 'assistant' as const,
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsSending(false);
    }, 1000);
  };

  return (
    <Box sx={{ height: 'calc(100vh - 64px)', display: 'flex' }}>
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
        
        <Grid item xs={12} sm={8} md={9}>
          <Box sx={{ height: '100%', p: 2 }}>
            <ChatInterface
              messages={messages}
              isLoading={isLoading}
              isSending={isSending}
              conversationId={conversationId}
              onSendMessage={handleSendMessage}
            />
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ChatPage;