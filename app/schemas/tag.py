"""
标签相关 Schema
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TagBase(BaseModel):
    """标签基础 Schema"""
    name: str = Field(
        ...,
        min_length=1,
        max_length=30,
        description="标签名称",
    )
    color: str = Field(
        default="#10B981",
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="颜色（HEX格式）",
    )


class TagCreate(TagBase):
    """创建标签请求"""
    pass


class TagUpdate(BaseModel):
    """更新标签请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=30)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class TagResponse(TagBase):
    """标签响应"""
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
