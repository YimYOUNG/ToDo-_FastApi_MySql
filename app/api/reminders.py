from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

from app.database import get_db
from app.models.todo import Reminder, Todo
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/api/reminders", tags=["Reminders"])


class ReminderCreate(BaseModel):
    todo_id: str
    remind_time: datetime
    method: str = Field(default="browser", pattern="^(browser|email)$")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_reminder(
    data: ReminderCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Todo).where(Todo.id == data.todo_id))
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    if data.remind_time < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reminder time must be in the future")

    existing = await db.execute(
        select(Reminder).where(
            Reminder.todo_id == data.todo_id,
            Reminder.is_sent == False
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Active reminder already exists for this todo")

    reminder = Reminder(
        todo_id=data.todo_id,
        remind_time=data.remind_time,
        method=data.method,
    )
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)

    return {
        "id": reminder.id,
        "todo_id": reminder.todo_id,
        "remind_time": str(reminder.remind_time) if reminder.remind_time else "",
        "method": reminder.method,
        "is_sent": reminder.is_sent,
    }


@router.get("")
async def get_reminders(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Reminder)
        .join(Todo)
        .where(Todo.user_id == current_user.id)
        .order_by(Reminder.remind_time.desc())
    )
    reminders = result.scalars().all()

    return [
        {
            "id": r.id,
            "todo_id": r.todo_id,
            "remind_time": str(r.remind_time) if r.remind_time else "",
            "method": r.method,
            "is_sent": r.is_sent,
        }
        for r in reminders
    ]


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Reminder)
        .join(Todo)
        .where(Reminder.id == reminder_id, Todo.user_id == current_user.id)
    )
    reminder = result.scalar_one_or_none()

    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    await db.delete(reminder)
    await db.commit()
