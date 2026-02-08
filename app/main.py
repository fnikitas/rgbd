import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import analytics, auth, tasks, themes, users
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("task_tracker")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(themes.router)
app.include_router(tasks.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("API трекера задач запущен")


@app.get("/", tags=["root"])
async def root():
    """Корневой эндпоинт."""
    return {
        "message": "Добро пожаловать в API трекера задач",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Проверка состояния сервиса."""
    return {"status": "ок"}
