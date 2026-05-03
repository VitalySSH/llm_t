# Двухсервисная система LLM-консультаций

Два независимых сервиса в одном репозитории:

- **Auth Service** (FastAPI) — регистрация, логин, выпуск JWT.
- **Bot Service** (aiogram + Celery) — Telegram-бот, который
  принимает запросы пользователя, проверяет JWT и через очередь
  RabbitMQ отправляет их в LLM (OpenRouter).

## Архитектура
- JWT создаётся **только** в Auth Service.
- Bot Service токен только проверяет (общий `JWT_SECRET`).
- Запрос к LLM выполняется в Celery-воркере, не в хэндлере.
- Redis: хранит токен по ключу `token:<tg_user_id>` и работает
  как result backend Celery.

## Стек

Python 3.13, uv, FastAPI, SQLAlchemy (async, SQLite), aiogram,
Celery, RabbitMQ, Redis, httpx, python-jose, passlib (bcrypt),
pytest.

## Структура

```
final_project_2/
├── docker-compose.yml      # вся система: инфра + сервисы
├── auth_service/           # FastAPI: /auth/register, /login, /me
└── bot_service/            # aiogram + celery + fastapi /health
```

## Установка

Заполнить `bot_service/.env`:

- `TELEGRAM_BOT_TOKEN` — токен бота от @BotFather.
- `OPENROUTER_API_KEY` — ключ OpenRouter.

`JWT_SECRET` должен быть одинаковым в обоих `.env`.

Зависимости подтягиваются внутри docker-образов автоматически.
Для локального запуска тестов также нужен `uv sync` в каждом
сервисе:

```bash
cd auth_service && uv sync && cd ..
cd bot_service  && uv sync && cd ..
```

## Запуск

Все сервисы поднимаются одной командой из корня репозитория:

```bash
docker compose up -d --build
```

Поднимается 6 контейнеров:

- `rabbitmq` — брокер Celery (5672, веб-интерфейс на 15672)
- `redis` — backend Celery и хранилище токенов (6379)
- `auth` — Auth Service на `http://localhost:8000`
- `bot-api` — FastAPI бот-сервиса на `http://localhost:8001`
- `bot-worker` — Celery-воркер с задачей `llm_request`
- `bot-polling` — aiogram polling
```

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

Без токена бот отказывает в обработке запроса и просит пройти
авторизацию.

## Тесты

Тесты не требуют Docker и внешних сервисов (используются
fakeredis, pytest-mock, respx).

```bash
cd auth_service && uv run pytest -v
cd bot_service && uv run pytest -v
```

## Скриншоты

### Регистрация пользователя

![Регистрация](https://github.com/VitalySSH/llm_t/blob/main/docs/screenshots/swagger_register.png)

### Выдача JWT

![Выдача JWT](https://github.com/VitalySSH/llm_t/blob/main/docs/screenshots/swagger_login.png)

### Профиль по токену (`/auth/me`)

![Профиль по токену](https://github.com/VitalySSH/llm_t/blob/main/docs/screenshots/swagger_me.png)

### Переписка с Telegram-ботом

![Чат с ботом](https://github.com/VitalySSH/llm_t/blob/main/docs/screenshots/telegram_chat.png)

### Очередь RabbitMQ

![Интерфейс RabbitMQ](https://github.com/VitalySSH/llm_t/blob/main/docs/screenshots/rabbitmq_queues.png)

### Тесты Auth Service

![Тесты сервиса авторизации](https://github.com/VitalySSH/llm_t/blob/main/docs/screenshots/auth_service_tests.png)

### Тесты Bot Service

![Тесты бота](https://github.com/VitalySSH/llm_t/blob/main/docs/screenshots/bot_service_tests.png)
