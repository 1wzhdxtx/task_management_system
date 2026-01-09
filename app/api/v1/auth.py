"""
认证相关 API
"""
from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="注册新用户账户",
)
async def register(
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    用户注册

    - **username**: 用户名（3-50字符，仅字母数字下划线）
    - **email**: 有效邮箱地址
    - **password**: 密码（至少6个字符）
    """
    user = await auth_service.register(user_in)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    summary="用户登录",
    description="使用邮箱和密码登录，获取 JWT Token",
)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    用户登录

    返回 JWT 访问令牌，用于后续 API 认证
    """
    return await auth_service.login(login_data.email, login_data.password)
