export interface Message {
  message_id: string;
  conversation_id: string;
  content: string;
  role: 'user' | 'assistant';
  created_at: string;
  model_used?: string;
  tokens_used?: number;
  response_time_ms?: number;
  is_error: boolean;
  error_message?: string;
}

export interface ConversationBase {
  title?: string;
}

export interface ConversationCreate extends ConversationBase {}

export interface ConversationUpdate {
  title?: string;
  is_active?: boolean;
}

export interface ConversationResponse extends ConversationBase {
  conversation_id: string;
  user_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message?: Message;
}

export interface ConversationWithMessages extends ConversationResponse {
  messages: Message[];
}

export interface ConversationContext {
  context_id: string;
  conversation_id: string;
  message_id?: string;
  context_type: 'profile' | 'document' | 'travel' | 'employment' | 'status';
  entity_id: string;
  entity_table: string;
  access_reason?: string;
  data_summary?: Record<string, any>;
  accessed_at: string;
}

export interface SendMessageRequest {
  content: string;
}

export interface SendMessageResponse {
  user_message: Message;
  assistant_message: Message;
  contexts_accessed: ConversationContext[];
}