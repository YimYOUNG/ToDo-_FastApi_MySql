from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, case, Date, cast, select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.todo import Todo, PriorityEnum, TodoStatus, TodoShare
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
    # 自己的待办
    own_total = await db.scalar(
        select(func.count()).select_from(Todo).where(Todo.user_id == current_user.id)
    ) or 0
    own_completed = await db.scalar(
        select(func.count()).select_from(Todo).where(
            Todo.user_id == current_user.id,
            Todo.status == TodoStatus.COMPLETED
        )
    ) or 0
    own_pending = await db.scalar(
        select(func.count()).select_from(Todo).where(
            Todo.user_id == current_user.id,
            Todo.status == TodoStatus.PENDING
        )
    ) or 0
    own_in_progress = await db.scalar(
        select(func.count()).select_from(Todo).where(
            Todo.user_id == current_user.id,
            Todo.status == TodoStatus.IN_PROGRESS
        )
    ) or 0
    own_overdue = await db.scalar(
        select(func.count()).select_from(Todo).where(
            Todo.user_id == current_user.id,
            Todo.due_date < func.curdate(),
            Todo.status != TodoStatus.COMPLETED
        )
    ) or 0

    # 共享待办
    shared_todos_subq = select(TodoShare.todo_id).where(
        TodoShare.shared_with_id == current_user.id
    ).subquery()
    shared_total = await db.scalar(
        select(func.count()).select_from(Todo).where(Todo.id.in_(select(shared_todos_subq)))
    ) or 0
    shared_completed = await db.scalar(
        select(func.count()).select_from(Todo).where(
            Todo.id.in_(select(shared_todos_subq)),
            Todo.status == TodoStatus.COMPLETED
        )
    ) or 0
    shared_pending = await db.scalar(
        select(func.count()).select_from(Todo).where(
            Todo.id.in_(select(shared_todos_subq)),
            Todo.status == TodoStatus.PENDING
        )
    ) or 0
    shared_in_progress = await db.scalar(
        select(func.count()).select_from(Todo).where(
            Todo.id.in_(select(shared_todos_subq)),
            Todo.status == TodoStatus.IN_PROGRESS
        )
    ) or 0
    shared_overdue = await db.scalar(
        select(func.count()).select_from(Todo).where(
            Todo.id.in_(select(shared_todos_subq)),
            Todo.due_date < func.curdate(),
            Todo.status != TodoStatus.COMPLETED
        )
    ) or 0

    total = own_total + shared_total
    completed = own_completed + shared_completed
    pending = own_pending + shared_pending
    in_progress = own_in_progress + shared_in_progress
    overdue = own_overdue + shared_overdue

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
    shared_todos_subq = select(TodoShare.todo_id).where(
        TodoShare.shared_with_id == current_user.id
    ).subquery()

    # 优先级的分布（自己 + 共享）
    priority_own = await db.execute(
        select(Todo.priority, func.count())
        .where(Todo.user_id == current_user.id)
        .group_by(Todo.priority)
    )
    priority_shared = await db.execute(
        select(Todo.priority, func.count())
        .where(Todo.id.in_(select(shared_todos_subq)))
        .group_by(Todo.priority)
    )

    priority_map = {}
    for row in priority_own.all():
        name = row[0].value if hasattr(row[0], 'value') else str(row[0])
        priority_map[name] = priority_map.get(name, 0) + row[1]
    for row in priority_shared.all():
        name = row[0].value if hasattr(row[0], 'value') else str(row[0])
        priority_map[name] = priority_map.get(name, 0) + row[1]

    by_priority = [DistributionItem(name=k, value=v) for k, v in sorted(priority_map.items())]

    # 状态的分布（自己 + 共享）
    status_own = await db.execute(
        select(Todo.status, func.count())
        .where(Todo.user_id == current_user.id)
        .group_by(Todo.status)
    )
    status_shared = await db.execute(
        select(Todo.status, func.count())
        .where(Todo.id.in_(select(shared_todos_subq)))
        .group_by(Todo.status)
    )

    status_map = {}
    for row in status_own.all():
        name = row[0].value if hasattr(row[0], 'value') else str(row[0])
        status_map[name] = status_map.get(name, 0) + row[1]
    for row in status_shared.all():
        name = row[0].value if hasattr(row[0], 'value') else str(row[0])
        status_map[name] = status_map.get(name, 0) + row[1]

    by_status = [DistributionItem(name=k, value=v) for k, v in sorted(status_map.items())]

    return DistributionStats(by_priority=by_priority, by_status=by_status)
