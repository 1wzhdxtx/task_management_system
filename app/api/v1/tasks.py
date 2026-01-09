"""
任务相关 API
核心业务接口，展示 RESTful 设计和文档自动生成
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user, get_task_service
from app.models.task import TaskStatus
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建任务",
    description="创建新任务，可同时关联分类和标签",
)
async def create_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    创建新任务

    - **title**: 任务标题（必填）
    - **description**: 任务描述
    - **status**: 任务状态（pending/in_progress/completed/archived）
    - **priority**: 优先级（low/medium/high/urgent）
    - **due_date**: 截止日期
    - **category_id**: 分类 ID
    - **tag_ids**: 标签 ID 列表
    """
    task = await task_service.create_task(current_user.id, task_in)
    return TaskResponse.model_validate(task)


@router.get(
    "",
    response_model=TaskListResponse,
    summary="获取任务列表",
    description="获取当前用户的任务列表，支持筛选和分页",
)
async def get_tasks(
    status: Optional[TaskStatus] = Query(None, description="按状态筛选"),
    category_id: Optional[int] = Query(None, description="按分类筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    获取任务列表

    支持按状态和分类筛选，返回分页结果
    """
    return await task_service.get_user_tasks(
        user_id=current_user.id,
        status=status,
        category_id=category_id,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/statistics",
    summary="获取任务统计",
    description="获取当前用户的任务统计信息",
)
async def get_task_statistics(
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    获取任务统计

    返回总任务数、各状态任务数和完成率
    """
    return await task_service.get_task_statistics(current_user.id)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="获取任务详情",
)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """获取指定任务的详细信息"""
    task = await task_service.get_task(task_id, current_user.id)
    return TaskResponse.model_validate(task)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="更新任务",
)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    更新任务

    所有字段都是可选的，只更新提供的字段
    """
    task = await task_service.update_task(task_id, current_user.id, task_in)
    return TaskResponse.model_validate(task)


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
    summary="更改任务状态",
)
async def change_task_status(
    task_id: int,
    new_status: TaskStatus,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    快速更改任务状态

    用于任务状态流转，如标记完成
    """
    task = await task_service.change_status(task_id, current_user.id, new_status)
    return TaskResponse.model_validate(task)


@router.delete(
    "/{task_id}",
    response_model=MessageResponse,
    summary="删除任务",
)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """删除指定任务"""
    await task_service.delete_task(task_id, current_user.id)
    return MessageResponse(message="Task deleted successfully")
