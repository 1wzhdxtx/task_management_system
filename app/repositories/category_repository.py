"""
分类数据访问层
"""
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """
    分类 Repository

    继承基类 CRUD，扩展分类特定查询
    """

    def __init__(self, db: AsyncSession):
        super().__init__(Category, db)

    async def get_user_categories(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Category]:
        """
        获取用户的所有分类

        Args:
            user_id: 用户 ID
            skip: 跳过记录数
            limit: 返回记录数

        Returns:
            分类列表
        """
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=[Category.user_id == user_id],
            order_by=Category.name.asc(),
        )

    async def get_by_name(
        self,
        user_id: int,
        name: str,
    ) -> Optional[Category]:
        """
        根据名称获取用户的分类

        Args:
            user_id: 用户 ID
            name: 分类名称

        Returns:
            分类对象或 None
        """
        query = select(Category).where(
            and_(Category.user_id == user_id, Category.name == name)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def name_exists(self, user_id: int, name: str) -> bool:
        """
        检查分类名称是否已存在

        Args:
            user_id: 用户 ID
            name: 分类名称

        Returns:
            是否存在
        """
        category = await self.get_by_name(user_id, name)
        return category is not None
