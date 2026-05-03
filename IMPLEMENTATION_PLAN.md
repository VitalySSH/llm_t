# IMPLEMENTATION_PLAN

Короткий индекс. Подробности каждого этапа — в отдельных файлах
в `docs/plan/`.

## Как работать

1. Перед началом работы прочитай `CLAUDE.md` (правила и стиль) и
   этот файл (контекст и дерево).
2. На каждом этапе читай **только** соответствующий файл из
   `docs/plan/`. Файлы предыдущих этапов перечитывать не нужно —
   их результаты уже в коде.
3. После завершения этапа сделай коммит, напиши «Этап N завершён,
   жду подтверждения» и **остановись**. Жди от пользователя «ok»
   или «дальше».

## Архитектура

Два независимых сервиса в одном репозитории.

**Auth Service** (FastAPI, порт 8000) — регистрация, логин,
выпуск JWT. SQLite + bcrypt + python-jose.

**Bot Service** (aiogram + FastAPI + Celery) — три процесса:
1. FastAPI (порт 8001, только `/health`).
2. aiogram polling — обработка сообщений Telegram.
3. Celery worker — обработка задач `llm_request`.

Поток:

```
TG user → aiogram handler → проверка JWT (Redis + jose)
       → llm_request.delay() → RabbitMQ → Celery worker
       → OpenRouter → Bot.send_message обратно в TG
```

JWT создаётся **только** в Auth Service, Bot Service токен
проверяет общим `JWT_SECRET`. Запрос к LLM — в воркере, не в
хэндлере.

## Дерево репозитория (целевое состояние)

```
final_project_2/
├── .gitignore
├── README.md
├── CLAUDE.md
├── IMPLEMENTATION_PLAN.md
├── docker-compose.yml
├── docs/
│   ├── plan/
│   │   ├── 01_skeleton.md
│   │   ├── 02_auth_core.md
│   │   ├── 03_auth_layers.md
│   │   ├── 04_auth_api.md
│   │   ├── 05_auth_tests.md
│   │   ├── 06_bot_core.md
│   │   ├── 07_bot_celery.md
│   │   ├── 08_bot_handlers.md
│   │   ├── 09_bot_tests.md
│   │   └── 10_readme.md
│   └── screenshots/
├── auth_service/
│   ├── pyproject.toml
│   ├── pytest.ini
│   ├── .env
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── exceptions.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── models.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── user.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   └── users.py
│   │   ├── usecases/
│   │   │   ├── __init__.py
│   │   │   └── auth.py
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── deps.py
│   │       ├── router.py
│   │       └── routes_auth.py
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_security.py
│       └── test_auth_api.py
└── bot_service/
    ├── pyproject.toml
    ├── pytest.ini
    ├── .env
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── config.py
    │   │   └── jwt.py
    │   ├── infra/
    │   │   ├── __init__.py
    │   │   ├── redis.py
    │   │   └── celery_app.py
    │   ├── tasks/
    │   │   ├── __init__.py
    │   │   └── llm_tasks.py
    │   ├── services/
    │   │   ├── __init__.py
    │   │   └── openrouter_client.py
    │   └── bot/
    │       ├── __init__.py
    │       ├── dispatcher.py
    │       ├── handlers.py
    │       └── runner.py
    └── tests/
        ├── __init__.py
        ├── conftest.py
        ├── test_jwt.py
        ├── test_handlers.py
        └── test_openrouter.py
```

## Этапы

| № | Файл | Что делается |
|---|---|---|
| 1 | `docs/plan/01_skeleton.md` | Скелет репо, docker-compose, оба пакета, `uv sync` |
| 2 | `docs/plan/02_auth_core.md` | Auth: config, security, exceptions, db |
| 3 | `docs/plan/03_auth_layers.md` | Auth: schemas, repository, usecase |
| 4 | `docs/plan/04_auth_api.md` | Auth: deps, routes, router, main |
| 5 | `docs/plan/05_auth_tests.md` | Auth: unit и интеграционные тесты |
| 6 | `docs/plan/06_bot_core.md` | Bot: config, jwt, infra (redis, celery), main |
| 7 | `docs/plan/07_bot_celery.md` | Bot: OpenRouter клиент, Celery-задача |
| 8 | `docs/plan/08_bot_handlers.md` | Bot: aiogram dispatcher, handlers, runner |
| 9 | `docs/plan/09_bot_tests.md` | Bot: тесты jwt, handlers, openrouter |
| 10 | `docs/plan/10_readme.md` | README, маркеры скриншотов, финал |

Email во всех примерах и тестах: `sharonov@email.com`.

## Соответствие критериям оценки

| Критерий задания | Где реализовано |
|---|---|
| Разделение на два сервиса | `auth_service/` и `bot_service/` |
| Auth: регистрация, хеш пароля | `usecases/auth.py` + `core/security.py` |
| Auth: логин с JWT | `usecases/auth.py` |
| JWT поля sub, role, iat, exp | `core/security.py::create_access_token` |
| `/auth/me` по Bearer | `routes_auth.py` + `deps.py` |
| Свои HTTP-исключения | `core/exceptions.py` |
| OAuth2PasswordRequestForm | `routes_auth.py::login` |
| Bot: только проверка JWT | `core/jwt.py::decode_and_validate` |
| JWT в Redis по `tg_user_id` | `bot/handlers.py::cmd_token` |
| Отказ без токена | `bot/handlers.py::on_text` |
| LLM не в хэндлере | `tasks/llm_tasks.py` |
| RabbitMQ broker | `infra/celery_app.py` |
| Redis backend + хранилище | `infra/celery_app.py` + `infra/redis.py` |
| Unit-тесты Auth | `tests/test_security.py` |
| Интеграционные тесты Auth | `tests/test_auth_api.py` |
| Unit-тесты Bot (JWT) | `tests/test_jwt.py` |
| Mock-тесты handlers | `tests/test_handlers.py` |
| respx для OpenRouter | `tests/test_openrouter.py` |
| Тесты без реального Redis/RabbitMQ | fakeredis + mocker |
| README с архитектурой | `README.md` |
| Email `surname@email.com` | `sharonov@email.com` |
| Скриншоты | `docs/screenshots/` |
