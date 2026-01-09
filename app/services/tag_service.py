"""
标签服务
处理任务标签相关业务逻辑
"""
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.models.tag import Tag
from app.repositories.tag_repository import TagRepository
from app.schemas.tag import TagCreate, TagUpdate


class TagService:
    """
    标签服务

    处理标签的 CRUD 操作
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.tag_repo = TagRepository(db)

    async def create_tag(self, user_id: int, tag_in: TagCreate) -> Tag:
        """
        创建标签

        Args:
            user_id: 用户 ID
            tag_in: 标签数据

        Returns:
            创建的标签

        Raises:
            BadRequestException: 标签名称已存在
        """
        # 检查名称是否重复
        if await self.tag_repo.name_exists(user_id, tag_in.name):
            raise BadRequestException(f"Tag '{tag_in.name}' already exists")

        tag_data = tag_in.model_dump()
        tag_data["user_id"] = user_id

        return await self.tag_repo.create(tag_data)

    async def get_tag(self, tag_id: int, user_id: int) -> Tag:
        """
        获取标签详情

        Args:
            tag_id: 标签 ID
            user_id: 用户 ID

        Returns:
            标签对象

        Raises:
            NotFoundException: 标签不存在
            ForbiddenException: 无权访问
        """
        tag = await self.tag_repo.get_by_id(tag_id)

        if not tag:
            raise NotFoundException(f"Tag with id {tag_id} not found")

        if tag.user_id != user_id:
            raise ForbiddenException("You don't have permission to access this tag")

        return tag

    async def get_user_tags(self, user_id: int) -> List[Tag]:
        """
        获取用户的所有标签

        Args:
            user_id: 用户 ID

        Returns:
            标签列表
        """
        return await self.tag_repo.get_user_tags(user_id)

    async def update_tag(
        self,
        tag_id: int,
        user_id: int,
        tag_in: TagUpdate,
    ) -> Tag:
        """
        更新标签

        Args:
            tag_id: 标签 ID
            user_id: 用户 ID
            tag_in: 更新数据

        Returns:
            更新后的标签
        """
        tag = await self.get_tag(tag_id, user_id)

        # 检查名称是否冲突
        if tag_in.name and tag_in.name != tag.name:
            if await self.tag_repo.name_exists(user_id, tag_in.name):
                raise BadRequestException(f"Tag '{tag_in.name}' already exists")

        update_data = tag_in.model_dump(exclude_unset=True)
        return await self.tag_repo.update(tag, update_data)

    async def delete_tag(self, tag_id: int, user_id: int) -> bool:
        """
        删除标签

        Args:
            tag_id: 标签 ID
            user_id: 用户 ID

        Returns:
            是否成功
        """
        await self.get_tag(tag_id, user_id)
        return await self.tag_repo.delete(tag_id)
