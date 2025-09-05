"""
Celery application configuration.

Sets up Celery for background task processing.
"""

from celery import Celery

from app.config import settings

# Create Celery app
celery_app = Celery(
    "krishi_sakhi",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.jobs",
        "app.tasks.notify",
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer=settings.celery_task_serializer,
    accept_content=settings.celery_accept_content,
    result_serializer=settings.celery_result_serializer,
    timezone=settings.celery_timezone,
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Optional configuration for production
if not settings.debug:
    celery_app.conf.update(
        worker_hijack_root_logger=False,
        worker_log_color=False,
    )
