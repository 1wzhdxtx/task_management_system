"""
分类模型
"""
from typing import TYPE_CHECKING, List

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task


class Category(BaseModel):
    """
    任务分类模型

    每个用户可以创建自己的分类，分类名称在用户范围内唯一
    """
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uk_user_category"),
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="分类名称",
    )
    description: Mapped[str] = mapped_column(
        String(200),
        nullable=True,
        default="",
        comment="分类描述",
    )
    color: Mapped[str] = mapped_column(
        String(7),
        default="#3B82F6",
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
        back_populates="categories",
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="category",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name})>"
