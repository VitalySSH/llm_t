# Этап 1. Скелет репозитория и docker-compose

## Что делаем

1. Создаём папку `final_project_2`, делаем `git init -b main`.
2. Кладём в корень `IMPLEMENTATION_PLAN.md` и `CLAUDE.md` (оба
   файла пользователь предоставил отдельно).
3. Создаём корневые файлы: `.gitignore`, `README.md` (заглушка),
   `docker-compose.yml`.
4. Создаём `docs/screenshots/.gitkeep` (чтобы папка попала в git).
5. Создаём всю структуру `auth_service/` и `bot_service/`:
   `pyproject.toml`, `pytest.ini`, `.env`, пустые `__init__.py`
   во всех пакетах.
6. В каждом сервисе: `uv sync`.
7. Коммит.

## Файлы

### `final_project_2/.gitignore`

```gitignore
# python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
.pytest_cache/

# окружение и бд
*.db

# ide и os
.idea/
.vscode/
.DS_Store
```

### `final_project_2/README.md` (заглушка)

```markdown
# Двухсервисная система LLM-консультаций

Учебный проект. Подробное описание появится на финальном этапе.
```

### `final_project_2/docker-compose.yml`

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

> Только инфра. Auth/Bot/Celery запускаются локально через `uv run`.

### `final_project_2/docs/screenshots/.gitkeep`

Пустой файл.

---

### `auth_service/pyproject.toml`

Содержимое **буквально из задания**:

```toml
[project]
name = "auth-service"
version = "0.1.0"
description = "Auth service: registration + JWT issuing"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.112.0",
  "uvicorn[standard]>=0.30.0",
  "sqlalchemy>=2.0.30",
  "aiosqlite>=0.20.0",
  "pydantic[email]>=2.7.0",
  "pydantic-settings>=2.3.0",
  "python-jose[cryptography]>=3.3.0",
  "passlib[bcrypt]>=1.7.4",
  "python-multipart>=0.0.9",
  "ruff>=0.14.0",
  "greenlet>=3.3.1",
  "bcrypt==4.3.0",
  "pytest>=8.0.0",
  "pytest-asyncio>=0.23.0",
  "httpx>=0.27.0",
  "respx>=0.21.0",
]

[tool.uv]
dev-dependencies = []
```

### `auth_service/.env`

Буквально из задания:

```dotenv
APP_NAME=auth-service
ENV=local
JWT_SECRET=change_me_super_secret
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
SQLITE_PATH=./auth.db
```

### `auth_service/pytest.ini`

```ini
[pytest]
pythonpath = .
asyncio_mode = auto
filterwarnings =
    ignore::DeprecationWarning
```

### Пустые `__init__.py` в `auth_service/`

В директориях:
- `app/`
- `app/core/`
- `app/db/`
- `app/schemas/`
- `app/repositories/`
- `app/usecases/`
- `app/api/`
- `tests/`

---

### `bot_service/pyproject.toml`

Содержимое **буквально из задания**:

```toml
[project]
name = "bot-service"
version = "0.1.0"
description = "Telegram bot service with JWT auth, Celery, RabbitMQ, Redis, OpenRouter"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.112.0",
  "uvicorn[standard]>=0.30.0",
  "aiogram>=3.10.0",
  "sqlalchemy>=2.0.30",
  "celery>=5.4.0",
  "redis>=5.0.0",
  "httpx>=0.27.0",
  "pydantic-settings>=2.3.0",
  "python-jose[cryptography]>=3.3.0",
  "ruff>=0.14.0",
  "pytest>=8.0.0",
  "pytest-asyncio>=0.23.0",
  "pytest-mock>=3.12.0",
  "httpx>=0.27.0",
  "respx>=0.21.0",
  "fakeredis>=2.23.0",
]

[tool.uv]
dev-dependencies = []
```

### `bot_service/.env`

Буквально из задания:

```dotenv
APP_NAME=bot-service
ENV=local
TELEGRAM_BOT_TOKEN=
JWT_SECRET=change_me_super_secret
JWT_ALG=HS256
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672//
OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=stepfun/step-3.5-flash:free
OPENROUTER_SITE_URL=https://example.com
OPENROUTER_APP_NAME=bot-service
```

### `bot_service/pytest.ini`

```ini
[pytest]
pythonpath = .
asyncio_mode = auto
filterwarnings =
    ignore::DeprecationWarning
```

### Пустые `__init__.py` в `bot_service/`

В директориях:
- `app/`
- `app/core/`
- `app/infra/`
- `app/tasks/`
- `app/services/`
- `app/bot/`
- `tests/`

## Команды

```bash
cd /home/vitaly-dev/edu/mifi/python/02
mkdir final_project_2
cd final_project_2
git init -b main

# создать все файлы (см. выше)

cd auth_service && uv sync && cd ..
cd bot_service && uv sync && cd ..

git add .
git commit -m "скелет проекта: два сервиса, docker-compose"
```

## Чек-лист

- [ ] `IMPLEMENTATION_PLAN.md` и `CLAUDE.md` в корне
- [ ] Дерево совпадает с целевой структурой из `IMPLEMENTATION_PLAN.md`
- [ ] `uv sync` отработал в обоих сервисах
- [ ] Коммит создан
- [ ] **STOP — жду подтверждения**
