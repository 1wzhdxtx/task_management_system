"""
API 依赖注入模块
提供认证和服务注入
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.category_service import CategoryService
from app.services.tag_service import TagService
from app.services.task_service import TaskService
from app.services.user_service import UserService

# HTTP Bearer 认证方案
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    获取当前认证用户

    通过 JWT Token 验证用户身份，用于需要认证的接口

    Args:
        credentials: HTTP Bearer Token
        db: 数据库会话

    Returns:
        当前登录的用户对象

    Raises:
        HTTPException: Token 无效或用户不存在/禁用
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 解码 Token
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    # 获取用户 ID
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    # 查询用户
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return user


# ====== Service 依赖注入 ======

def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """获取认证服务"""
    return AuthService(db)


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """获取用户服务"""
    return UserService(db)


def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    """获取任务服务"""
    return TaskService(db)


def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    """获取分类服务"""
    return CategoryService(db)


def get_tag_service(db: AsyncSession = Depends(get_db)) -> TagService:
    """获取标签服务"""
    return TagService(db)
