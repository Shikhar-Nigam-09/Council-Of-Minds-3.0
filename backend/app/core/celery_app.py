from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "council_of_minds",
    broker=settings.REDIS_URL if settings.REDIS_URL else "memory://",
    backend=settings.REDIS_URL if settings.REDIS_URL else "cache+memory://"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_always_eager=not bool(settings.REDIS_URL),
    task_eager_propagates=True,
)

# Autodiscover tasks in the app.tasks package
celery_app.autodiscover_tasks(["app.tasks"])
