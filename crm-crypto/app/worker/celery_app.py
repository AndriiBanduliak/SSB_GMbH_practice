"""
Celery application configuration
"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "cryptocrm_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.worker.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    'sync-all-clients-binance': {
        'task': 'app.worker.tasks.sync_all_clients',
        'schedule': settings.BINANCE_SYNC_INTERVAL * 60.0,  # Convert to seconds
        'args': ('binance',)
    },
    'sync-all-clients-coinbase': {
        'task': 'app.worker.tasks.sync_all_clients',
        'schedule': settings.COINBASE_SYNC_INTERVAL * 60.0,
        'args': ('coinbase',)
    },
    'calculate-daily-pnl': {
        'task': 'app.worker.tasks.calculate_all_clients_pnl',
        'schedule': 24 * 60 * 60.0,  # Daily at midnight
        'args': ('daily',)
    },
}

