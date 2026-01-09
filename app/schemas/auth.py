"""
认证相关 Schema
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """JWT Token 响应"""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token 载荷"""
    sub: Optional[int] = None  # user_id
    exp: Optional[int] = None  # 过期时间戳


class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., description="密码")
