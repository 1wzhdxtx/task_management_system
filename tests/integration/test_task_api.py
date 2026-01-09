"""
任务 API 集成测试
"""
import pytest
from httpx import AsyncClient


class TestTaskAPI:
    """任务 API 测试类"""

    @pytest.mark.asyncio
    async def test_create_task_success(
        self, client: AsyncClient, auth_headers: dict, test_task_data: dict
    ):
        """测试成功创建任务"""
        response = await client.post(
            "/api/v1/tasks",
            json=test_task_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == test_task_data["title"]
        assert data["description"] == test_task_data["description"]
        assert data["priority"] == test_task_data["priority"]
        assert data["status"] == "pending"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_task_unauthorized(
        self, client: AsyncClient, test_task_data: dict
    ):
        """测试未授权创建任务"""
        response = await client.post("/api/v1/tasks", json=test_task_data)

        # 401 for missing credentials, 403 for forbidden
        assert response.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_get_tasks_list(self, client: AsyncClient, auth_headers: dict):
        """测试获取任务列表"""
        # 先创建几个任务
        for i in range(3):
            await client.post(
                "/api/v1/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )

        response = await client.get("/api/v1/tasks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
        assert data["page"] == 1

    @pytest.mark.asyncio
    async def test_get_tasks_with_pagination(
        self, client: AsyncClient, auth_headers: dict
    ):
        """测试任务列表分页"""
        # 创建 5 个任务
        for i in range(5):
            await client.post(
                "/api/v1/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )

        # 请求第一页，每页 2 条
        response = await client.get(
            "/api/v1/tasks?page=1&page_size=2",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["total_pages"] == 3

    @pytest.mark.asyncio
    async def test_get_tasks_filter_by_status(
        self, client: AsyncClient, auth_headers: dict
    ):
        """测试按状态筛选任务"""
        # 创建不同状态的任务
        await client.post(
            "/api/v1/tasks",
            json={"title": "Pending Task", "status": "pending"},
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/tasks",
            json={"title": "Completed Task", "status": "completed"},
            headers=auth_headers,
        )

        response = await client.get(
            "/api/v1/tasks?status=pending",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        for task in data["items"]:
            assert task["status"] == "pending"

    @pytest.mark.asyncio
    async def test_get_task_detail(self, client: AsyncClient, auth_headers: dict):
        """测试获取任务详情"""
        # 先创建任务
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Detail Test Task"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Detail Test Task"

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, client: AsyncClient, auth_headers: dict):
        """测试获取不存在的任务"""
        response = await client.get("/api/v1/tasks/99999", headers=auth_headers)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_task(self, client: AsyncClient, auth_headers: dict):
        """测试更新任务"""
        # 先创建任务
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Original Title"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # 更新任务
        response = await client.put(
            f"/api/v1/tasks/{task_id}",
            json={"title": "Updated Title", "priority": "urgent"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["priority"] == "urgent"

    @pytest.mark.asyncio
    async def test_change_task_status(self, client: AsyncClient, auth_headers: dict):
        """测试更改任务状态"""
        # 先创建任务
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Status Test"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # 更改状态
        response = await client.patch(
            f"/api/v1/tasks/{task_id}/status?new_status=completed",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    @pytest.mark.asyncio
    async def test_delete_task(self, client: AsyncClient, auth_headers: dict):
        """测试删除任务"""
        # 先创建任务
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "To Delete"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # 删除任务
        response = await client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200

        # 确认已删除
        get_response = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_task_statistics(self, client: AsyncClient, auth_headers: dict):
        """测试获取任务统计"""
        # 创建不同状态的任务
        await client.post(
            "/api/v1/tasks",
            json={"title": "Task 1", "status": "pending"},
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/tasks",
            json={"title": "Task 2", "status": "completed"},
            headers=auth_headers,
        )

        response = await client.get("/api/v1/tasks/statistics", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_status" in data
        assert "completion_rate" in data
