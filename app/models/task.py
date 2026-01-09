"""
任务模型
"""
import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Text, Enum, ForeignKey, DateTime, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category
    from app.models.tag import Tag


class TaskStatus(str, enum.Enum):
    """任务状态枚举"""
    PENDING = "pending"           # 待处理
    IN_PROGRESS = "in_progress"   # 进行中
    COMPLETED = "completed"       # 已完成
    ARCHIVED = "archived"         # 已归档


class TaskPriority(str, enum.Enum):
    """任务优先级枚举"""
    LOW = "low"           # 低
    MEDIUM = "medium"     # 中
    HIGH = "high"         # 高
    URGENT = "urgent"     # 紧急


# 任务-标签多对多关联表
task_tags = Table(
    "task_tags",
    Base.metadata,
    Column(
        "task_id",
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Task(BaseModel):
    """
    任务模型

    核心业务实体，支持状态管理、优先级、分类和标签
    """
    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="任务标题",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="任务描述",
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus),
        default=TaskStatus.PENDING,
        index=True,
        comment="任务状态",
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority),
        default=TaskPriority.MEDIUM,
        comment="优先级",
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
        comment="截止日期",
    )

    # 外键
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        comment="所属用户ID",
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        comment="分类ID",
    )

    # 关系定义
    user: Mapped["User"] = relationship(
        "User",
        back_populates="tasks",
    )
    category: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="tasks",
    )
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary=task_tags,
        back_populates="tasks",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"
