"""
Repository 基类模块
实现通用 CRUD 操作，体现泛型编程和代码复用
"""
from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    通用 Repository 基类

    使用泛型实现，为所有模型提供统一的 CRUD 接口
    体现工程能力：泛型编程、关注点分离、代码复用
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        初始化 Repository

        Args:
            model: ORM 模型类
            db: 异步数据库会话
        """
        self.model = model
        self.db = db

    async def get_by_id(
        self,
        id: int,
        options: Optional[List[Any]] = None,
    ) -> Optional[ModelType]:
        """
        根据 ID 获取单个实体

        Args:
            id: 实体 ID
            options: SQLAlchemy 查询选项（如 selectinload）

        Returns:
            实体对象或 None
        """
        query = select(self.model).where(self.model.id == id)
        if options:
            for opt in options:
                query = query.options(opt)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[List[Any]] = None,
        order_by: Optional[Any] = None,
        options: Optional[List[Any]] = None,
    ) -> List[ModelType]:
        """
        获取实体列表（支持分页、过滤、排序）

        Args:
            skip: 跳过记录数
            limit: 返回记录数
            filters: 过滤条件列表
            order_by: 排序条件
            options: 查询选项

        Returns:
            实体列表
        """
        query = select(self.model)

        if filters:
            for f in filters:
                query = query.where(f)

        if options:
            for opt in options:
                query = query.options(opt)

        if order_by is not None:
            query = query.order_by(order_by)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(self, filters: Optional[List[Any]] = None) -> int:
        """
        统计实体数量

        Args:
            filters: 过滤条件列表

        Returns:
            记录数量
        """
        query = select(func.count()).select_from(self.model)
        if filters:
            for f in filters:
                query = query.where(f)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def create(self, obj_in: dict) -> ModelType:
        """
        创建实体

        Args:
            obj_in: 实体数据字典

        Returns:
            创建的实体
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        obj_in: dict,
    ) -> ModelType:
        """
        更新实体

        Args:
            db_obj: 数据库实体对象
            obj_in: 更新数据字典

        Returns:
            更新后的实体
        """
        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        """
        删除实体

        Args:
            id: 实体 ID

        Returns:
            是否删除成功
        """
        query = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.rowcount > 0

    async def exists(self, id: int) -> bool:
        """
        检查实体是否存在

        Args:
            id: 实体 ID

        Returns:
            是否存在
        """
        query = select(func.count()).select_from(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return (result.scalar() or 0) > 0
