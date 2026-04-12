from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Conversation, Message
from backend.schemas import ConversationOut, MessageOut

router = APIRouter(prefix="/conversations", tags=["conversations"])

"""
列出所有對話（含標題、訊息數）
"""
@router.get("", response_model=list[ConversationOut])
def list_conversations(db: Session = Depends(get_db)):
    convs = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
    result = []
    for c in convs:
        msg_count = db.query(Message).filter(Message.conversation_id == c.id).count()
        result.append(
            ConversationOut(
                id=c.id,
                title=c.title,
                message_count=msg_count,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )
    return result

"""
取得某對話的所有訊息
"""
@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
def get_messages(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="對話不存在")
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )

"""
刪除對話（cascade 刪除所有訊息）
"""
@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="對話不存在")
    db.delete(conv)
    db.commit()
    return {"deleted": conversation_id}
