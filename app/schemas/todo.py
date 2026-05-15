from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import date, datetime
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


class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    priority: PriorityEnum = PriorityEnum.MEDIUM
    due_date: Optional[date] = None


class TodoCreate(TodoBase):
    tag_ids: Optional[List[str]] = []


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    priority: Optional[PriorityEnum] = None
    status: Optional[TodoStatus] = None
    due_date: Optional[date] = None
    tag_ids: Optional[List[str]] = None


class TagResponse(BaseModel):
    id: str
    name: str
    color: str

    model_config = {"from_attributes": True}


class SubTaskResponse(BaseModel):
    id: str
    title: str
    is_completed: bool
    todo_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TodoResponse(TodoBase):
    id: str
    status: TodoStatus
    user_id: str
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []
    subtasks_count: int = 0
    is_shared: Optional[bool] = False
    shared_by: Optional[str] = None
    permission: Optional[str] = None

    model_config = {"from_attributes": True}


class TodoListResponse(BaseModel):
    items: List[TodoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = {"from_attributes": True}


class TodoDetailResponse(TodoResponse):
    subtasks: List[SubTaskResponse] = []

    model_config = {"from_attributes": True}
