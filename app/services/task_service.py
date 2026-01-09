"""
任务服务
核心业务逻辑层，处理任务相关操作
"""
from typing import Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.task import Task, TaskStatus
from app.repositories.task_repository import TaskRepository
from app.repositories.tag_repository import TagRepository
from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)


class TaskService:
    """
    任务服务

    封装任务相关的业务逻辑，包括 CRUD、状态管理、统计等
    体现工程能力：业务逻辑封装、权限校验、事务管理
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.tag_repo = TagRepository(db)

    async def create_task(self, user_id: int, task_in: TaskCreate) -> Task:
        """
        创建任务

        Args:
            user_id: 创建者用户 ID
            task_in: 任务创建数据

        Returns:
            创建的任务对象
        """
        # 准备任务数据
        task_data = task_in.model_dump(exclude={"tag_ids"})
        task_data["user_id"] = user_id

        # 创建任务
        task = await self.task_repo.create(task_data)

        # 关联标签
        if task_in.tag_ids:
            # 验证标签属于该用户
            valid_tags = await self.tag_repo.get_by_ids(user_id, task_in.tag_ids)
            if valid_tags:
                task = await self.task_repo.update_task_tags(task, [t.id for t in valid_tags])

        return task

    async def get_task(self, task_id: int, user_id: int) -> Task:
        """
        获取任务详情（含权限校验）

        Args:
            task_id: 任务 ID
            user_id: 当前用户 ID

        Returns:
            任务对象

        Raises:
            NotFoundException: 任务不存在
            ForbiddenException: 无权访问
        """
        task = await self.task_repo.get_task_with_relations(task_id)

        if not task:
            raise NotFoundException(f"Task with id {task_id} not found")

        if task.user_id != user_id:
            raise ForbiddenException("You don't have permission to access this task")

        return task

    async def get_user_tasks(
        self,
        user_id: int,
        status: Optional[TaskStatus] = None,
        category_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> TaskListResponse:
        """
        获取用户任务列表（分页）

        Args:
            user_id: 用户 ID
            status: 状态筛选
            category_id: 分类筛选
            page: 页码
            page_size: 每页数量

        Returns:
            分页任务列表响应
        """
        skip = (page - 1) * page_size

        # 获取任务列表
        tasks = await self.task_repo.get_user_tasks(
            user_id=user_id,
            status=status,
            category_id=category_id,
            skip=skip,
            limit=page_size,
        )

        # 获取总数
        total = await self.task_repo.count_user_tasks(
            user_id=user_id,
            status=status,
            category_id=category_id,
        )

        total_pages = (total + page_size - 1) // page_size

        return TaskListResponse(
            items=[TaskResponse.model_validate(t) for t in tasks],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def update_task(
        self,
        task_id: int,
        user_id: int,
        task_in: TaskUpdate,
    ) -> Task:
        """
        更新任务

        Args:
            task_id: 任务 ID
            user_id: 当前用户 ID
            task_in: 更新数据

        Returns:
            更新后的任务

        Raises:
            NotFoundException: 任务不存在
            ForbiddenException: 无权操作
        """
        # 验证权限
        task = await self.get_task(task_id, user_id)

        # 更新基本信息
        update_data = task_in.model_dump(exclude_unset=True, exclude={"tag_ids"})
        if update_data:
            task = await self.task_repo.update(task, update_data)

        # 更新标签
        if task_in.tag_ids is not None:
            valid_tags = await self.tag_repo.get_by_ids(user_id, task_in.tag_ids)
            task = await self.task_repo.update_task_tags(
                task,
                [t.id for t in valid_tags]
            )

        return task

    async def delete_task(self, task_id: int, user_id: int) -> bool:
        """
        删除任务

        Args:
            task_id: 任务 ID
            user_id: 当前用户 ID

        Returns:
            是否删除成功

        Raises:
            NotFoundException: 任务不存在
            ForbiddenException: 无权操作
        """
        # 验证权限
        await self.get_task(task_id, user_id)
        return await self.task_repo.delete(task_id)

    async def change_status(
        self,
        task_id: int,
        user_id: int,
        new_status: TaskStatus,
    ) -> Task:
        """
        更改任务状态

        Args:
            task_id: 任务 ID
            user_id: 当前用户 ID
            new_status: 新状态

        Returns:
            更新后的任务
        """
        task = await self.get_task(task_id, user_id)
        return await self.task_repo.update(task, {"status": new_status})

    async def get_task_statistics(self, user_id: int) -> Dict:
        """
        获取任务统计信息

        Args:
            user_id: 用户 ID

        Returns:
            统计信息字典
        """
        status_counts = await self.task_repo.count_by_status(user_id)
        total = sum(status_counts.values())

        # 计算各状态数量和完成率
        completed = status_counts.get(TaskStatus.COMPLETED, 0)
        completion_rate = (completed / total * 100) if total > 0 else 0

        return {
            "total": total,
            "by_status": {str(k.value): v for k, v in status_counts.items()},
            "completion_rate": round(completion_rate, 2),
        }
