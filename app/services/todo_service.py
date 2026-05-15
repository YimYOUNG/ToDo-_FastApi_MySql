from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, true
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import date

from app.models.todo import Todo, SubTask, TodoTag, PriorityEnum, TodoStatus, TodoShare
from app.models.user import User
from app.models.tag import Tag
from app.schemas.todo import TodoCreate, TodoUpdate
from app.core.exceptions import NotFoundError, ForbiddenError


class TodoService:
    @staticmethod
    async def create_todo(
        db: AsyncSession,
        user_id: str,
        todo_data: TodoCreate
    ) -> Todo:
        todo = Todo(
            title=todo_data.title,
            description=todo_data.description,
            priority=todo_data.priority.value if isinstance(todo_data.priority, PriorityEnum) else todo_data.priority,
            due_date=todo_data.due_date,
            user_id=user_id,
        )
        db.add(todo)
        await db.flush()

        if todo_data.tag_ids:
            for tag_id in todo_data.tag_ids:
                result = await db.execute(
                    select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
                )
                tag = result.scalar_one_or_none()
                if tag:
                    db.add(TodoTag(todo_id=todo.id, tag_id=tag.id))

        await db.commit()
        result = await db.execute(
            select(Todo).options(selectinload(Todo.tags)).where(Todo.id == todo.id)
        )
        todo = result.scalar_one()
        return todo

    @staticmethod
    async def get_todos(
        db: AsyncSession,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tag_id: Optional[str] = None,
        search: Optional[str] = None,
        due_from: Optional[date] = None,
        due_to: Optional[date] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ):
        query = select(Todo).options(selectinload(Todo.tags)).where(Todo.user_id == user_id)

        count_query = select(func.count()).select_from(Todo).where(Todo.user_id == user_id)

        filters = []
        count_filters = []

        if status:
            try:
                status_enum = TodoStatus(status)
                filters.append(Todo.status == status_enum)
                count_filters.append(Todo.status == status_enum)
            except ValueError:
                pass

        if priority:
            try:
                priority_enum = PriorityEnum(priority)
                filters.append(Todo.priority == priority_enum)
                count_filters.append(Todo.priority == priority_enum)
            except ValueError:
                pass

        if tag_id:
            subq = select(TodoTag.todo_id).where(TodoTag.tag_id == tag_id)
            filters.append(Todo.id.in_(subq))
            count_filters.append(Todo.id.in_(subq))

        if search:
            search_filter = or_(
                Todo.title.ilike(f"%{search}%"),
                Todo.description.ilike(f"%{search}%")
            )
            filters.append(search_filter)
            count_filters.append(search_filter)

        if due_from:
            filters.append(Todo.due_date >= due_from)
            count_filters.append(Todo.due_date >= due_from)

        if due_to:
            filters.append(Todo.due_date <= due_to)
            count_filters.append(Todo.due_date <= due_to)

        for f in filters:
            query = query.where(f)
        for f in count_filters:
            count_query = count_query.where(f)

        valid_sort_fields = ["created_at", "updated_at", "due_date", "title", "priority"]
        if sort_by not in valid_sort_fields:
            sort_by = "created_at"

        sort_column = getattr(Todo, sort_by)
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await db.execute(query)
        own_todos = result.scalars().all()

        shared_todos = []
        readonly_todos = []
        try:
            shared_todo_ids = [t.id for t in own_todos]

            base_shared_conditions = [
                TodoShare.shared_with_id == user_id,
                TodoShare.permission == 'write',
            ]
            if shared_todo_ids:
                base_shared_conditions.append(~Todo.id.in_(shared_todo_ids))

            shared_query = (
                select(Todo)
                .options(selectinload(Todo.tags))
                .join(TodoShare, Todo.id == TodoShare.todo_id)
                .where(and_(*base_shared_conditions))
            )

            if status:
                try:
                    shared_query = shared_query.where(Todo.status == TodoStatus(status))
                except ValueError:
                    pass

            if priority:
                try:
                    shared_query = shared_query.where(Todo.priority == PriorityEnum(priority))
                except ValueError:
                    pass

            if search:
                shared_search_filter = or_(
                    Todo.title.ilike(f"%{search}%"),
                    Todo.description.ilike(f"%{search}%")
                )
                shared_query = shared_query.where(shared_search_filter)

            if sort_order.lower() == "asc":
                shared_query = shared_query.order_by(sort_column.asc())
            else:
                shared_query = shared_query.order_by(sort_column.desc())

            shared_result = await db.execute(shared_query)
            shared_todos = list(shared_result.scalars().all())

            all_shared_ids = shared_todo_ids + [t.id for t in shared_todos]

            readonly_base_conditions = [
                TodoShare.shared_with_id == user_id,
                TodoShare.permission == 'read',
            ]
            if all_shared_ids:
                readonly_base_conditions.append(~Todo.id.in_(all_shared_ids))

            readonly_query = (
                select(Todo)
                .options(selectinload(Todo.tags))
                .join(TodoShare, Todo.id == TodoShare.todo_id)
                .where(and_(*readonly_base_conditions))
            )

            if status:
                try:
                    readonly_query = readonly_query.where(Todo.status == TodoStatus(status))
                except ValueError:
                    pass

            if priority:
                try:
                    readonly_query = readonly_query.where(Todo.priority == PriorityEnum(priority))
                except ValueError:
                    pass

            if search:
                readonly_search_filter = or_(
                    Todo.title.ilike(f"%{search}%"),
                    Todo.description.ilike(f"%{search}%")
                )
                readonly_query = readonly_query.where(readonly_search_filter)

            if sort_order.lower() == "asc":
                readonly_query = readonly_query.order_by(sort_column.asc())
            else:
                readonly_query = readonly_query.order_by(sort_column.desc())

            readonly_result = await db.execute(readonly_query)
            readonly_todos = list(readonly_result.scalars().all())

        except Exception as e:
            print(f"[WARNING] 加载共享待办失败: {e}")
            shared_todos = []
            readonly_todos = []

        all_todos = []
        for todo in own_todos:
            all_todos.append({
                "id": todo.id,
                "user_id": todo.user_id,
                "title": todo.title,
                "description": todo.description,
                "priority": todo.priority.value if hasattr(todo.priority, 'value') else str(todo.priority),
                "status": todo.status.value if hasattr(todo.status, 'value') else str(todo.status),
                "due_date": todo.due_date.isoformat() if todo.due_date else None,
                "created_at": todo.created_at.isoformat() if todo.created_at else None,
                "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
                "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in (todo.tags or [])],
                "is_shared": False,
                "shared_by": None,
                "permission": None
            })

        for todo in shared_todos:
            sharer_name = '未知'
            try:
                share_result = await db.execute(
                    select(User)
                    .where(User.id == TodoShare.shared_by_id)
                    .select_from(TodoShare)
                    .where(TodoShare.todo_id == todo.id, TodoShare.shared_with_id == user_id)
                    .limit(1)
                )
                sharer = share_result.scalar_one_or_none()
                if sharer:
                    sharer_name = sharer.username
            except Exception:
                pass

            all_todos.append({
                "id": todo.id,
                "user_id": todo.user_id,
                "title": f"[共享] {todo.title}",
                "description": todo.description,
                "priority": todo.priority.value if hasattr(todo.priority, 'value') else str(todo.priority),
                "status": todo.status.value if hasattr(todo.status, 'value') else str(todo.status),
                "due_date": todo.due_date.isoformat() if todo.due_date else None,
                "created_at": todo.created_at.isoformat() if todo.created_at else None,
                "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
                "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in (todo.tags or [])],
                "is_shared": True,
                "shared_by": sharer_name,
                "permission": "write"
            })

        for todo in readonly_todos:
            sharer_name = '未知'
            try:
                share_result = await db.execute(
                    select(User)
                    .where(User.id == TodoShare.shared_by_id)
                    .select_from(TodoShare)
                    .where(TodoShare.todo_id == todo.id, TodoShare.shared_with_id == user_id)
                    .limit(1)
                )
                sharer = share_result.scalar_one_or_none()
                if sharer:
                    sharer_name = sharer.username
            except Exception:
                pass

            all_todos.append({
                "id": todo.id,
                "user_id": todo.user_id,
                "title": f"[只读] {todo.title}",
                "description": todo.description,
                "priority": todo.priority.value if hasattr(todo.priority, 'value') else str(todo.priority),
                "status": todo.status.value if hasattr(todo.status, 'value') else str(todo.status),
                "due_date": todo.due_date.isoformat() if todo.due_date else None,
                "created_at": todo.created_at.isoformat() if todo.created_at else None,
                "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
                "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in (todo.tags or [])],
                "is_shared": True,
                "shared_by": sharer_name,
                "permission": "read"
            })

        all_todos.sort(
            key=lambda x: x.get(sort_by, '') or '',
            reverse=(sort_order.lower() != 'asc')
        )

        paginated_items = all_todos[offset:offset + page_size]
        actual_total = len(all_todos)
        total_pages = (actual_total + page_size - 1) // page_size if actual_total > 0 else 0

        return {
            "items": paginated_items,
            "total": actual_total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    @staticmethod
    async def get_todo_by_id(db: AsyncSession, todo_id: str, user_id: str) -> Todo:
        result = await db.execute(
            select(Todo)
            .options(
                selectinload(Todo.tags),
                selectinload(Todo.subtasks),
            )
            .where(Todo.id == todo_id)
        )
        todo = result.scalar_one_or_none()

        if not todo:
            raise NotFoundError("Todo")

        if todo.user_id != user_id:
            share_result = await db.execute(
                select(TodoShare).where(
                    TodoShare.todo_id == todo_id,
                    TodoShare.shared_with_id == user_id
                )
            )
            if not share_result.scalar_one_or_none():
                raise ForbiddenError("You do not have access to this todo")

        return todo

    @staticmethod
    async def _check_write_permission(db: AsyncSession, todo: Todo, user_id: str):
        if todo.user_id == user_id:
            return True
        
        share_result = await db.execute(
            select(TodoShare).where(
                TodoShare.todo_id == todo.id,
                TodoShare.shared_with_id == user_id,
                TodoShare.permission == 'write'
            )
        )
        share = share_result.scalar_one_or_none()
        if share:
            return True
        
        raise ForbiddenError("You do not have write permission for this shared todo")

    @staticmethod
    async def update_todo(
        db: AsyncSession,
        todo_id: str,
        user_id: str,
        update_data: TodoUpdate
    ) -> Todo:
        todo = await TodoService.get_todo_by_id(db, todo_id, user_id)

        await TodoService._check_write_permission(db, todo, user_id)

        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if field != "tag_ids" and value is not None:
                setattr(todo, field, value.value if hasattr(value, 'value') else value)

        if "tag_ids" in update_dict and update_data.tag_ids is not None:
            todo.tags.clear()
            if update_data.tag_ids:
                for tag_id in update_data.tag_ids:
                    result = await db.execute(
                        select(Tag).where(Tag.id == tag_id)
                    )
                    tag = result.scalar_one_or_none()
                    if tag:
                        todo.tags.append(tag)

        await db.commit()
        result = await db.execute(
            select(Todo).options(selectinload(Todo.tags), selectinload(Todo.subtasks)).where(Todo.id == todo.id)
        )
        return result.scalar_one()

    @staticmethod
    async def delete_todo(db: AsyncSession, todo_id: str, user_id: str) -> bool:
        todo = await TodoService.get_todo_by_id(db, todo_id, user_id)

        if todo.user_id != user_id:
            raise ForbiddenError("Only owner can delete this todo")

        await db.delete(todo)
        await db.commit()
        return True

    @staticmethod
    async def toggle_todo_status(db: AsyncSession, todo_id: str, user_id: str) -> Todo:
        todo = await TodoService.get_todo_by_id(db, todo_id, user_id)

        await TodoService._check_write_permission(db, todo, user_id)

        if todo.status == TodoStatus.COMPLETED:
            todo.status = TodoStatus.PENDING
        else:
            todo.status = TodoStatus.COMPLETED

        await db.commit()
        result = await db.execute(
            select(Todo).options(selectinload(Todo.tags), selectinload(Todo.subtasks)).where(Todo.id == todo.id)
        )
        return result.scalar_one()


class SubTaskService:
    @staticmethod
    async def create_subtask(
        db: AsyncSession,
        todo_id: str,
        user_id: str,
        title: str
    ) -> SubTask:
        from app.services.todo_service import TodoService
        await TodoService.get_todo_by_id(db, todo_id, user_id)

        subtask = SubTask(title=title, todo_id=todo_id)
        db.add(subtask)
        await db.commit()
        await db.refresh(subtask)
        return subtask

    @staticmethod
    async def get_subtask_by_id(db: AsyncSession, subtask_id: str, user_id: str) -> SubTask:
        result = await db.execute(
            select(SubTask)
            .join(Todo)
            .where(SubTask.id == subtask_id, Todo.user_id == user_id)
        )
        subtask = result.scalar_one_or_none()

        if not subtask:
            raise NotFoundError("SubTask")

        return subtask

    @staticmethod
    async def update_subtask(
        db: AsyncSession,
        subtask_id: str,
        user_id: str,
        **kwargs
    ) -> SubTask:
        subtask = await SubTaskService.get_subtask_by_id(db, subtask_id, user_id)

        for key, value in kwargs.items():
            if value is not None and hasattr(subtask, key):
                setattr(subtask, key, value)

        await db.commit()
        await db.refresh(subtask)
        return subtask

    @staticmethod
    async def delete_subtask(db: AsyncSession, subtask_id: str, user_id: str) -> bool:
        subtask = await SubTaskService.get_subtask_by_id(db, subtask_id, user_id)
        await db.delete(subtask)
        await db.commit()
        return True

    @staticmethod
    async def toggle_subtask(db: AsyncSession, subtask_id: str, user_id: str) -> SubTask:
        subtask = await SubTaskService.get_subtask_by_id(db, subtask_id, user_id)
        subtask.is_completed = not subtask.is_completed
        await db.commit()
        await db.refresh(subtask)
        return subtask
