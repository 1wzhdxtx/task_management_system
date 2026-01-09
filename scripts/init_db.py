#!/usr/bin/env python3
"""
数据库初始化脚本
创建数据库和表结构
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.core.database import Base, engine
from app.models import *  # noqa: F401, F403


async def init_database():
    """初始化数据库"""
    settings = get_settings()

    print(f"Initializing database: {settings.DB_NAME}")
    print(f"Host: {settings.DB_HOST}:{settings.DB_PORT}")

    # Create database if not exists (using sync connection)
    db_url_without_db = (
        f"mysql+aiomysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/"
    )

    try:
        temp_engine = create_async_engine(db_url_without_db, echo=False)
        async with temp_engine.connect() as conn:
            await conn.execute(
                text(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME} "
                     "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            )
            await conn.commit()
        await temp_engine.dispose()
        print(f"Database '{settings.DB_NAME}' created or already exists")
    except Exception as e:
        print(f"Error creating database: {e}")
        print("Please ensure MySQL is running and credentials are correct")
        sys.exit(1)

    # Create all tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("All tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)

    print("\nDatabase initialization completed!")
    print("You can now run 'make run' to start the application")


if __name__ == "__main__":
    asyncio.run(init_database())
