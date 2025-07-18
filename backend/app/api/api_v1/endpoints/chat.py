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
from app.services.google_auth import GoogleAuthService

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user = Depends(GoogleAuthService.get_current_user),
    chat_service: ChatService = Depends()
):
    """
    Create a new chat conversation.
    """
    return await chat_service.create_conversation(
        user_id=current_user.user_id,
        conversation_data=conversation_data
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    current_user = Depends(GoogleAuthService.get_current_user),
    chat_service: ChatService = Depends()
):
    """
    List all conversations for the current user.
    """
    return await chat_service.list_conversations(user_id=current_user.user_id)


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: UUID,
    current_user = Depends(GoogleAuthService.get_current_user),
    chat_service: ChatService = Depends()
):
    """
    Get a specific conversation with all its messages.
    """
    return await chat_service.get_conversation_with_messages(
        conversation_id=conversation_id,
        user_id=current_user.user_id
    )


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: UUID,
    update_data: ConversationUpdate,
    current_user = Depends(GoogleAuthService.get_current_user),
    chat_service: ChatService = Depends()
):
    """
    Update a conversation (e.g., change title or archive it).
    """
    return await chat_service.update_conversation(
        conversation_id=conversation_id,
        user_id=current_user.user_id,
        update_data=update_data
    )


@router.post("/conversations/{conversation_id}/messages", response_model=SendMessageResponse)
async def send_message(
    conversation_id: UUID,
    message_data: SendMessageRequest,
    current_user = Depends(GoogleAuthService.get_current_user),
    chat_service: ChatService = Depends()
):
    """
    Send a message to a conversation and get AI response.
    """
    return await chat_service.send_message(
        conversation_id=conversation_id,
        user_id=current_user.user_id,
        message_content=message_data.content
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    current_user = Depends(GoogleAuthService.get_current_user),
    chat_service: ChatService = Depends()
):
    """
    Delete a conversation and all its messages.
    """
    await chat_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.user_id
    )
    return None