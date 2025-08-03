from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from app.schemas.chat import (
    ConversationCreate,
    ConversationResponse,
    ConversationWithMessages,
    ConversationUpdate,
    SendMessageRequest,
    SendMessageResponse
)
from app.services.chat import ChatService
from app.core.security import get_current_user
from app.db.postgres import get_db
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new chat conversation.
    """
    chat_service = ChatService(db)
    return await chat_service.create_conversation(
        user_id=UUID(current_user),
        conversation_data=conversation_data
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all conversations for the current user.
    """
    chat_service = ChatService(db)
    return await chat_service.list_conversations(user_id=UUID(current_user))


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: UUID,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific conversation with all its messages.
    """
    chat_service = ChatService(db)
    return await chat_service.get_conversation_with_messages(
        conversation_id=conversation_id,
        user_id=UUID(current_user)
    )


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: UUID,
    update_data: ConversationUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a conversation (e.g., change title or archive it).
    """
    chat_service = ChatService(db)
    return await chat_service.update_conversation(
        conversation_id=conversation_id,
        user_id=UUID(current_user),
        update_data=update_data
    )


@router.post("/conversations/{conversation_id}/messages", response_model=SendMessageResponse)
async def send_message(
    conversation_id: UUID,
    message_data: SendMessageRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to a conversation and get AI response.
    """
    chat_service = ChatService(db)
    return await chat_service.send_message(
        conversation_id=conversation_id,
        user_id=UUID(current_user),
        message_content=message_data.content
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a conversation and all its messages.
    """
    chat_service = ChatService(db)
    await chat_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=UUID(current_user)
    )
    return None