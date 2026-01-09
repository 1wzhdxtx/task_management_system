#!/usr/bin/env python3
"""
数据种子脚本
创建示例数据用于测试和演示
"""
import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.category import Category
from app.models.tag import Tag
from app.models.task import Task, TaskStatus, TaskPriority


async def seed_data():
    """创建示例数据"""
    print("Seeding database with sample data...")

    async with AsyncSessionLocal() as session:
        # Check if data already exists
        from sqlalchemy import select
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("Data already exists. Skipping seed.")
            return

        # Create demo user
        demo_user = User(
            username="demo",
            email="demo@example.com",
            hashed_password=get_password_hash("demo123"),
            is_active=True,
        )
        session.add(demo_user)
        await session.flush()
        print(f"Created user: {demo_user.username} (password: demo123)")

        # Create categories
        categories_data = [
            {"name": "Work", "description": "Work related tasks", "color": "#3B82F6"},
            {"name": "Personal", "description": "Personal tasks", "color": "#10B981"},
            {"name": "Shopping", "description": "Shopping list", "color": "#F59E0B"},
            {"name": "Learning", "description": "Study and learning", "color": "#8B5CF6"},
        ]

        categories = []
        for cat_data in categories_data:
            category = Category(user_id=demo_user.id, **cat_data)
            session.add(category)
            categories.append(category)
        await session.flush()
        print(f"Created {len(categories)} categories")

        # Create tags
        tags_data = [
            {"name": "urgent", "color": "#EF4444"},
            {"name": "important", "color": "#F97316"},
            {"name": "easy", "color": "#22C55E"},
            {"name": "review", "color": "#6366F1"},
            {"name": "meeting", "color": "#EC4899"},
        ]

        tags = []
        for tag_data in tags_data:
            tag = Tag(user_id=demo_user.id, **tag_data)
            session.add(tag)
            tags.append(tag)
        await session.flush()
        print(f"Created {len(tags)} tags")

        # Create tasks
        tasks_data = [
            {
                "title": "Complete project documentation",
                "description": "Write comprehensive documentation for the API endpoints and setup instructions.",
                "status": TaskStatus.IN_PROGRESS,
                "priority": TaskPriority.HIGH,
                "category": categories[0],
                "tags": [tags[1], tags[3]],
                "due_date": datetime.now() + timedelta(days=3),
            },
            {
                "title": "Review pull requests",
                "description": "Review and merge pending pull requests from team members.",
                "status": TaskStatus.PENDING,
                "priority": TaskPriority.MEDIUM,
                "category": categories[0],
                "tags": [tags[3]],
                "due_date": datetime.now() + timedelta(days=1),
            },
            {
                "title": "Weekly team meeting",
                "description": "Discuss project progress and upcoming milestones.",
                "status": TaskStatus.PENDING,
                "priority": TaskPriority.MEDIUM,
                "category": categories[0],
                "tags": [tags[4]],
                "due_date": datetime.now() + timedelta(days=2),
            },
            {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, fruits, vegetables",
                "status": TaskStatus.PENDING,
                "priority": TaskPriority.LOW,
                "category": categories[2],
                "tags": [tags[2]],
                "due_date": datetime.now() + timedelta(days=1),
            },
            {
                "title": "Learn FastAPI advanced features",
                "description": "Study dependency injection, middleware, and background tasks.",
                "status": TaskStatus.IN_PROGRESS,
                "priority": TaskPriority.MEDIUM,
                "category": categories[3],
                "tags": [tags[1]],
                "due_date": datetime.now() + timedelta(days=7),
            },
            {
                "title": "Fix login page bug",
                "description": "Users report that the login form sometimes doesn't submit.",
                "status": TaskStatus.PENDING,
                "priority": TaskPriority.URGENT,
                "category": categories[0],
                "tags": [tags[0], tags[1]],
                "due_date": datetime.now() + timedelta(hours=4),
            },
            {
                "title": "Gym workout",
                "description": "30 minutes cardio + strength training",
                "status": TaskStatus.COMPLETED,
                "priority": TaskPriority.LOW,
                "category": categories[1],
                "tags": [],
                "due_date": datetime.now() - timedelta(days=1),
            },
            {
                "title": "Read 'Clean Code' book",
                "description": "Continue reading chapter 5-7",
                "status": TaskStatus.IN_PROGRESS,
                "priority": TaskPriority.LOW,
                "category": categories[3],
                "tags": [],
                "due_date": datetime.now() + timedelta(days=14),
            },
        ]

        for task_data in tasks_data:
            task_tags = task_data.pop("tags")
            category = task_data.pop("category")
            task = Task(
                user_id=demo_user.id,
                category_id=category.id,
                **task_data
            )
            task.tags = task_tags
            session.add(task)

        await session.commit()
        print(f"Created {len(tasks_data)} tasks")

    print("\nSeed data created successfully!")
    print("\nDemo account:")
    print("  Email: demo@example.com")
    print("  Password: demo123")


if __name__ == "__main__":
    asyncio.run(seed_data())
