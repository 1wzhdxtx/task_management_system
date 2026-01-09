"""
标签数据访问层
"""
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag
from app.repositories.base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    """
    标签 Repository

    继承基类 CRUD，扩展标签特定查询
    """

    def __init__(self, db: AsyncSession):
        super().__init__(Tag, db)

    async def get_user_tags(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Tag]:
        """
        获取用户的所有标签

        Args:
            user_id: 用户 ID
            skip: 跳过记录数
            limit: 返回记录数

        Returns:
            标签列表
        """
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=[Tag.user_id == user_id],
            order_by=Tag.name.asc(),
        )

    async def get_by_name(
        self,
        user_id: int,
        name: str,
    ) -> Optional[Tag]:
        """
        根据名称获取用户的标签

        Args:
            user_id: 用户 ID
            name: 标签名称

        Returns:
            标签对象或 None
        """
        query = select(Tag).where(
            and_(Tag.user_id == user_id, Tag.name == name)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_ids(
        self,
        user_id: int,
        tag_ids: List[int],
    ) -> List[Tag]:
        """
        根据 ID 列表获取标签（仅限用户自己的）

        Args:
            user_id: 用户 ID
            tag_ids: 标签 ID 列表

        Returns:
            标签列表
        """
        if not tag_ids:
            return []

        query = select(Tag).where(
            and_(Tag.user_id == user_id, Tag.id.in_(tag_ids))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def name_exists(self, user_id: int, name: str) -> bool:
        """
        检查标签名称是否已存在

        Args:
            user_id: 用户 ID
            name: 标签名称

        Returns:
            是否存在
        """
        tag = await self.get_by_name(user_id, name)
        return tag is not None
