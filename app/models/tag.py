"""
标签模型
"""
from typing import TYPE_CHECKING, List

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task


class Tag(BaseModel):
    """
    任务标签模型

    标签与任务是多对多关系，支持灵活分类
    """
    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uk_user_tag"),
    )

    name: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="标签名称",
    )
    color: Mapped[str] = mapped_column(
        String(7),
        default="#10B981",
        comment="显示颜色（HEX格式）",
    )

    # 外键
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        comment="所属用户ID",
    )

    # 关系定义
    user: Mapped["User"] = relationship(
        "User",
        back_populates="tags",
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        secondary="task_tags",
        back_populates="tags",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name={self.name})>"
