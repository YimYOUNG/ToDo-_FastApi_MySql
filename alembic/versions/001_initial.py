"""initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', mysql.CHAR(36), primary_key=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table('tags',
        sa.Column('id', mysql.CHAR(36), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('color', sa.String(7), default='#3498db'),
        sa.Column('user_id', mysql.CHAR(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )
    op.create_index('ix_tags_user_id', 'tags', ['user_id'])

    op.create_table('todos',
        sa.Column('id', mysql.CHAR(36), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', name='priorityenum'), default='medium'),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'cancelled', name='todostatus'), default='pending'),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('user_id', mysql.CHAR(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_todos_user_id', 'todos', ['user_id'])

    op.create_table('subtasks',
        sa.Column('id', mysql.CHAR(36), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('is_completed', sa.Boolean(), default=False),
        sa.Column('todo_id', mysql.CHAR(36), sa.ForeignKey('todos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )
    op.create_index('ix_subtasks_todo_id', 'subtasks', ['todo_id'])

    op.create_table('todo_tags',
        sa.Column('todo_id', mysql.CHAR(36), sa.ForeignKey('todos.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tag_id', mysql.CHAR(36), sa.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    )

    op.create_table('todo_shares',
        sa.Column('id', mysql.CHAR(36), primary_key=True),
        sa.Column('todo_id', mysql.CHAR(36), sa.ForeignKey('todos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('shared_with_id', mysql.CHAR(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('shared_by_id', mysql.CHAR(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('permission', sa.String(20), default='read'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )

    op.create_table('reminders',
        sa.Column('id', mysql.CHAR(36), primary_key=True),
        sa.Column('todo_id', mysql.CHAR(36), sa.ForeignKey('todos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('remind_time', sa.DateTime(), nullable=False),
        sa.Column('method', sa.String(20), default='browser'),
        sa.Column('is_sent', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('reminders')
    op.drop_table('todo_shares')
    op.drop_table('todo_tags')
    op.drop_table('subtasks')
    op.drop_table('todos')
    op.drop_table('tags')
    op.drop_table('users')
