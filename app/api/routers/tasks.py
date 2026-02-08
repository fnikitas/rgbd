from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskStatusChange,
    TaskStatusHistoryResponse,
    TaskUpdate,
)
from app.services.tasks import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[str] = None,
    theme_id: Optional[UUID] = None,
    assignee_id: Optional[UUID] = None,
    created_by: Optional[UUID] = None,
    priority: Optional[int] = None,
    due_date_from: Optional[date] = None,
    due_date_to: Optional[date] = None,
    q: Optional[str] = None,
    sort: str = Query("created_at", description="Поле сортировки"),
    order: str = Query("desc", description="Порядок сортировки"),
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Получить список задач с фильтрами, сортировкой и пагинацией."""
    service = TaskService(db)
    tasks, total = await service.list_with_filters(
        status=status,
        theme_id=theme_id,
        assignee_id=assignee_id,
        created_by=created_by,
        priority=priority,
        due_date_from=due_date_from,
        due_date_to=due_date_to,
        q=q,
        sort=sort,
        order=order,
        limit=limit,
        offset=offset,
    )
    return {
        "items": tasks,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("", response_model=TaskResponse)
async def create_task(
    data: TaskCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать новую задачу."""
    service = TaskService(db)
    try:
        task = await service.create(
            title=data.title,
            created_by=current_user.id,
            description=data.description,
            priority=data.priority,
            theme_id=data.theme_id,
            assignee_id=data.assignee_id,
            due_date=data.due_date,
        )
        return task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Получить задачу по идентификатору."""
    service = TaskService(db)
    task = await service.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обновить задачу."""
    service = TaskService(db)
    task = await service.get_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )

    if task.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Редактировать можно только свои задачи",
        )

    try:
        update_data = data.model_dump(exclude_unset=True)
        updated_task = await service.update(task_id, **update_data)
        return updated_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Удалить задачу."""
    service = TaskService(db)
    task = await service.get_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )

    if task.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Удалять можно только свои задачи",
        )

    success = await service.delete(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )


# Проверка прав доступа перед сменой статуса.
@router.post("/{task_id}/status", response_model=TaskResponse)
async def change_task_status(
    task_id: UUID,
    data: TaskStatusChange,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Изменить статус задачи."""
    service = TaskService(db)
    task = await service.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )

    if task.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Менять статус можно только у своих задач",
        )

    try:
        updated_task = await service.change_status(task_id, data.to_status, current_user.id)
        return updated_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{task_id}/history", response_model=list[TaskStatusHistoryResponse])
async def get_task_history(
    task_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить историю изменения статусов задачи."""
    service = TaskService(db)
    task = await service.get_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )

    if (
        task.created_by != current_user.id
        and task.assignee_id != current_user.id
        and not current_user.is_admin
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на просмотр истории этой задачи",
        )

    return await service.get_task_history(task_id)

