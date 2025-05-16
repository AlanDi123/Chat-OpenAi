from typing import List, Dict
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Message
from app.config import settings

class MemoryService:
    def __init__(self, max_history: int):
        self.max_history = max_history

    def save(self, role: str, content: str):
        db: Session = SessionLocal()
        try:
            m = Message(role=role, content=content)
            db.add(m); db.commit()
        except:
            db.rollback(); raise
        finally:
            db.close()

    def load_context(self) -> List[Dict[str,str]]:
        db: Session = SessionLocal()
        try:
            msgs = db.query(Message)\
                     .order_by(Message.timestamp.desc())\
                     .limit(self.max_history)\
                     .all()
            msgs.reverse()
            return [{"role":m.role,"content":m.content} for m in msgs]
        finally:
            db.close()

memory = MemoryService(max_history=settings.MAX_HISTORY)
