# Этап 5. Auth Service: тесты

## Файлы

### `auth_service/tests/conftest.py`

```python
"""Фикстуры для тестов auth-сервиса."""
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.api.deps import get_db
from app.db.base import Base
from app.main import app


@pytest_asyncio.fixture
async def client():
    """HTTP-клиент с in-memory SQLite."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:"
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
    await engine.dispose()
```

### `auth_service/tests/test_security.py`

```python
"""Тесты модуля security."""
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_хеш_не_равен_паролю():
    h = hash_password("secret123")
    assert h != "secret123"


def test_верный_пароль_проходит():
    h = hash_password("secret123")
    assert verify_password("secret123", h) is True


def test_неверный_пароль_не_проходит():
    h = hash_password("secret123")
    assert verify_password("wrong", h) is False


def test_jwt_содержит_все_поля():
    token = create_access_token(sub="42", role="user")
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "user"
    assert "iat" in payload
    assert "exp" in payload
```

### `auth_service/tests/test_auth_api.py`

```python
"""Интеграционные тесты auth-эндпоинтов."""
import pytest

EMAIL = "sharonov@email.com"
PASSWORD = "qwerty12"


@pytest.mark.asyncio
async def test_полный_сценарий(client):
    # регистрация
    r = await client.post(
        "/auth/register",
        json={"email": EMAIL, "password": PASSWORD},
    )
    assert r.status_code == 201
    assert r.json()["email"] == EMAIL

    # логин (форма OAuth2)
    r = await client.post(
        "/auth/login",
        data={"username": EMAIL, "password": PASSWORD},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token

    # профиль
    r = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["email"] == EMAIL


@pytest.mark.asyncio
async def test_дубль_регистрации_409(client):
    data = {"email": EMAIL, "password": PASSWORD}
    await client.post("/auth/register", json=data)
    r = await client.post("/auth/register", json=data)
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_неверный_пароль_401(client):
    await client.post(
        "/auth/register",
        json={"email": EMAIL, "password": PASSWORD},
    )
    r = await client.post(
        "/auth/login",
        data={"username": EMAIL, "password": "wrong"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_me_без_токена_401(client):
    r = await client.get("/auth/me")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_me_неверный_токен_401(client):
    r = await client.get(
        "/auth/me",
        headers={"Authorization": "Bearer мусор"},
    )
    assert r.status_code == 401
```

## Запуск

```bash
cd auth_service
uv run pytest -v
```

Все тесты должны быть зелёными.

## Коммит

```bash
git add auth_service
git commit -m "auth: тесты unit и интеграционные"
```

## Чек-лист

- [ ] 3 файла созданы (conftest + 2 test_*)
- [ ] `pytest -v` зелёный
- [ ] Коммит сделан
- [ ] **STOP**
