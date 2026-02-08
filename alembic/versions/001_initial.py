"""Initial migration - create all tables

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    op.create_table(
        'themes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(1024), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_themes_name'),
    )
    op.create_index('ix_themes_name', 'themes', ['name'], unique=True)
    
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.String(2000), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='new'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('theme_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('assignee_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['theme_id'], ['themes.id'], ),
        sa.ForeignKeyConstraint(['assignee_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("status IN ('new', 'in_progress', 'done', 'blocked', 'canceled')", name='check_task_status'),
        sa.CheckConstraint('priority >= 1 AND priority <= 5', name='check_task_priority'),
    )
    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_assignee_id', 'tasks', ['assignee_id'])
    op.create_index('idx_tasks_theme_id', 'tasks', ['theme_id'])
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'])
    op.create_index('idx_tasks_status_assignee_id', 'tasks', ['status', 'assignee_id'])
    
    op.create_table(
        'task_status_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('from_status', sa.String(20), nullable=False),
        sa.Column('to_status', sa.String(20), nullable=False),
        sa.Column('changed_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('changed_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_history_task_id', 'task_status_history', ['task_id'])


def downgrade() -> None:
    op.drop_index('idx_history_task_id', table_name='task_status_history')
    op.drop_table('task_status_history')
    
    op.drop_index('idx_tasks_status_assignee_id', table_name='tasks')
    op.drop_index('idx_tasks_due_date', table_name='tasks')
    op.drop_index('idx_tasks_theme_id', table_name='tasks')
    op.drop_index('idx_tasks_assignee_id', table_name='tasks')
    op.drop_index('idx_tasks_status', table_name='tasks')
    op.drop_table('tasks')
    
    op.drop_index('ix_themes_name', table_name='themes')
    op.drop_table('themes')
    
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
