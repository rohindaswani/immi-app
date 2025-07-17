from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    """Base schema for chat messages"""
    content: str = Field(..., min_length=1, max_length=10000)
    role: str = Field(..., pattern="^(user|assistant)$")


class MessageCreate(MessageBase):
    """Schema for creating a new message"""
    pass


class MessageResponse(MessageBase):
    """Schema for a message response"""
    message_id: UUID
    conversation_id: UUID
    created_at: datetime
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    response_time_ms: Optional[int] = None
    is_error: bool = False
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    """Base schema for conversations"""
    title: Optional[str] = None


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation"""
    pass


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation"""
    title: Optional[str] = None
    is_active: Optional[bool] = None


class ConversationResponse(ConversationBase):
    """Schema for a conversation response"""
    conversation_id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0
    last_message: Optional[MessageResponse] = None

    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    """Schema for a conversation with its messages"""
    messages: List[MessageResponse] = []


class ConversationContextBase(BaseModel):
    """Base schema for conversation context"""
    context_type: str = Field(..., pattern="^(profile|document|travel|employment|status)$")
    entity_id: UUID
    entity_table: str
    access_reason: Optional[str] = None
    data_summary: Optional[Dict[str, Any]] = None


class ConversationContextResponse(ConversationContextBase):
    """Schema for conversation context response"""
    context_id: UUID
    conversation_id: UUID
    message_id: Optional[UUID] = None
    accessed_at: datetime

    class Config:
        from_attributes = True


class SendMessageRequest(BaseModel):
    """Schema for sending a message"""
    content: str = Field(..., min_length=1, max_length=10000)


class SendMessageResponse(BaseModel):
    """Schema for the response to sending a message"""
    user_message: MessageResponse
    assistant_message: MessageResponse
    contexts_accessed: List[ConversationContextResponse] = []