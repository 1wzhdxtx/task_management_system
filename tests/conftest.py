"""
测试配置模块
定义 pytest fixtures 和测试数据库设置
"""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.user import User

settings = get_settings()

# 测试数据库 URL（使用 SQLite 内存数据库进行测试）
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# 创建测试数据库引擎
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

# 测试会话工厂
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    创建测试数据库会话

    每个测试函数使用独立的数据库会话，测试后自动清理
    """
    # 创建所有表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    # 删除所有表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    创建测试 HTTP 客户端

    自动替换数据库依赖为测试数据库
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """
    创建测试用户

    用于需要认证的测试用例
    """
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """
    生成认证请求头

    包含测试用户的 JWT Token
    """
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_user_data() -> dict:
    """测试用户数据"""
    return {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
    }


@pytest.fixture
def test_task_data() -> dict:
    """测试任务数据"""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "high",
        "status": "pending",
    }
