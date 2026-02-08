from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.schemas.theme import ThemeCreate, ThemeResponse, ThemeUpdate
from app.services.themes import ThemeService

router = APIRouter(prefix="/themes", tags=["themes"])


@router.get("", response_model=list[ThemeResponse])
async def list_themes(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Получить список тем."""
    service = ThemeService(db)
    themes, _ = await service.list_all(limit, offset)
    return themes


@router.post("", response_model=ThemeResponse)
async def create_theme(
    data: ThemeCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать новую тему (только для админа)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Тему может создать только админ",
        )

    service = ThemeService(db)
    try:
        theme = await service.create(data.name, data.description)
        return theme
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{theme_id}", response_model=ThemeResponse)
async def get_theme(
    theme_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Получить тему по идентификатору."""
    service = ThemeService(db)
    theme = await service.get_by_id(theme_id)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тема не найдена",
        )
    return theme


@router.patch("/{theme_id}", response_model=ThemeResponse)
async def update_theme(
    theme_id: UUID,
    data: ThemeUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обновить тему (только для админа)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Тему может изменить только админ",
        )

    service = ThemeService(db)
    try:
        theme = await service.update(theme_id, data.name, data.description)
        if not theme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тема не найдена",
            )
        return theme
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{theme_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_theme(
    theme_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Удалить тему (только для админа)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Тему может удалить только админ",
        )

    service = ThemeService(db)
    success = await service.delete(theme_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тема не найдена",
        )

