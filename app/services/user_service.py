"""
用户服务
处理用户相关业务逻辑
"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.security import get_password_hash
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate


class UserService:
    """
    用户服务

    处理用户信息管理
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_user(self, user_id: int) -> User:
        """
        获取用户信息

        Args:
            user_id: 用户 ID

        Returns:
            用户对象

        Raises:
            NotFoundException: 用户不存在
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")
        return user

    async def update_user(
        self,
        user_id: int,
        user_in: UserUpdate,
    ) -> User:
        """
        更新用户信息

        Args:
            user_id: 用户 ID
            user_in: 更新数据

        Returns:
            更新后的用户

        Raises:
            NotFoundException: 用户不存在
            BadRequestException: 邮箱或用户名冲突
        """
        user = await self.get_user(user_id)

        # 检查邮箱冲突
        if user_in.email and user_in.email != user.email:
            if await self.user_repo.email_exists(user_in.email):
                raise BadRequestException("Email already in use")

        # 检查用户名冲突
        if user_in.username and user_in.username != user.username:
            if await self.user_repo.username_exists(user_in.username):
                raise BadRequestException("Username already taken")

        # 准备更新数据
        update_data = user_in.model_dump(exclude_unset=True)

        # 处理密码更新
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        return await self.user_repo.update(user, update_data)

    async def deactivate_user(self, user_id: int) -> User:
        """
        停用用户账户

        Args:
            user_id: 用户 ID

        Returns:
            更新后的用户
        """
        user = await self.get_user(user_id)
        return await self.user_repo.update(user, {"is_active": False})
