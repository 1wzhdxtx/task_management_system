"""
模型基类模块
定义公共字段和混入类，减少代码重复
"""
from datetime import datetime

from sqlalchemy import Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TimestampMixin:
    """
    时间戳混入类

    为模型提供 created_at 和 updated_at 字段
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class BaseModel(Base, TimestampMixin):
    """
    所有业务模型的基类

    提供：
    - 自增主键 id
    - 创建时间 created_at
    - 更新时间 updated_at
    """
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
