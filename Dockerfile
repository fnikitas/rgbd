FROM python:3.11-slim

WORKDIR /app

# Ставим системные зависимости.
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем метаданные и пакет приложения для editable-установки.
COPY pyproject.toml .
COPY app ./app

# Устанавливаем Python-зависимости.
RUN pip install --no-cache-dir -e .

# Копируем остальной проект.
COPY . .

# Открываем порт приложения.
EXPOSE 8000

# Проверка здоровья контейнера.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Запускаем API.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
