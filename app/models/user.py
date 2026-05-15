import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    todos = relationship("Todo", back_populates="owner", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="owner", cascade="all, delete-orphan")
    shared_todos_received = relationship(
        "TodoShare",
        foreign_keys="TodoShare.shared_with_id",
        back_populates="shared_with_user"
    )
    shared_todos_sent = relationship(
        "TodoShare",
        foreign_keys="TodoShare.shared_by_id",
        back_populates="shared_by_user"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
