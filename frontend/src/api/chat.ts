import apiClient from './client';
import { 
  ConversationResponse, 
  ConversationWithMessages,
  SendMessageRequest,
  SendMessageResponse,
  ConversationCreate,
  ConversationUpdate
} from '../types/chat';

export const chatApi = {
  // Create a new conversation
  createConversation: async (data: ConversationCreate): Promise<ConversationResponse> => {
    console.log('chatApi - Creating conversation');
    const response = await apiClient.post('/chat/conversations', data);
    return response.data;
  },

  // List all conversations for the current user
  listConversations: async (): Promise<ConversationResponse[]> => {
    const response = await apiClient.get('/chat/conversations');
    return response.data;
  },

  // Get a specific conversation with messages
  getConversation: async (conversationId: string): Promise<ConversationWithMessages> => {
    const response = await apiClient.get(`/chat/conversations/${conversationId}`);
    return response.data;
  },

  // Update a conversation
  updateConversation: async (
    conversationId: string, 
    data: ConversationUpdate
  ): Promise<ConversationResponse> => {
    const response = await apiClient.patch(`/chat/conversations/${conversationId}`, data);
    return response.data;
  },

  // Send a message to a conversation
  sendMessage: async (
    conversationId: string,
    data: SendMessageRequest
  ): Promise<SendMessageResponse> => {
    const response = await apiClient.post(
      `/chat/conversations/${conversationId}/messages`,
      data
    );
    return response.data;
  },

  // Delete a conversation
  deleteConversation: async (conversationId: string): Promise<void> => {
    await apiClient.delete(`/chat/conversations/${conversationId}`);
  },

  // Get debug information for a message (staff only)
  getMessageDebugInfo: async (conversationId: string, messageId: string): Promise<any> => {
    const response = await apiClient.get(`/chat/conversations/${conversationId}/messages/${messageId}/debug`);
    return response.data;
  },
};