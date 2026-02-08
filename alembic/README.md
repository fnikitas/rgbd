# Миграции Alembic

В этом проекте Alembic отвечает за схему базы данных.

## Полезные команды

### Создать новую миграцию

```bash
alembic revision --autogenerate -m "описание_миграции"
```

### Применить все миграции

```bash
alembic upgrade head
```

### Откатить одну миграцию

```bash
alembic downgrade -1
```

### Откатить до нуля

```bash
alembic downgrade base
```

### Показать текущую ревизию

```bash
alembic current
```

### История ревизий

```bash
alembic history
```
