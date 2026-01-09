"""
API v1 路由聚合
"""
from fastapi import APIRouter

from app.api.v1 import auth, categories, tags, tasks, users

api_router = APIRouter()

# 注册子路由
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(tasks.router)
api_router.include_router(categories.router)
api_router.include_router(tags.router)
