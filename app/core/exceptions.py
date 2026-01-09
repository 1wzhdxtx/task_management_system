"""
自定义异常模块
定义统一的业务异常类，便于全局异常处理
"""
from typing import Any, Optional


class AppException(Exception):
    """应用基础异常类"""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        detail: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class NotFoundException(AppException):
    """资源未找到异常"""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=404)


class ForbiddenException(AppException):
    """权限不足异常"""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message=message, status_code=403)


class UnauthorizedException(AppException):
    """未授权异常"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, status_code=401)


class BadRequestException(AppException):
    """请求参数错误异常"""

    def __init__(self, message: str = "Bad request"):
        super().__init__(message=message, status_code=400)


class ConflictException(AppException):
    """资源冲突异常（如重复创建）"""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message=message, status_code=409)
