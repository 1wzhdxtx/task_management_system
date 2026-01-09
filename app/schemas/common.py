"""
通用 Schema 定义
"""
from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")

    @property
    def skip(self) -> int:
        """计算跳过的记录数"""
        return (self.page - 1) * self.page_size
