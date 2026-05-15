from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from sqlalchemy.orm import selectinload
from datetime import date, datetime
from typing import Optional

from app.database import get_db
from app.models.todo import Todo, TodoStatus, TodoShare
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/api/calendar", tags=["Calendar"])


@router.get("/{year}/{month}")
async def get_calendar_data(
    year: int,
    month: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    if month < 1 or month > 12:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")

    if year < 1900 or year > 2100:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Year must be between 1900 and 2100")

    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year + (month // 12), (month % 12) + 1, 1)

    own_result = await db.execute(
        select(Todo)
        .options(selectinload(Todo.tags))
        .where(
            Todo.user_id == current_user.id,
            Todo.due_date >= start_date,
            Todo.due_date < end_date
        )
        .order_by(Todo.due_date, Todo.priority)
    )
    own_todos = list(own_result.scalars().all())

    try:
        shared_result = await db.execute(
            select(Todo)
            .options(selectinload(Todo.tags))
            .join(TodoShare, Todo.id == TodoShare.todo_id)
            .where(
                TodoShare.shared_with_id == current_user.id,
                Todo.due_date >= start_date,
                Todo.due_date < end_date
            )
            .order_by(Todo.due_date, Todo.priority)
        )
        shared_todos_list = list(shared_result.scalars().all())
    except Exception as e:
        print(f"[WARNING] 日历加载共享待办失败: {e}")
        shared_todos_list = []

    all_todos = []
    seen_ids = set()

    for todo in own_todos:
        if todo.id not in seen_ids:
            seen_ids.add(todo.id)
            all_todos.append((todo, False))

    for todo in shared_todos_list:
        if todo.id not in seen_ids:
            seen_ids.add(todo.id)
            all_todos.append((todo, True))

    calendar_data = {}
    for todo, is_shared in all_todos:
        due_str = str(todo.due_date) if todo.due_date else None
        if due_str:
            if due_str not in calendar_data:
                calendar_data[due_str] = []

            prefix = "[共享] " if is_shared else ""
            calendar_data[due_str].append({
                "id": todo.id,
                "title": f"{prefix}{todo.title}",
                "priority": todo.priority.value if hasattr(todo.priority, "value") else str(todo.priority),
                "status": todo.status.value if hasattr(todo.status, "value") else str(todo.status),
                "is_shared": is_shared,
            })

    import calendar as cal_module
    first_weekday, days_in_month = cal_module.monthrange(year, month)

    return {
        "year": year,
        "month": month,
        "days_in_month": days_in_month,
        "first_weekday": first_weekday,
        "todos": calendar_data,
        "today": str(date.today()),
    }
