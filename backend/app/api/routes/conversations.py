from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.search import Search
from app.models.user import User
from app.schemas.conversation import ConversationCreate, ConversationOut, ConversationUpdate, MessageCreate, MessageOut
from app.schemas.search import SearchOut

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

DEFAULT_TITLE = "Nueva conversación"
AUTO_TITLE_MAX_LENGTH = 60


def _get_owned_conversation(conversation_id: int, user: User, db: Session) -> Conversation:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None or conversation.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada")
    return conversation


@router.post("", response_model=ConversationOut)
def create_conversation(
    payload: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Conversation:
    conversation = Conversation(user_id=current_user.id, title=payload.title or DEFAULT_TITLE)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("", response_model=list[ConversationOut])
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Conversation]:
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )


@router.get("/{conversation_id}", response_model=ConversationOut)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Conversation:
    return _get_owned_conversation(conversation_id, current_user, db)


@router.patch("/{conversation_id}", response_model=ConversationOut)
def rename_conversation(
    conversation_id: int,
    payload: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Conversation:
    conversation = _get_owned_conversation(conversation_id, current_user, db)
    conversation.title = payload.title.strip() or DEFAULT_TITLE
    db.commit()
    db.refresh(conversation)
    return conversation


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    conversation = _get_owned_conversation(conversation_id, current_user, db)
    db.delete(conversation)
    db.commit()
    return {"ok": True}


@router.post("/{conversation_id}/messages", response_model=MessageOut)
def create_message(
    conversation_id: int,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Message:
    conversation = _get_owned_conversation(conversation_id, current_user, db)
    message = Message(conversation_id=conversation_id, role="user", content=payload.content)
    db.add(message)

    if conversation.title == DEFAULT_TITLE:
        title = payload.content.strip().replace("\n", " ")
        if len(title) > AUTO_TITLE_MAX_LENGTH:
            title = title[:AUTO_TITLE_MAX_LENGTH].rstrip() + "…"
        conversation.title = title or DEFAULT_TITLE

    db.commit()
    db.refresh(message)
    return message


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
def list_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Message]:
    _get_owned_conversation(conversation_id, current_user, db)
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )


@router.get("/{conversation_id}/searches", response_model=list[SearchOut])
def list_conversation_searches(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Search]:
    _get_owned_conversation(conversation_id, current_user, db)
    return (
        db.query(Search)
        .filter(Search.conversation_id == conversation_id)
        .order_by(Search.created_at.asc())
        .all()
    )
