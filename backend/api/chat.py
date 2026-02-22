from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models.chat import ChatSession, ChatMessage
from backend.models.schemas import ChatRequest, ChatResponse, ChatMessageResponse
from backend.agents.orchestrator import AgentOrchestrator
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])
orchestrator = AgentOrchestrator()


@router.post("", response_model=ChatResponse)
async def chat(data: ChatRequest, db: AsyncSession = Depends(get_db)):
    if data.session_id:
        session = await db.get(ChatSession, data.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        session = ChatSession(title=data.message[:50])
        db.add(session)
        await db.commit()
        await db.refresh(session)

    user_msg = ChatMessage(
        session_id=session.id,
        sender="user",
        text=data.message,
    )
    db.add(user_msg)
    await db.commit()
    await db.refresh(user_msg)

    history_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at)
    )
    history = [
        {"sender": msg.sender, "text": msg.text}
        for msg in history_result.scalars().all()
    ]

    try:
        result = await orchestrator.process(data.message, history, db)
        agent_text = result["response"]
        active_agent = result.get("agent", "unknown")
        logger.info(f"[CHAT] Response from: {active_agent}")
    except Exception as e:
        logger.error(f"[CHAT] Error: {e}", exc_info=True)
        agent_text = f"I'm sorry, I encountered an error processing your request. Please try again."

    agent_msg = ChatMessage(
        session_id=session.id,
        sender="agent",
        text=agent_text,
    )
    db.add(agent_msg)
    await db.commit()
    await db.refresh(agent_msg)

    return ChatResponse(
        session_id=session.id,
        message=ChatMessageResponse(
            id=user_msg.id, sender=user_msg.sender, text=user_msg.text,
            timestamp=user_msg.created_at.strftime("%I:%M %p") if user_msg.created_at else "",
        ),
        agent_response=ChatMessageResponse(
            id=agent_msg.id, sender=agent_msg.sender, text=agent_msg.text,
            timestamp=agent_msg.created_at.strftime("%I:%M %p") if agent_msg.created_at else "",
        ),
    )


@router.get("/sessions")
async def get_sessions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatSession).order_by(ChatSession.created_at.desc())
    )
    sessions = result.scalars().all()
    return [
        {"id": s.id, "title": s.title, "created_at": str(s.created_at)}
        for s in sessions
    ]


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
async def get_session_messages(session_id: int, db: AsyncSession = Depends(get_db)):
    session = await db.get(ChatSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    return [
        ChatMessageResponse(
            id=msg.id, sender=msg.sender, text=msg.text,
            timestamp=msg.created_at.strftime("%I:%M %p") if msg.created_at else "",
        )
        for msg in messages
    ]
