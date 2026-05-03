"""Клиент OpenRouter."""
import httpx

from app.core.config import settings


async def call_openrouter(prompt: str) -> str:
    """Запрос в OpenRouter, возвращает текст ответа."""
    url = (
        f"{settings.openrouter_base_url}/chat/completions"
    )
    headers = {
        "Authorization": (
            f"Bearer {settings.openrouter_api_key}"
        ),
        "HTTP-Referer": settings.openrouter_site_url,
        "X-Title": settings.openrouter_app_name,
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }
    async with httpx.AsyncClient(timeout=60) as cli:
        r = await cli.post(
            url, json=payload, headers=headers
        )
    if r.status_code != 200:
        raise RuntimeError(
            f"openrouter ошибка {r.status_code}: {r.text}"
        )
    data = r.json()
    return data["choices"][0]["message"]["content"]
