import uuid
from datetime import datetime
from sqlalchemy import Column, String, CHAR, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), nullable=False)
    color = Column(String(7), default="#3498db")  # Hex color code
    user_id = Column(
        CHAR(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="tags")
    todos = relationship("Todo", secondary="todo_tags", back_populates="tags")

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"
