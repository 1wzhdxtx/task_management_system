"""
用户相关 API
"""
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_user_service
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取当前用户信息",
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """获取当前登录用户的详细信息"""
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="更新当前用户信息",
)
async def update_current_user(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    更新当前用户信息

    所有字段都是可选的，只更新提供的字段
    """
    user = await user_service.update_user(current_user.id, user_in)
    return UserResponse.model_validate(user)
