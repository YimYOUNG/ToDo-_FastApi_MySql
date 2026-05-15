from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from app.database import get_db
from app.schemas.todo import (
    TodoCreate, TodoUpdate, TodoResponse,
    TodoListResponse, TodoDetailResponse, PriorityEnum, TodoStatus
)
from app.schemas.subtask import SubTaskCreate, SubTaskUpdate, SubTaskResponse
from app.services.todo_service import TodoService, SubTaskService
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/api/todos", tags=["Todos"])


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    todo = await TodoService.create_todo(db, current_user.id, todo_data)
    return todo


@router.get("", response_model=TodoListResponse)
async def get_todos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tag_id: Optional[str] = None,
    search: Optional[str] = None,
    due_from: Optional[date] = None,
    due_to: Optional[date] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await TodoService.get_todos(
        db, current_user.id, page, page_size,
        status, priority, tag_id, search, due_from, due_to, sort_by, sort_order
    )
    return result


@router.get("/{todo_id}", response_model=TodoDetailResponse)
async def get_todo(
    todo_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        todo = await TodoService.get_todo_by_id(db, todo_id, current_user.id)
        return todo
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "forbidden" in str(e).lower() or "access" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: str,
    update_data: TodoUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        todo = await TodoService.update_todo(db, todo_id, current_user.id, update_data)
        return todo
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "forbidden" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        await TodoService.delete_todo(db, todo_id, current_user.id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "forbidden" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{todo_id}/toggle", response_model=TodoResponse)
async def toggle_todo(
    todo_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        todo = await TodoService.toggle_todo_status(db, todo_id, current_user.id)
        return todo
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Subtask endpoints
@router.post("/{todo_id}/subtasks", response_model=SubTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_subtask(
    todo_id: str,
    subtask_data: SubTaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        subtask = await SubTaskService.create_subtask(db, todo_id, current_user.id, subtask_data.title)
        return subtask
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/subtasks/{subtask_id}", response_model=SubTaskResponse)
async def update_subtask(
    subtask_id: str,
    update_data: SubTaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        subtask = await SubTaskService.update_subtask(
            db, subtask_id, current_user.id,
            **update_data.model_dump(exclude_unset=True)
        )
        return subtask
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/subtasks/{subtask_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subtask(
    subtask_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        await SubTaskService.delete_subtask(db, subtask_id, current_user.id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/subtasks/{subtask_id}/toggle", response_model=SubTaskResponse)
async def toggle_subtask(
    subtask_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        subtask = await SubTaskService.toggle_subtask(db, subtask_id, current_user.id)
        return subtask
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
