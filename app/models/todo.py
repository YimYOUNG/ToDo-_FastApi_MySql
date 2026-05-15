import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, DateTime, Enum, ForeignKey,
    Date as SQLDate, Boolean
)
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class PriorityEnum(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TodoStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Todo(Base):
    __tablename__ = "todos"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.MEDIUM)
    status = Column(Enum(TodoStatus), default=TodoStatus.PENDING)
    due_date = Column(SQLDate, nullable=True)
    user_id = Column(
        CHAR(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="todos")
    subtasks = relationship(
        "SubTask",
        back_populates="todo",
        cascade="all, delete-orphan",
        order_by="SubTask.created_at"
    )
    tags = relationship("Tag", secondary="todo_tags", back_populates="todos")
    shares = relationship(
        "TodoShare",
        back_populates="todo",
        cascade="all, delete-orphan"
    )
    reminders = relationship(
        "Reminder",
        back_populates="todo",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Todo(id={self.id}, title={self.title}, status={self.status})>"


class SubTask(Base):
    __tablename__ = "subtasks"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    is_completed = Column(Boolean, default=False)
    todo_id = Column(
        CHAR(36),
        ForeignKey("todos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    todo = relationship("Todo", back_populates="subtasks")

    def __repr__(self):
        return f"<SubTask(id={self.id}, title={self.title})>"


class TodoTag(Base):
    __tablename__ = "todo_tags"

    todo_id = Column(
        CHAR(36),
        ForeignKey("todos.id", ondelete="CASCADE"),
        primary_key=True
    )
    tag_id = Column(
        CHAR(36),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True
    )


class TodoShare(Base):
    __tablename__ = "todo_shares"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    todo_id = Column(
        CHAR(36),
        ForeignKey("todos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    shared_with_id = Column(
        CHAR(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    shared_by_id = Column(
        CHAR(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    permission = Column(String(20), default="read")  # read or write
    created_at = Column(DateTime, default=datetime.utcnow)

    todo = relationship("Todo", back_populates="shares")
    shared_with_user = relationship(
        "User",
        foreign_keys=[shared_with_id],
        back_populates="shared_todos_received"
    )
    shared_by_user = relationship(
        "User",
        foreign_keys=[shared_by_id],
        back_populates="shared_todos_sent"
    )


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    todo_id = Column(
        CHAR(36),
        ForeignKey("todos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    remind_time = Column(DateTime, nullable=False)
    method = Column(String(20), default="browser")  # browser, email
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    todo = relationship("Todo", back_populates="reminders")
