from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate
from app.core.exceptions import NotFoundError, DuplicateError


class TagService:
    @staticmethod
    async def create_tag(db: AsyncSession, user_id: str, tag_data: TagCreate) -> Tag:
        result = await db.execute(
            select(Tag).where(Tag.name == tag_data.name, Tag.user_id == user_id)
        )
        if result.scalar_one_or_none():
            raise DuplicateError("Tag name")

        tag = Tag(
            name=tag_data.name,
            color=tag_data.color,
            user_id=user_id,
        )
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
        return tag

    @staticmethod
    async def get_tags(db: AsyncSession, user_id: str) -> list[Tag]:
        result = await db.execute(
            select(Tag)
            .options(selectinload(Tag.todos))
            .where(Tag.user_id == user_id)
            .order_by(Tag.name)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_tag_by_id(db: AsyncSession, tag_id: str, user_id: str) -> Tag:
        result = await db.execute(
            select(Tag)
            .options(selectinload(Tag.todos))
            .where(Tag.id == tag_id, Tag.user_id == user_id)
        )
        tag = result.scalar_one_or_none()

        if not tag:
            raise NotFoundError("Tag")

        return tag

    @staticmethod
    async def update_tag(
        db: AsyncSession,
        tag_id: str,
        user_id: str,
        update_data: TagUpdate
    ) -> Tag:
        tag = await TagService.get_tag_by_id(db, tag_id, user_id)

        if update_data.name is not None:
            result = await db.execute(
                select(Tag).where(
                    Tag.name == update_data.name,
                    Tag.user_id == user_id,
                    Tag.id != tag_id
                )
            )
            if result.scalar_one_or_none():
                raise DuplicateError("Tag name")
            tag.name = update_data.name

        if update_data.color is not None:
            tag.color = update_data.color

        await db.commit()
        await db.refresh(tag)
        return tag

    @staticmethod
    async def delete_tag(db: AsyncSession, tag_id: str, user_id: str) -> bool:
        tag = await TagService.get_tag_by_id(db, tag_id, user_id)
        await db.delete(tag)
        await db.commit()
        return True
