"""
用户数据访问层
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    用户 Repository

    继承基类 CRUD，扩展用户特定查询方法
    """

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户

        Args:
            email: 用户邮箱

        Returns:
            用户对象或 None
        """
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户

        Args:
            username: 用户名

        Returns:
            用户对象或 None
        """
        query = select(User).where(User.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """
        检查邮箱是否已存在

        Args:
            email: 邮箱地址

        Returns:
            是否存在
        """
        user = await self.get_by_email(email)
        return user is not None

    async def username_exists(self, username: str) -> bool:
        """
        检查用户名是否已存在

        Args:
            username: 用户名

        Returns:
            是否存在
        """
        user = await self.get_by_username(username)
        return user is not None
