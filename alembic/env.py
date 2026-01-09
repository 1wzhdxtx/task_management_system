"""
Alembic 迁移环境配置
"""
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# 导入模型和配置
from app.core.config import get_settings
from app.core.database import Base
from app.models import *  # noqa: F401, F403

# Alembic Config 对象
config = context.config

# 设置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 元数据（用于 autogenerate）
target_metadata = Base.metadata

# 从应用配置获取数据库 URL
settings = get_settings()


def get_url():
    """获取同步数据库 URL"""
    return settings.SYNC_DATABASE_URL


def run_migrations_offline() -> None:
    """
    离线模式运行迁移

    只生成 SQL 语句，不连接数据库
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    在线模式运行迁移

    连接数据库执行迁移
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # 检测列类型变化
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
