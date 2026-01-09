"""
标签相关 API
"""
from typing import List

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user, get_tag_service
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.tag import TagCreate, TagResponse, TagUpdate
from app.services.tag_service import TagService

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.post(
    "",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建标签",
)
async def create_tag(
    tag_in: TagCreate,
    current_user: User = Depends(get_current_user),
    tag_service: TagService = Depends(get_tag_service),
):
    """
    创建新标签

    - **name**: 标签名称（必填）
    - **color**: 显示颜色（HEX格式，如 #10B981）
    """
    tag = await tag_service.create_tag(current_user.id, tag_in)
    return TagResponse.model_validate(tag)


@router.get(
    "",
    response_model=List[TagResponse],
    summary="获取标签列表",
)
async def get_tags(
    current_user: User = Depends(get_current_user),
    tag_service: TagService = Depends(get_tag_service),
):
    """获取当前用户的所有标签"""
    tags = await tag_service.get_user_tags(current_user.id)
    return [TagResponse.model_validate(t) for t in tags]


@router.get(
    "/{tag_id}",
    response_model=TagResponse,
    summary="获取标签详情",
)
async def get_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    tag_service: TagService = Depends(get_tag_service),
):
    """获取指定标签的详细信息"""
    tag = await tag_service.get_tag(tag_id, current_user.id)
    return TagResponse.model_validate(tag)


@router.put(
    "/{tag_id}",
    response_model=TagResponse,
    summary="更新标签",
)
async def update_tag(
    tag_id: int,
    tag_in: TagUpdate,
    current_user: User = Depends(get_current_user),
    tag_service: TagService = Depends(get_tag_service),
):
    """更新标签信息"""
    tag = await tag_service.update_tag(tag_id, current_user.id, tag_in)
    return TagResponse.model_validate(tag)


@router.delete(
    "/{tag_id}",
    response_model=MessageResponse,
    summary="删除标签",
)
async def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    tag_service: TagService = Depends(get_tag_service),
):
    """删除标签（会自动解除与任务的关联）"""
    await tag_service.delete_tag(tag_id, current_user.id)
    return MessageResponse(message="Tag deleted successfully")
