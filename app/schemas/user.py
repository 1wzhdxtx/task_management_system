"""
用户相关 Schema
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """用户基础 Schema"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="用户名（3-50字符，仅字母数字下划线）",
    )
    email: EmailStr = Field(..., description="邮箱地址")


class UserCreate(UserBase):
    """创建用户请求"""
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="密码（至少6个字符）",
    )


class UserUpdate(BaseModel):
    """更新用户请求（所有字段可选）"""
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
    )
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class UserResponse(UserBase):
    """用户响应"""
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """数据库中的用户（包含密码哈希）"""
    hashed_password: str
