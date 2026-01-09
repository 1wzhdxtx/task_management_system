"""
分类服务
处理任务分类相关业务逻辑
"""
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    """
    分类服务

    处理分类的 CRUD 操作
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.category_repo = CategoryRepository(db)

    async def create_category(
        self,
        user_id: int,
        category_in: CategoryCreate,
    ) -> Category:
        """
        创建分类

        Args:
            user_id: 用户 ID
            category_in: 分类数据

        Returns:
            创建的分类

        Raises:
            BadRequestException: 分类名称已存在
        """
        # 检查名称是否重复
        if await self.category_repo.name_exists(user_id, category_in.name):
            raise BadRequestException(
                f"Category '{category_in.name}' already exists"
            )

        category_data = category_in.model_dump()
        category_data["user_id"] = user_id

        return await self.category_repo.create(category_data)

    async def get_category(
        self,
        category_id: int,
        user_id: int,
    ) -> Category:
        """
        获取分类详情

        Args:
            category_id: 分类 ID
            user_id: 用户 ID

        Returns:
            分类对象

        Raises:
            NotFoundException: 分类不存在
            ForbiddenException: 无权访问
        """
        category = await self.category_repo.get_by_id(category_id)

        if not category:
            raise NotFoundException(f"Category with id {category_id} not found")

        if category.user_id != user_id:
            raise ForbiddenException(
                "You don't have permission to access this category"
            )

        return category

    async def get_user_categories(self, user_id: int) -> List[Category]:
        """
        获取用户的所有分类

        Args:
            user_id: 用户 ID

        Returns:
            分类列表
        """
        return await self.category_repo.get_user_categories(user_id)

    async def update_category(
        self,
        category_id: int,
        user_id: int,
        category_in: CategoryUpdate,
    ) -> Category:
        """
        更新分类

        Args:
            category_id: 分类 ID
            user_id: 用户 ID
            category_in: 更新数据

        Returns:
            更新后的分类
        """
        category = await self.get_category(category_id, user_id)

        # 检查名称是否冲突
        if category_in.name and category_in.name != category.name:
            if await self.category_repo.name_exists(user_id, category_in.name):
                raise BadRequestException(
                    f"Category '{category_in.name}' already exists"
                )

        update_data = category_in.model_dump(exclude_unset=True)
        return await self.category_repo.update(category, update_data)

    async def delete_category(
        self,
        category_id: int,
        user_id: int,
    ) -> bool:
        """
        删除分类

        Args:
            category_id: 分类 ID
            user_id: 用户 ID

        Returns:
            是否成功
        """
        await self.get_category(category_id, user_id)
        return await self.category_repo.delete(category_id)
