import pytest
import respx
from httpx import Response

from app.core.config import settings
from app.services.openrouter_client import call_openrouter


@pytest.mark.asyncio
async def test_call_openrouter_возвращает_текст():
    url = (
        f"{settings.openrouter_base_url}/chat/completions"
    )
    with respx.mock(assert_all_called=True) as mock:
        route = mock.post(url).mock(
            return_value=Response(
                200,
                json={
                    "choices": [
                        {"message": {"content": "ответ"}}
                    ]
                },
            )
        )
        text = await call_openrouter("вопрос")
        assert text == "ответ"
        assert route.called
