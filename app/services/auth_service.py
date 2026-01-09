"""
认证服务
处理用户注册、登录和令牌管理
"""
from datetime import timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token
from app.schemas.user import UserCreate

settings = get_settings()


class AuthService:
    """
    认证服务

    处理用户注册、登录验证和 JWT 令牌生成
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, user_in: UserCreate) -> User:
        """
        用户注册

        Args:
            user_in: 注册信息

        Returns:
            创建的用户对象

        Raises:
            BadRequestException: 邮箱或用户名已存在
        """
        # 检查邮箱是否已存在
        if await self.user_repo.email_exists(user_in.email):
            raise BadRequestException("Email already registered")

        # 检查用户名是否已存在
        if await self.user_repo.username_exists(user_in.username):
            raise BadRequestException("Username already taken")

        # 创建用户
        user_data = {
            "username": user_in.username,
            "email": user_in.email,
            "hashed_password": get_password_hash(user_in.password),
        }

        return await self.user_repo.create(user_data)

    async def authenticate(
        self,
        email: str,
        password: str,
    ) -> Optional[User]:
        """
        验证用户凭据

        Args:
            email: 邮箱
            password: 密码

        Returns:
            验证成功返回用户，否则返回 None
        """
        user = await self.user_repo.get_by_email(email)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    async def login(self, email: str, password: str) -> Token:
        """
        用户登录

        Args:
            email: 邮箱
            password: 密码

        Returns:
            JWT Token

        Raises:
            UnauthorizedException: 认证失败
        """
        user = await self.authenticate(email, password)

        if not user:
            raise UnauthorizedException("Incorrect email or password")

        if not user.is_active:
            raise UnauthorizedException("User account is disabled")

        # 生成访问令牌
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return Token(access_token=access_token, token_type="bearer")
