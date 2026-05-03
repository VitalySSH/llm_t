from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "bot_service",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
)

# регистрация задач (импорт в конце во избежание цикла)
from app.tasks import llm_tasks  # noqa: E402, F401
