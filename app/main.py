"""
应用入口
FastAPI 应用创建和配置
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.utils.logger import setup_logging

# 初始化配置和日志
settings = get_settings()
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    处理启动和关闭时的初始化/清理工作
    """
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    yield

    logger.info("Shutting down application...")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Task Management System

一个展示工程化最佳实践的任务管理系统 Demo

### 功能特性
- 用户认证（JWT）
- 任务 CRUD
- 分类与标签管理
- 任务状态流转
- 统计分析

### 技术栈
- FastAPI + SQLAlchemy 2.0
- MySQL + Alembic
- Pydantic + JWT
""",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Authentication", "description": "用户认证相关接口"},
        {"name": "Users", "description": "用户信息管理"},
        {"name": "Tasks", "description": "任务管理核心接口"},
        {"name": "Categories", "description": "任务分类管理"},
        {"name": "Tags", "description": "任务标签管理"},
        {"name": "Health", "description": "健康检查"},
    ],
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# 模板引擎
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# 注册 API 路由
app.include_router(api_router, prefix="/api/v1")


# 全局异常处理
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """处理自定义业务异常"""
    logger.warning(f"App exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理未捕获的异常"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# 健康检查
@app.get("/health", tags=["Health"], summary="健康检查")
async def health_check():
    """
    健康检查接口

    用于负载均衡和监控系统检测服务状态
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "app_name": settings.APP_NAME,
    }


# ====== Web 页面路由 ======

@app.get("/", include_in_schema=False)
async def index(request: Request):
    """Web 首页"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "app_name": settings.APP_NAME},
    )


@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    """登录页面"""
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request},
    )


@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    """注册页面"""
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request},
    )


@app.get("/tasks", include_in_schema=False)
async def tasks_page(request: Request):
    """任务列表页面"""
    return templates.TemplateResponse(
        "tasks/list.html",
        {"request": request},
    )


@app.get("/categories", include_in_schema=False)
async def categories_page(request: Request):
    """分类管理页面"""
    return templates.TemplateResponse(
        "categories/list.html",
        {"request": request},
    )


@app.get("/tags", include_in_schema=False)
async def tags_page(request: Request):
    """标签管理页面"""
    return templates.TemplateResponse(
        "tags/list.html",
        {"request": request},
    )


@app.get("/profile", include_in_schema=False)
async def profile_page(request: Request):
    """个人资料页面"""
    return templates.TemplateResponse(
        "profile/index.html",
        {"request": request},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
