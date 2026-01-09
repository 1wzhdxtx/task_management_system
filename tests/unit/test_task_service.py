"""
任务服务单元测试
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService


class TestTaskService:
    """任务服务测试类"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return AsyncMock()

    @pytest.fixture
    def task_service(self, mock_db):
        """创建带模拟依赖的任务服务"""
        service = TaskService(mock_db)
        service.task_repo = AsyncMock()
        service.tag_repo = AsyncMock()
        return service

    @pytest.fixture
    def sample_task(self):
        """创建示例任务"""
        task = MagicMock(spec=Task)
        task.id = 1
        task.title = "Test Task"
        task.description = "Test Description"
        task.status = TaskStatus.PENDING
        task.priority = TaskPriority.MEDIUM
        task.user_id = 1
        task.category_id = None
        task.tags = []
        return task

    @pytest.mark.asyncio
    async def test_create_task_success(self, task_service, sample_task):
        """测试成功创建任务"""
        # Arrange
        user_id = 1
        task_in = TaskCreate(
            title="New Task",
            description="Task description",
            priority="high",
        )
        task_service.task_repo.create.return_value = sample_task

        # Act
        result = await task_service.create_task(user_id, task_in)

        # Assert
        assert result.id == 1
        task_service.task_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_task_with_tags(self, task_service, sample_task):
        """测试创建带标签的任务"""
        # Arrange
        user_id = 1
        task_in = TaskCreate(
            title="Tagged Task",
            tag_ids=[1, 2, 3],
        )
        task_service.task_repo.create.return_value = sample_task
        task_service.tag_repo.get_by_ids.return_value = [
            MagicMock(id=1),
            MagicMock(id=2),
        ]
        task_service.task_repo.update_task_tags.return_value = sample_task

        # Act
        result = await task_service.create_task(user_id, task_in)

        # Assert
        task_service.tag_repo.get_by_ids.assert_called_once()
        task_service.task_repo.update_task_tags.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_task_success(self, task_service, sample_task):
        """测试成功获取任务"""
        # Arrange
        task_service.task_repo.get_task_with_relations.return_value = sample_task

        # Act
        result = await task_service.get_task(1, user_id=1)

        # Assert
        assert result.id == 1
        assert result.title == "Test Task"

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, task_service):
        """测试获取不存在的任务"""
        # Arrange
        task_service.task_repo.get_task_with_relations.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            await task_service.get_task(999, user_id=1)

        assert "not found" in str(exc_info.value.message).lower()

    @pytest.mark.asyncio
    async def test_get_task_forbidden(self, task_service, sample_task):
        """测试访问他人任务被拒绝"""
        # Arrange
        sample_task.user_id = 2  # 不同用户
        task_service.task_repo.get_task_with_relations.return_value = sample_task

        # Act & Assert
        with pytest.raises(ForbiddenException):
            await task_service.get_task(1, user_id=1)

    @pytest.mark.asyncio
    async def test_update_task_success(self, task_service, sample_task):
        """测试成功更新任务"""
        # Arrange
        task_service.task_repo.get_task_with_relations.return_value = sample_task
        task_service.task_repo.update.return_value = sample_task
        task_in = TaskUpdate(title="Updated Title")

        # Act
        result = await task_service.update_task(1, user_id=1, task_in=task_in)

        # Assert
        task_service.task_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_task_success(self, task_service, sample_task):
        """测试成功删除任务"""
        # Arrange
        task_service.task_repo.get_task_with_relations.return_value = sample_task
        task_service.task_repo.delete.return_value = True

        # Act
        result = await task_service.delete_task(1, user_id=1)

        # Assert
        assert result is True
        task_service.task_repo.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_change_status(self, task_service, sample_task):
        """测试更改任务状态"""
        # Arrange
        task_service.task_repo.get_task_with_relations.return_value = sample_task
        sample_task.status = TaskStatus.COMPLETED
        task_service.task_repo.update.return_value = sample_task

        # Act
        result = await task_service.change_status(
            1, user_id=1, new_status=TaskStatus.COMPLETED
        )

        # Assert
        task_service.task_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_task_statistics(self, task_service):
        """测试获取任务统计"""
        # Arrange
        task_service.task_repo.count_by_status.return_value = {
            TaskStatus.PENDING: 5,
            TaskStatus.IN_PROGRESS: 3,
            TaskStatus.COMPLETED: 10,
        }

        # Act
        result = await task_service.get_task_statistics(user_id=1)

        # Assert
        assert result["total"] == 18
        assert result["completion_rate"] == pytest.approx(55.56, rel=0.01)
