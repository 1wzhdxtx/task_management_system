"""
数据库连接模块
实现异步数据库会话管理和连接池配置
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

# 创建异步数据库引擎
# SQLite 不支持连接池参数
_engine_kwargs = {
    "echo": settings.DEBUG,
}

# MySQL 特定参数
if not settings.ASYNC_DATABASE_URL.startswith("sqlite"):
    _engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600,
    })

engine = create_async_engine(settings.ASYNC_DATABASE_URL, **_engine_kwargs)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """ORM 模型基类"""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖注入函数

    使用 async with 确保会话正确关闭，异常时自动回滚
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
