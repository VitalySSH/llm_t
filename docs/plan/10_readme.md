# Этап 10. README и финал

## Файлы

### `final_project_2/README.md`

```markdown
# Двухсервисная система LLM-консультаций

Учебный проект. Два независимых сервиса в одном репозитории:

- **Auth Service** (FastAPI) — регистрация, логин, выпуск JWT.
- **Bot Service** (aiogram + Celery) — Telegram-бот, который
  принимает запросы пользователя, проверяет JWT и через очередь
  RabbitMQ отправляет их в LLM (OpenRouter).

## Архитектура

```
TG user
   │
   ▼
aiogram handler ──► JWT (Redis + jose)
   │                      │
   │                      └─► отказ, если нет/невалидный
   │
   └─► llm_request.delay() ──► RabbitMQ ──► Celery worker
                                                │
                                                ├─► OpenRouter
                                                │
                                                └─► Bot.send_message
```

- JWT создаётся **только** в Auth Service.
- Bot Service токен только проверяет (общий `JWT_SECRET`).
- Запрос к LLM выполняется в Celery-воркере, не в хэндлере.
- Redis: хранит токен по ключу `token:<tg_user_id>` и работает
  как result backend Celery.

## Стек

Python 3.11, uv, FastAPI, SQLAlchemy (async, SQLite), aiogram,
Celery, RabbitMQ, Redis, httpx, python-jose, passlib (bcrypt),
pytest.

## Структура

```
final_project_2/
├── docker-compose.yml      # rabbitmq + redis
├── auth_service/           # FastAPI: /auth/register, /login, /me
└── bot_service/            # aiogram + celery + fastapi /health
```

## Установка

```bash
cd auth_service && uv sync && cd ..
cd bot_service && uv sync && cd ..
```

Заполнить `bot_service/.env`:

- `TELEGRAM_BOT_TOKEN` — токен бота от @BotFather.
- `OPENROUTER_API_KEY` — ключ OpenRouter.

`JWT_SECRET` должен быть **одинаковым** в обоих `.env`.

## Запуск

1. Инфра:
   ```bash
   docker-compose up -d
   ```
2. Auth Service:
   ```bash
   cd auth_service
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
3. Celery worker:
   ```bash
   cd bot_service
   uv run celery -A app.infra.celery_app:celery_app worker --loglevel=info
   ```
4. Telegram polling:
   ```bash
   cd bot_service
   uv run python -m app.bot.runner
   ```
5. (опционально) FastAPI bot-сервиса:
   ```bash
   cd bot_service
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8001
   ```

> При локальном запуске вне Docker замените в `bot_service/.env`
> хосты `redis` и `rabbitmq` на `localhost`.

## Сценарий пользователя

1. Открыть Swagger Auth: `http://localhost:8000/docs`.
2. `POST /auth/register` с email вида `sharonov@email.com`.
3. `POST /auth/login` (форма) → получить `access_token`.
4. В Telegram: `/token <access_token>` боту.
5. Бот сохраняет токен в Redis, отвечает «токен сохранён».
6. Любое текстовое сообщение → бот публикует задачу в RabbitMQ
   и отвечает «запрос принят, ожидайте ответа».
7. Celery-воркер получает задачу, ходит в OpenRouter и присылает
   ответ от LLM в чат.

Без токена бот отказывает в обслуживании и просит пройти
авторизацию.

## Тесты

Тесты не требуют Docker и внешних сервисов (используются
fakeredis, pytest-mock, respx).

```bash
cd auth_service && uv run pytest -v
cd bot_service && uv run pytest -v
```

## Скриншоты

Папка `docs/screenshots/`:

- `swagger_register.png` — успешная регистрация.
- `swagger_login.png` — выдача JWT.
- `swagger_me.png` — `/auth/me` с Bearer.
- `telegram_chat.png` — `/token` и переписка с ботом.
- `rabbitmq_queues.png` — интерфейс RabbitMQ
  (`http://localhost:15672`, guest/guest), активные очереди и
  consumers.
- `tests_passed.png` — зелёные `pytest` обоих сервисов.
```

## Маркеры скриншотов

Создать пустые файлы-плейсхолдеры, чтобы пользователь сразу
видел, куда класть скрины (заменит на настоящие PNG без
суффикса `.placeholder`):

```bash
cd final_project_2
touch docs/screenshots/swagger_register.png.placeholder
touch docs/screenshots/swagger_login.png.placeholder
touch docs/screenshots/swagger_me.png.placeholder
touch docs/screenshots/telegram_chat.png.placeholder
touch docs/screenshots/rabbitmq_queues.png.placeholder
touch docs/screenshots/tests_passed.png.placeholder
```

## Финальная проверка

```bash
cd auth_service && uv run pytest -v && cd ..
cd bot_service  && uv run pytest -v && cd ..
```

Оба `pytest` зелёные.

## Коммит

```bash
git add .
git commit -m "readme и финальная сборка"
```

## Чек-лист

- [ ] README заполнен
- [ ] Маркеры скриншотов созданы
- [ ] Все тесты зелёные
- [ ] Финальный коммит сделан
- [ ] **STOP. Проект готов.**
