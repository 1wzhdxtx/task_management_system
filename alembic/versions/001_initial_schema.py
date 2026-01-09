"""Initial schema - create all tables

Revision ID: 001_initial
Revises:
Create Date: 2024-01-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(50), nullable=False, comment='用户名'),
        sa.Column('email', sa.String(100), nullable=False, comment='邮箱'),
        sa.Column('hashed_password', sa.String(255), nullable=False, comment='加密后的密码'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True, comment='是否激活'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(50), nullable=False, comment='分类名称'),
        sa.Column('description', sa.String(200), nullable=True, default='', comment='分类描述'),
        sa.Column('color', sa.String(7), nullable=False, default='#3B82F6', comment='显示颜色'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='所属用户ID'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name', name='uk_user_category')
    )
    op.create_index('ix_categories_user_id', 'categories', ['user_id'])

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(30), nullable=False, comment='标签名称'),
        sa.Column('color', sa.String(7), nullable=False, default='#10B981', comment='显示颜色'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='所属用户ID'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name', name='uk_user_tag')
    )
    op.create_index('ix_tags_user_id', 'tags', ['user_id'])

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(200), nullable=False, comment='任务标题'),
        sa.Column('description', sa.Text(), nullable=True, comment='任务描述'),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'archived', name='taskstatus'),
                  nullable=False, default='pending', comment='任务状态'),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent', name='taskpriority'),
                  nullable=False, default='medium', comment='优先级'),
        sa.Column('due_date', sa.DateTime(), nullable=True, comment='截止日期'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='所属用户ID'),
        sa.Column('category_id', sa.Integer(), nullable=True, comment='分类ID'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('ix_tasks_status', 'tasks', ['status'])
    op.create_index('ix_tasks_due_date', 'tasks', ['due_date'])

    # Create task_tags association table
    op.create_table(
        'task_tags',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'tag_id')
    )


def downgrade() -> None:
    op.drop_table('task_tags')
    op.drop_table('tasks')
    op.drop_index('ix_tags_user_id', table_name='tags')
    op.drop_table('tags')
    op.drop_index('ix_categories_user_id', table_name='categories')
    op.drop_table('categories')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')

    # Drop enums (MySQL doesn't need this, but good practice)
    op.execute("DROP TYPE IF EXISTS taskstatus")
    op.execute("DROP TYPE IF EXISTS taskpriority")
