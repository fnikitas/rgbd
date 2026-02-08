import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String

from app.db.base import Base
from app.db.types import GUID


class Theme(Base):
    """Модель темы задач."""
    __tablename__ = "themes"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Theme {self.name}>"
