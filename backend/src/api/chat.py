"""
Chat API Endpoint

Handles chatbot conversations with stateless architecture (FR-004, FR-030).
Loads history, executes agent, persists messages (FR-022, FR-024, FR-109).
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.schemas.chat import ChatRequest, ChatResponse, ToolCall
from src.services.conversation_service import ConversationService
from src.models.user import User
from src.agent.runner import run_agent
from src.api.auth import require_auth, SessionUser

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/{user_id}", response_model=ChatResponse)
async def chat(
    user_id: UUID,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: SessionUser = Depends(require_auth)
) -> ChatResponse:
    """
    Process a chat message and return AI response.

    Stateless request lifecycle (FR-021, FR-022):
    1. Validate user_id matches authenticated user
    2. Load or create conversation
    3. Load last 100 messages (FR-022b)
    4. Persist user message
    5. Execute agent with MCP tools
    6. Persist assistant response
    7. Return response

    Args:
        user_id: User UUID from path
        request: Chat request with message
        db: Database session
        current_user: Authenticated user

    Returns:
        ChatResponse with AI response and conversation ID

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 500 if agent execution fails
    """
    # Validate user_id matches authenticated user (FR-030)
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another user's conversation"
        )

    # Get or create conversation (FR-022a)
    conversation = await ConversationService.get_or_create_conversation(
        session=db,
        user_id=current_user.id
    )

    # Load conversation history (last 100 messages) (FR-022b, FR-107)
    history = await ConversationService.load_conversation_history(
        session=db,
        conversation_id=conversation.id,
        limit=100
    )

    # Persist user message (FR-109)
    user_message = await ConversationService.add_message(
        session=db,
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )

    # Execute agent with MCP tools (FR-016, FR-017, FR-018, FR-019, FR-020)
    try:
        agent_response, tool_calls_made = await run_agent(
            user_id=current_user.id,
            user_message=request.message,
            conversation_history=history
        )
    except Exception as e:
        # Log the error for debugging but return user-friendly message
        print(f"Agent execution error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="I encountered an error processing your request. Please try again."
        )

    # Persist assistant response (FR-024)
    tool_calls_metadata = [call.model_dump() for call in tool_calls_made]
    assistant_message = await ConversationService.add_message(
        session=db,
        conversation_id=conversation.id,
        role="assistant",
        content=agent_response,
        tool_metadata={"tool_calls": tool_calls_metadata}
    )

    # Return response
    return ChatResponse(
        response=agent_response,
        conversation_id=conversation.id,
        tool_calls=tool_calls_made
    )
