from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import Depends, HTTPException, status

from app.db.postgres import get_db
from app.db.models import Conversation, Message, ConversationContext, User
from app.schemas.chat import (
    ConversationCreate,
    ConversationResponse,
    ConversationWithMessages,
    ConversationUpdate,
    MessageResponse,
    SendMessageResponse,
    ConversationContextResponse
)
from app.ai.context_service import ContextService
from app.ai.chat_ai_service import ChatAIService


class ChatService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.context_service = ContextService(db)
        self.ai_service = ChatAIService(self.context_service)

    async def create_conversation(
        self, 
        user_id: UUID, 
        conversation_data: ConversationCreate
    ) -> ConversationResponse:
        """Create a new conversation for a user."""
        conversation = Conversation(
            user_id=user_id,
            title=conversation_data.title
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        return ConversationResponse(
            conversation_id=conversation.conversation_id,
            user_id=conversation.user_id,
            title=conversation.title,
            is_active=conversation.is_active,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=0
        )

    async def list_conversations(self, user_id: UUID) -> List[ConversationResponse]:
        """List all conversations for a user."""
        conversations = self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).all()
        
        results = []
        for conv in conversations:
            # Get last message if exists
            last_message = self.db.query(Message).filter(
                Message.conversation_id == conv.conversation_id
            ).order_by(Message.created_at.desc()).first()
            
            # Get message count
            message_count = self.db.query(Message).filter(
                Message.conversation_id == conv.conversation_id
            ).count()
            
            conv_response = ConversationResponse(
                conversation_id=conv.conversation_id,
                user_id=conv.user_id,
                title=conv.title,
                is_active=conv.is_active,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=message_count
            )
            
            if last_message:
                conv_response.last_message = MessageResponse(
                    message_id=last_message.message_id,
                    conversation_id=last_message.conversation_id,
                    content=last_message.content,
                    role=last_message.role,
                    created_at=last_message.created_at,
                    model_used=last_message.model_used,
                    tokens_used=last_message.tokens_used,
                    response_time_ms=last_message.response_time_ms,
                    is_error=last_message.is_error,
                    error_message=last_message.error_message
                )
            
            results.append(conv_response)
        
        return results

    async def get_conversation_with_messages(
        self, 
        conversation_id: UUID, 
        user_id: UUID
    ) -> ConversationWithMessages:
        """Get a conversation with all its messages."""
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get all messages
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
        
        message_responses = [
            MessageResponse(
                message_id=msg.message_id,
                conversation_id=msg.conversation_id,
                content=msg.content,
                role=msg.role,
                created_at=msg.created_at,
                model_used=msg.model_used,
                tokens_used=msg.tokens_used,
                response_time_ms=msg.response_time_ms,
                is_error=msg.is_error,
                error_message=msg.error_message
            )
            for msg in messages
        ]
        
        return ConversationWithMessages(
            conversation_id=conversation.conversation_id,
            user_id=conversation.user_id,
            title=conversation.title,
            is_active=conversation.is_active,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=len(messages),
            messages=message_responses
        )

    async def update_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID,
        update_data: ConversationUpdate
    ) -> ConversationResponse:
        """Update a conversation."""
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        if update_data.title is not None:
            conversation.title = update_data.title
        if update_data.is_active is not None:
            conversation.is_active = update_data.is_active
        
        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(conversation)
        
        # Get message count
        message_count = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).count()
        
        return ConversationResponse(
            conversation_id=conversation.conversation_id,
            user_id=conversation.user_id,
            title=conversation.title,
            is_active=conversation.is_active,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=message_count
        )

    async def send_message(
        self,
        conversation_id: UUID,
        user_id: UUID,
        message_content: str
    ) -> SendMessageResponse:
        """Send a message and get AI response."""
        # Verify conversation belongs to user
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Create user message
        user_message = Message(
            conversation_id=conversation_id,
            content=message_content,
            role="user"
        )
        self.db.add(user_message)
        self.db.commit()
        self.db.refresh(user_message)
        
        # Generate AI response with user context
        ai_response = await self.ai_service.generate_response(
            user_id=user_id,
            conversation_id=conversation_id,
            message_id=user_message.message_id,
            user_message=message_content
        )
        
        # Create assistant message with AI response
        assistant_message = Message(
            conversation_id=conversation_id,
            content=ai_response["content"],
            role="assistant",
            model_used=ai_response["model_used"],
            tokens_used=ai_response["tokens_used"],
            response_time_ms=ai_response["response_time_ms"],
            is_error=ai_response["is_error"],
            error_message=ai_response.get("error_message")
        )
        self.db.add(assistant_message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(assistant_message)
        
        return SendMessageResponse(
            user_message=MessageResponse(
                message_id=user_message.message_id,
                conversation_id=user_message.conversation_id,
                content=user_message.content,
                role=user_message.role,
                created_at=user_message.created_at,
                model_used=user_message.model_used,
                tokens_used=user_message.tokens_used,
                response_time_ms=user_message.response_time_ms,
                is_error=user_message.is_error,
                error_message=user_message.error_message
            ),
            assistant_message=MessageResponse(
                message_id=assistant_message.message_id,
                conversation_id=assistant_message.conversation_id,
                content=assistant_message.content,
                role=assistant_message.role,
                created_at=assistant_message.created_at,
                model_used=assistant_message.model_used,
                tokens_used=assistant_message.tokens_used,
                response_time_ms=assistant_message.response_time_ms,
                is_error=assistant_message.is_error,
                error_message=assistant_message.error_message
            ),
            contexts_accessed=self._get_contexts_for_message(assistant_message.message_id)
        )

    async def delete_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID
    ) -> None:
        """Delete a conversation and all its messages."""
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Cascade delete will handle messages and context
        self.db.delete(conversation)
        self.db.commit()
    
    def _get_contexts_for_message(self, message_id: UUID) -> List[ConversationContextResponse]:
        """Get context accesses for a specific message"""
        contexts = self.db.query(ConversationContext).filter(
            ConversationContext.message_id == message_id
        ).all()
        
        return [
            ConversationContextResponse(
                context_id=ctx.context_id,
                conversation_id=ctx.conversation_id,
                message_id=ctx.message_id,
                context_type=ctx.context_type,
                entity_id=ctx.entity_id,
                entity_table=ctx.entity_table,
                access_reason=ctx.access_reason,
                data_summary=ctx.data_summary,
                accessed_at=ctx.accessed_at
            )
            for ctx in contexts
        ]