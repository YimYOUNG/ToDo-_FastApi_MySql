from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SubTaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class SubTaskCreate(SubTaskBase):
    pass


class SubTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    is_completed: Optional[bool] = None


class SubTaskResponse(SubTaskBase):
    id: str
    is_completed: bool
    todo_id: str
    created_at: datetime

    class Config:
        from_attributes = True
