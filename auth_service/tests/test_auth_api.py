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
        headers={"Authorization": "Bearer garbage"},
    )
    assert r.status_code == 401
