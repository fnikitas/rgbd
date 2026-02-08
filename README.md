
# rgbd
Расширенные главы баз данных
=======

Task Tracker API (учебный проект)

## Что внутри

- FastAPI + async эндпоинты
- SQLAlchemy 2.0 (ORM)
- Alembic миграции
- PostgreSQL
- JWT авторизация
- Хеширование паролей через bcrypt (passlib)
- Pydantic-схемы
- Аналитика через pandas + matplotlib
- Тесты: pytest + httpx (AsyncClient)

## Быстрый запуск через Docker

1. Поднять контейнеры:

```bash
docker compose up --build
```

2. Применить миграции:

```bash
docker compose exec app alembic upgrade head
```

3. Открыть документацию:

- Swagger: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

4. Проверка, что сервис жив:

```bash
curl http://localhost:8000/health
```

## Локальный запуск (без Docker)

1. Создать и активировать виртуальное окружение.

2. Установить зависимости:

```bash
pip install -e .
```

3. Создать `.env` из примера:

```bash
cp .env.example .env
```

4. Запустить миграции:

```bash
alembic upgrade head
```

5. Старт приложения:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Основные эндпоинты

- `POST /auth/register` — регистрация
- `POST /auth/login` — вход и JWT
- `GET /auth/me` — текущий пользователь
- `GET /tasks` — список задач с фильтрами
- `POST /tasks` — создать задачу
- `PATCH /tasks/{task_id}` — обновить задачу
- `DELETE /tasks/{task_id}` — удалить задачу
- `POST /tasks/{task_id}/status` — сменить статус
- `GET /tasks/{task_id}/history` — история статусов
- `GET /analytics/summary` — сводная аналитика
- `GET /analytics/plot/statuses.png` — PNG-график

## Примеры curl

### Регистрация

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user",
    "password": "password123"
  }'
```

### Логин

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Создать задачу

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Сделать лабораторную",
    "description": "Нужен CRUD и аналитика",
    "priority": 4
  }'
```

### Список задач с фильтрами и сортировкой

```bash
curl "http://localhost:8000/tasks?status=new&priority=4&sort=due_date&order=asc&limit=20&offset=0"
```

### Смена статуса

```bash
curl -X POST http://localhost:8000/tasks/<TASK_ID>/status \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "to_status": "in_progress"
  }'
```

### Сводная аналитика

```bash
curl http://localhost:8000/analytics/summary
```

### График статусов

```bash
curl http://localhost:8000/analytics/plot/statuses.png --output statuses.png
```

## Тесты

Запуск всех тестов:

```bash
pytest
```

Запуск конкретного файла:

```bash
pytest tests/test_tasks.py -v
```

## Структура проекта

```text
app/
  main.py
  core/
  db/
  models/
  schemas/
  repositories/
  services/
  api/routers/
  analytics/
alembic/
tests/
Dockerfile
docker-compose.yml
pyproject.toml
README.md
.env.example
```

(Федоров Н.С. Вариант 1 (Трекер задач))
