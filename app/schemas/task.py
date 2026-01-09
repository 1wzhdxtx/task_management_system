"""
任务相关 Schema
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TaskPriority(str, Enum):
    """任务优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TagBrief(BaseModel):
    """标签简要信息"""
    id: int
    name: str
    color: str

    model_config = ConfigDict(from_attributes=True)


class CategoryBrief(BaseModel):
    """分类简要信息"""
    id: int
    name: str
    color: str

    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    """任务基础 Schema"""
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="任务标题",
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="任务描述",
    )
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="任务状态",
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="优先级",
    )
    due_date: Optional[datetime] = Field(
        None,
        description="截止日期",
    )
    category_id: Optional[int] = Field(
        None,
        description="分类ID",
    )


class TaskCreate(TaskBase):
    """创建任务请求"""
    tag_ids: List[int] = Field(
        default_factory=list,
        description="标签ID列表",
    )


class TaskUpdate(BaseModel):
    """更新任务请求（所有字段可选）"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None


class TaskResponse(TaskBase):
    """任务响应"""
    id: int
    user_id: int
    category: Optional[CategoryBrief] = None
    tags: List[TagBrief] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """任务列表响应（分页）"""
    items: List[TaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
