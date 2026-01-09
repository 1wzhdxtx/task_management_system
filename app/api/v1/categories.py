"""
分类相关 API
"""
from typing import List

from fastapi import APIRouter, Depends, status

from app.api.deps import get_category_service, get_current_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.common import MessageResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建分类",
)
async def create_category(
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service),
):
    """
    创建新分类

    - **name**: 分类名称（必填）
    - **description**: 分类描述
    - **color**: 显示颜色（HEX格式，如 #3B82F6）
    """
    category = await category_service.create_category(current_user.id, category_in)
    return CategoryResponse.model_validate(category)


@router.get(
    "",
    response_model=List[CategoryResponse],
    summary="获取分类列表",
)
async def get_categories(
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service),
):
    """获取当前用户的所有分类"""
    categories = await category_service.get_user_categories(current_user.id)
    return [CategoryResponse.model_validate(c) for c in categories]


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="获取分类详情",
)
async def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service),
):
    """获取指定分类的详细信息"""
    category = await category_service.get_category(category_id, current_user.id)
    return CategoryResponse.model_validate(category)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="更新分类",
)
async def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service),
):
    """更新分类信息"""
    category = await category_service.update_category(
        category_id, current_user.id, category_in
    )
    return CategoryResponse.model_validate(category)


@router.delete(
    "/{category_id}",
    response_model=MessageResponse,
    summary="删除分类",
)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service),
):
    """删除分类（不会删除该分类下的任务）"""
    await category_service.delete_category(category_id, current_user.id)
    return MessageResponse(message="Category deleted successfully")
