import fakeredis.aioredis
import pytest_asyncio


@pytest_asyncio.fixture
async def fake_redis(monkeypatch):
    """Подменяет get_redis в handlers на fakeredis."""
    r = fakeredis.aioredis.FakeRedis(
        decode_responses=True
    )
    from app.bot import handlers
    monkeypatch.setattr(
        handlers, "get_redis", lambda: r
    )
    yield r
    await r.aclose()
