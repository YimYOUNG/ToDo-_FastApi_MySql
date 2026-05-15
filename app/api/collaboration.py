from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.todo import Todo, TodoShare
from app.models.user import User
from app.core.dependencies import get_current_active_user

router = APIRouter(prefix="/api/collaboration", tags=["Collaboration"])


class ShareRequest(BaseModel):
    username: str
    permission: str = "read"


class ShareResponse(BaseModel):
    id: str
    todo_id: str
    shared_with_username: str
    permission: str
    created_at: str


@router.post("/{todo_id}/share", response_model=ShareResponse, status_code=status.HTTP_201_CREATED)
async def share_todo(
    todo_id: str,
    share_data: ShareRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id))
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    user_result = await db.execute(
        select(User).where(User.username == share_data.username)
    )
    target_user = user_result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if target_user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot share with yourself")

    existing = await db.execute(
        select(TodoShare).where(
            TodoShare.todo_id == todo_id,
            TodoShare.shared_with_id == target_user.id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already shared with this user")

    share = TodoShare(
        todo_id=todo_id,
        shared_with_id=target_user.id,
        shared_by_id=current_user.id,
        permission=share_data.permission
    )
    db.add(share)
    await db.commit()
    await db.refresh(share)

    return ShareResponse(
        id=share.id,
        todo_id=share.todo_id,
        shared_with_username=target_user.username,
        permission=share.permission,
        created_at=str(share.created_at) if share.created_at else ""
    )


@router.get("/shared")
async def get_shared_todos(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TodoShare)
        .options(
            selectinload(TodoShare.shared_by_user),
            selectinload(TodoShare.todo)
        )
        .join(Todo)
        .where(TodoShare.shared_with_id == current_user.id)
    )
    shares = result.scalars().all()

    return [
        {
            "id": s.id,
            "todo_id": s.todo_id,
            "todo_title": s.todo.title if s.todo else '未知',
            "shared_by": s.shared_by_user.username if s.shared_by_user else '未知',
            "permission": s.permission,
        }
        for s in shares
    ]


@router.get("/shared-by-me")
async def get_my_shared_todos(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TodoShare)
        .options(selectinload(TodoShare.shared_with_user), selectinload(TodoShare.todo))
        .where(TodoShare.shared_by_id == current_user.id)
    )
    shares = result.scalars().all()

    return [
        {
            "id": s.id,
            "todo_id": s.todo_id,
            "todo_title": getattr(s.todo, 'title', '未知') if hasattr(s, 'todo') else '未知',
            "shared_with": s.shared_with_user.username if hasattr(s, 'shared_with_user') else '未知',
            "permission": s.permission,
        }
        for s in shares
    ]


@router.delete("/{todo_id}/unshare/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unshare_todo(
    todo_id: str,
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TodoShare).where(
            TodoShare.todo_id == todo_id,
            TodoShare.shared_with_id == user_id,
            TodoShare.shared_by_id == current_user.id
        )
    )
    share = result.scalar_one_or_none()

    if not share:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share record not found")

    await db.delete(share)
    await db.commit()
