# CLAUDE.md

Учебный проект — двухсервисная система LLM-консультаций.

## Workflow (важно)

Работа выполняется **поэтапно**. Подробности проекта и список
этапов — в `IMPLEMENTATION_PLAN.md` (короткий индекс в корне).
Детальные инструкции каждого этапа — в `docs/plan/0N_*.md`.

**Алгоритм работы:**

1. Если ещё не читал — прочитай `IMPLEMENTATION_PLAN.md` (это
   индекс, дерево репо и таблица этапов). Файлы этапов оттуда
   **не подгружай заранее**.
2. Когда пользователь говорит «начинай Этап N» / «Этап N» /
   «дальше» / «ok» — открой **только** соответствующий файл
   `docs/plan/0N_*.md` и выполни его.
3. Файлы предыдущих этапов перечитывать не нужно — их код уже
   в репозитории.
4. После выполнения этапа сделай коммит (точный текст коммита
   указан в файле этапа), напиши «Этап N завершён, жду
   подтверждения» и **остановись**.
5. Не переходи к следующему этапу без явного «ok» / «дальше».

Соответствие этапов и файлов:

| № | Файл |
|---|---|
| 1 | `docs/plan/01_skeleton.md` |
| 2 | `docs/plan/02_auth_core.md` |
| 3 | `docs/plan/03_auth_layers.md` |
| 4 | `docs/plan/04_auth_api.md` |
| 5 | `docs/plan/05_auth_tests.md` |
| 6 | `docs/plan/06_bot_core.md` |
| 7 | `docs/plan/07_bot_celery.md` |
| 8 | `docs/plan/08_bot_handlers.md` |
| 9 | `docs/plan/09_bot_tests.md` |
| 10 | `docs/plan/10_readme.md` |

## Стиль кода (важно)

Это **студенческая работа**, не корпоративный код.

- Простые функции, очевидные имена, минимум абстракций.
- Без оверинжиниринга и преждевременных оптимизаций.
- Без логирования сверх дефолтного uvicorn / celery.
- Без middleware, CORS, rate limiting, pre-commit, mypy и т.п.
- **Не выходить за рамки задания.** Если в задании есть
  формулировка «можно сделать так» — делаем (`router.py`,
  `lifespan`, `filterwarnings`). Если задание не требует —
  не делаем.

## Язык и форматирование

- Докстринги — на **русском**, краткие, **однострочные**. Без
  разделов `Args:` / `Returns:` — это видно из сигнатуры.
- Имена функций / переменных — английские, `snake_case`.
- Комментарии — на русском, только где без них непонятно.
- **Длина строки — максимум 80 символов** (для кода; в markdown
  ограничения нет).
- Коммиты — на русском, в форме «что сделано»
  (например: `auth: репозиторий и usecase`). Без emoji,
  без conventional commits, без префиксов `feat:` / `fix:`.

## Структура

```
final_project_2/
├── docker-compose.yml      # rabbitmq + redis
├── auth_service/           # FastAPI, SQLite, JWT
└── bot_service/            # aiogram + Celery + FastAPI
```

## Стек

Python 3.11, `uv`, FastAPI, SQLAlchemy (async, SQLite), aiogram,
Celery, RabbitMQ, Redis, httpx, python-jose, passlib (bcrypt),
pytest + fakeredis + respx + pytest-mock.

Email для всех примеров и тестов: `sharonov@email.com`.

## Команды

```bash
# зависимости
cd auth_service && uv sync
cd bot_service  && uv sync

# тесты (без docker и без внешних сервисов)
cd auth_service && uv run pytest -v
cd bot_service  && uv run pytest -v

# инфра
docker-compose up -d

# локальный запуск (в отдельных терминалах)
cd auth_service && uv run uvicorn app.main:app --port 8000
cd bot_service
uv run celery -A app.infra.celery_app:celery_app worker --loglevel=info
cd bot_service && uv run python -m app.bot.runner
```

## Что не трогать без явной просьбы

- Файлы `.env` — содержимое скопировано буквально из задания.
- Версии зависимостей в `pyproject.toml` — из задания, не
  обновлять.
- `IMPLEMENTATION_PLAN.md`, `CLAUDE.md`, `docs/plan/*.md` — это
  инструкции, не часть кода.
