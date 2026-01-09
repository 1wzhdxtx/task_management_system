"""
认证服务单元测试
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.core.exceptions import BadRequestException, UnauthorizedException
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService


class TestAuthService:
    """认证服务测试类"""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.fixture
    def auth_service(self, mock_db):
        service = AuthService(mock_db)
        service.user_repo = AsyncMock()
        return service

    @pytest.fixture
    def sample_user(self):
        user = MagicMock(spec=User)
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        user.hashed_password = "$2b$12$test_hash"
        user.is_active = True
        return user

    @pytest.mark.asyncio
    async def test_register_success(self, auth_service, sample_user):
        """测试成功注册"""
        # Arrange
        user_in = UserCreate(
            username="newuser",
            email="new@example.com",
            password="password123",
        )
        auth_service.user_repo.email_exists.return_value = False
        auth_service.user_repo.username_exists.return_value = False
        auth_service.user_repo.create.return_value = sample_user

        # Act
        result = await auth_service.register(user_in)

        # Assert
        assert result.id == 1
        auth_service.user_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_email_exists(self, auth_service):
        """测试邮箱已存在"""
        # Arrange
        user_in = UserCreate(
            username="newuser",
            email="existing@example.com",
            password="password123",
        )
        auth_service.user_repo.email_exists.return_value = True

        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            await auth_service.register(user_in)

        assert "email" in str(exc_info.value.message).lower()

    @pytest.mark.asyncio
    async def test_register_username_exists(self, auth_service):
        """测试用户名已存在"""
        # Arrange
        user_in = UserCreate(
            username="existinguser",
            email="new@example.com",
            password="password123",
        )
        auth_service.user_repo.email_exists.return_value = False
        auth_service.user_repo.username_exists.return_value = True

        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            await auth_service.register(user_in)

        assert "username" in str(exc_info.value.message).lower()

    @pytest.mark.asyncio
    async def test_login_success(self, auth_service, sample_user, monkeypatch):
        """测试成功登录"""
        # Arrange
        auth_service.user_repo.get_by_email.return_value = sample_user

        # Mock password verification
        monkeypatch.setattr(
            "app.services.auth_service.verify_password",
            lambda p, h: True
        )

        # Act
        result = await auth_service.login("test@example.com", "password123")

        # Assert
        assert result.access_token is not None
        assert result.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, auth_service):
        """测试用户不存在"""
        # Arrange
        auth_service.user_repo.get_by_email.return_value = None

        # Act & Assert
        with pytest.raises(UnauthorizedException):
            await auth_service.login("unknown@example.com", "password")

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, auth_service, sample_user, monkeypatch):
        """测试密码错误"""
        # Arrange
        auth_service.user_repo.get_by_email.return_value = sample_user
        monkeypatch.setattr(
            "app.services.auth_service.verify_password",
            lambda p, h: False
        )

        # Act & Assert
        with pytest.raises(UnauthorizedException):
            await auth_service.login("test@example.com", "wrongpassword")

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, auth_service, sample_user, monkeypatch):
        """测试禁用用户登录"""
        # Arrange
        sample_user.is_active = False
        auth_service.user_repo.get_by_email.return_value = sample_user
        monkeypatch.setattr(
            "app.services.auth_service.verify_password",
            lambda p, h: True
        )

        # Act & Assert
        with pytest.raises(UnauthorizedException):
            await auth_service.login("test@example.com", "password123")
