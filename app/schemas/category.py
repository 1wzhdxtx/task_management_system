"""
分类相关 Schema
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    """分类基础 Schema"""
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="分类名称",
    )
    description: Optional[str] = Field(
        None,
        max_length=200,
        description="分类描述",
    )
    color: str = Field(
        default="#3B82F6",
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="颜色（HEX格式）",
    )


class CategoryCreate(CategoryBase):
    """创建分类请求"""
    pass


class CategoryUpdate(BaseModel):
    """更新分类请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class CategoryResponse(CategoryBase):
    """分类响应"""
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
