from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import date
import json
import csv
import io

from app.database import get_db
from app.models.todo import Todo, TodoTag
from app.models.tag import Tag
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.get("/csv")
async def export_csv(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tag_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Todo).options(selectinload(Todo.tags)).where(Todo.user_id == current_user.id)

    filters = []
    if status:
        from app.models.todo import TodoStatus
        try:
            filters.append(Todo.status == TodoStatus(status))
        except ValueError:
            pass

    if priority:
        from app.models.todo import PriorityEnum
        try:
            filters.append(Todo.priority == PriorityEnum(priority))
        except ValueError:
            pass

    if tag_id:
        subq = select(TodoTag.todo_id).where(TodoTag.tag_id == tag_id)
        filters.append(Todo.id.in_(subq))

    for f in filters:
        query = query.where(f)

    result = await db.execute(query)
    todos = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["ID", "Title", "Description", "Priority", "Status", "Due Date", "Created At"])

    for todo in todos:
        tags = ", ".join([t.name for t in todo.tags]) if todo.tags else ""
        writer.writerow([
            todo.id,
            todo.title,
            todo.description or "",
            todo.priority.value if hasattr(todo.priority, 'value') else str(todo.priority),
            todo.status.value if hasattr(todo.status, 'value') else str(todo.status),
            str(todo.due_date) if todo.due_date else "",
            str(todo.created_at) if todo.created_at else "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=todos_export.csv"}
    )


@router.get("/json")
async def export_json(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tag_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Todo).options(selectinload(Todo.tags)).where(Todo.user_id == current_user.id)

    filters = []
    if status:
        from app.models.todo import TodoStatus
        try:
            filters.append(Todo.status == TodoStatus(status))
        except ValueError:
            pass

    if priority:
        from app.models.todo import PriorityEnum
        try:
            filters.append(Todo.priority == PriorityEnum(priority))
        except ValueError:
            pass

    if tag_id:
        subq = select(TodoTag.todo_id).where(TodoTag.tag_id == tag_id)
        filters.append(Todo.id.in_(subq))

    for f in filters:
        query = query.where(f)

    result = await db.execute(query)
    todos = result.scalars().all()

    data = [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "priority": t.priority.value if hasattr(t.priority, 'value') else str(t.priority),
            "status": t.status.value if hasattr(t.status, 'value') else str(t.status),
            "due_date": str(t.due_date) if t.due_date else None,
            "created_at": str(t.created_at) if t.created_at else None,
            "tags": [tag.name for tag in t.tags],
        }
        for t in todos
    ]

    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    return StreamingResponse(
        iter([json_str]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=todos_export.json"}
    )
