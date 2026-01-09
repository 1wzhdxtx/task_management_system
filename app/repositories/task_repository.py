"""
任务数据访问层
"""
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task import Task, TaskStatus
from app.models.tag import Tag
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """
    任务 Repository

    继承基类 CRUD，扩展任务特定业务查询
    """

    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)

    async def get_user_tasks(
        self,
        user_id: int,
        status: Optional[TaskStatus] = None,
        category_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Task]:
        """
        获取用户的任务列表（带预加载关联数据）

        Args:
            user_id: 用户 ID
            status: 任务状态筛选
            category_id: 分类 ID 筛选
            skip: 跳过记录数
            limit: 返回记录数

        Returns:
            任务列表
        """
        filters = [Task.user_id == user_id]

        if status:
            filters.append(Task.status == status)
        if category_id:
            filters.append(Task.category_id == category_id)

        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=Task.created_at.desc(),
            options=[
                selectinload(Task.category),
                selectinload(Task.tags),
            ],
        )

    async def get_task_with_relations(self, task_id: int) -> Optional[Task]:
        """
        获取任务详情（包含关联的分类和标签）

        Args:
            task_id: 任务 ID

        Returns:
            任务对象或 None
        """
        return await self.get_by_id(
            task_id,
            options=[
                selectinload(Task.category),
                selectinload(Task.tags),
            ],
        )

    async def update_task_tags(self, task: Task, tag_ids: List[int]) -> Task:
        """
        更新任务的标签关联

        Args:
            task: 任务对象
            tag_ids: 标签 ID 列表

        Returns:
            更新后的任务
        """
        if tag_ids:
            query = select(Tag).where(Tag.id.in_(tag_ids))
            result = await self.db.execute(query)
            tags = list(result.scalars().all())
        else:
            tags = []

        task.tags = tags
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def count_by_status(self, user_id: int) -> Dict[TaskStatus, int]:
        """
        统计用户各状态的任务数量

        Args:
            user_id: 用户 ID

        Returns:
            状态到数量的映射
        """
        query = (
            select(Task.status, func.count(Task.id).label("count"))
            .where(Task.user_id == user_id)
            .group_by(Task.status)
        )

        result = await self.db.execute(query)
        return {row.status: row.count for row in result}

    async def count_user_tasks(
        self,
        user_id: int,
        status: Optional[TaskStatus] = None,
        category_id: Optional[int] = None,
    ) -> int:
        """
        统计用户任务数量

        Args:
            user_id: 用户 ID
            status: 状态筛选
            category_id: 分类筛选

        Returns:
            任务数量
        """
        filters = [Task.user_id == user_id]

        if status:
            filters.append(Task.status == status)
        if category_id:
            filters.append(Task.category_id == category_id)

        return await self.count(filters)
