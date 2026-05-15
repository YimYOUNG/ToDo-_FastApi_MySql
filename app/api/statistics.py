from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, case, Date, cast, select

from app.database import get_db
from app.models.todo import Todo, PriorityEnum, TodoStatus
from app.schemas.todo import TodoStatus, PriorityEnum as SchemaPriorityEnum
from app.core.dependencies import get_current_active_user
from app.models.user import User
from pydantic import BaseModel
from typing import Optional
from datetime import date

router = APIRouter(prefix="/api/statistics", tags=["Statistics"])


class OverviewStats(BaseModel):
    total_todos: int
    completed_todos: int
    pending_todos: int
    in_progress_todos: int
    completion_rate: float
    overdue_todos: int


class DistributionItem(BaseModel):
    name: str
    value: int


class DistributionStats(BaseModel):
    by_priority: list[DistributionItem]
    by_status: list[DistributionItem]


@router.get("/overview", response_model=OverviewStats)
async def get_overview(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    total = await db.scalar(
        select(func.count()).select_from(Todo).where(Todo.user_id == current_user.id)
    ) or 0

    completed = await db.scalar(
        select(func.count()).select_from(Todo).where(
            Todo.user_id == current_user.id,
            Todo.status == TodoStatus.COMPLETED
        )
    ) or 0

    pending = await db.scalar(
        select(func.count()).select_from(Todo).where(
            Todo.user_id == current_user.id,
            Todo.status == TodoStatus.PENDING
        )
    ) or 0

    in_progress = await db.scalar(
        select(func.count()).select_from(Todo).where(
            Todo.user_id == current_user.id,
            Todo.status == TodoStatus.IN_PROGRESS
        )
    ) or 0

    overdue = await db.scalar(
        select(func.count()).select_from(Todo).where(
            Todo.user_id == current_user.id,
            Todo.due_date < func.curdate(),
            Todo.status != TodoStatus.COMPLETED
        )
    ) or 0

    completion_rate = round((completed / total * 100), 2) if total > 0 else 0.0

    return OverviewStats(
        total_todos=total,
        completed_todos=completed,
        pending_todos=pending,
        in_progress_todos=in_progress,
        completion_rate=completion_rate,
        overdue_todos=overdue,
    )


@router.get("/distribution", response_model=DistributionStats)
async def get_distribution(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    priority_result = await db.execute(
        select(Todo.priority, func.count())
        .where(Todo.user_id == current_user.id)
        .group_by(Todo.priority)
    )

    by_priority = [
        DistributionItem(name=row[0].value if hasattr(row[0], 'value') else str(row[0]), value=row[1])
        for row in priority_result.all()
    ]

    status_result = await db.execute(
        select(Todo.status, func.count())
        .where(Todo.user_id == current_user.id)
        .group_by(Todo.status)
    )

    by_status = [
        DistributionItem(name=row[0].value if hasattr(row[0], 'value') else str(row[0]), value=row[1])
        for row in status_result.all()
    ]

    return DistributionStats(by_priority=by_priority, by_status=by_status)
