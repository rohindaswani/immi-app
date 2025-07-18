import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { chatApi } from '../../api/chat';
import {
  ConversationResponse,
  ConversationWithMessages,
  Message,
  SendMessageRequest,
  ConversationCreate,
  ConversationUpdate,
} from '../../types/chat';
import { RootState } from '../index';

interface ChatState {
  conversations: ConversationResponse[];
  currentConversation: ConversationWithMessages | null;
  loading: {
    conversations: boolean;
    messages: boolean;
    sending: boolean;
  };
  error: string | null;
}

const initialState: ChatState = {
  conversations: [],
  currentConversation: null,
  loading: {
    conversations: false,
    messages: false,
    sending: false,
  },
  error: null,
};

// Async thunks
export const fetchConversations = createAsyncThunk(
  'chat/fetchConversations',
  async () => {
    return await chatApi.listConversations();
  }
);

export const fetchConversation = createAsyncThunk(
  'chat/fetchConversation',
  async (conversationId: string) => {
    return await chatApi.getConversation(conversationId);
  }
);

export const createConversation = createAsyncThunk(
  'chat/createConversation',
  async (data: ConversationCreate) => {
    return await chatApi.createConversation(data);
  }
);

export const updateConversation = createAsyncThunk(
  'chat/updateConversation',
  async ({ conversationId, data }: { conversationId: string; data: ConversationUpdate }) => {
    return await chatApi.updateConversation(conversationId, data);
  }
);

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ conversationId, data }: { conversationId: string; data: SendMessageRequest }) => {
    return await chatApi.sendMessage(conversationId, data);
  }
);

export const deleteConversation = createAsyncThunk(
  'chat/deleteConversation',
  async (conversationId: string) => {
    await chatApi.deleteConversation(conversationId);
    return conversationId;
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentConversation: (state) => {
      state.currentConversation = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch conversations
    builder
      .addCase(fetchConversations.pending, (state) => {
        state.loading.conversations = true;
        state.error = null;
      })
      .addCase(fetchConversations.fulfilled, (state, action) => {
        state.loading.conversations = false;
        state.conversations = action.payload;
      })
      .addCase(fetchConversations.rejected, (state, action) => {
        state.loading.conversations = false;
        state.error = action.error.message || 'Failed to fetch conversations';
      });

    // Fetch single conversation
    builder
      .addCase(fetchConversation.pending, (state) => {
        state.loading.messages = true;
        state.error = null;
      })
      .addCase(fetchConversation.fulfilled, (state, action) => {
        state.loading.messages = false;
        state.currentConversation = action.payload;
      })
      .addCase(fetchConversation.rejected, (state, action) => {
        state.loading.messages = false;
        state.error = action.error.message || 'Failed to fetch conversation';
      });

    // Create conversation
    builder
      .addCase(createConversation.pending, (state) => {
        state.error = null;
      })
      .addCase(createConversation.fulfilled, (state, action) => {
        state.conversations.unshift(action.payload);
      })
      .addCase(createConversation.rejected, (state, action) => {
        state.error = action.error.message || 'Failed to create conversation';
      });

    // Update conversation
    builder
      .addCase(updateConversation.fulfilled, (state, action) => {
        const index = state.conversations.findIndex(
          (conv) => conv.conversation_id === action.payload.conversation_id
        );
        if (index !== -1) {
          state.conversations[index] = action.payload;
        }
        if (
          state.currentConversation &&
          state.currentConversation.conversation_id === action.payload.conversation_id
        ) {
          state.currentConversation = {
            ...state.currentConversation,
            ...action.payload,
          };
        }
      });

    // Send message
    builder
      .addCase(sendMessage.pending, (state) => {
        state.loading.sending = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.loading.sending = false;
        
        // Add messages to current conversation
        if (state.currentConversation) {
          state.currentConversation.messages.push(
            action.payload.user_message,
            action.payload.assistant_message
          );
          state.currentConversation.message_count += 2;
          state.currentConversation.updated_at = new Date().toISOString();
        }

        // Update conversation in list
        const convIndex = state.conversations.findIndex(
          (conv) => conv.conversation_id === action.meta.arg.conversationId
        );
        if (convIndex !== -1) {
          state.conversations[convIndex].last_message = action.payload.assistant_message;
          state.conversations[convIndex].message_count += 2;
          state.conversations[convIndex].updated_at = new Date().toISOString();
          
          // Move conversation to top
          const [conversation] = state.conversations.splice(convIndex, 1);
          state.conversations.unshift(conversation);
        }
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.loading.sending = false;
        state.error = action.error.message || 'Failed to send message';
      });

    // Delete conversation
    builder
      .addCase(deleteConversation.fulfilled, (state, action) => {
        state.conversations = state.conversations.filter(
          (conv) => conv.conversation_id !== action.payload
        );
        if (
          state.currentConversation &&
          state.currentConversation.conversation_id === action.payload
        ) {
          state.currentConversation = null;
        }
      });
  },
});

// Actions
export const { clearError, clearCurrentConversation } = chatSlice.actions;

// Selectors
export const selectConversations = (state: RootState) => state.chat.conversations;
export const selectCurrentConversation = (state: RootState) => state.chat.currentConversation;
export const selectChatLoading = (state: RootState) => state.chat.loading;
export const selectChatError = (state: RootState) => state.chat.error;

export default chatSlice.reducer;