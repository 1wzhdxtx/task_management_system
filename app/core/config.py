"""
应用配置模块
使用 Pydantic Settings 管理环境变量，体现配置集中化和类型安全
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用配置类

    从环境变量或 .env 文件加载配置，支持类型验证和默认值
    """

    # 应用配置
    APP_NAME: str = "Task Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 数据库配置
    # 支持直接设置 DATABASE_URL，或通过 DB_* 参数构建 MySQL URL
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "task_management"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """异步数据库连接 URL"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """同步数据库 URL（用于 Alembic 迁移）"""
        if self.DATABASE_URL:
            # Convert async URL to sync URL
            url = self.DATABASE_URL
            url = url.replace("sqlite+aiosqlite", "sqlite")
            url = url.replace("mysql+aiomysql", "mysql+pymysql")
            return url
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "logs/app.log"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例

    使用 lru_cache 确保配置只加载一次，提升性能
    """
    return Settings()
