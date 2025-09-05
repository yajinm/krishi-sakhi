"""
Celery Beat schedules for periodic tasks.

Defines scheduled tasks for data sync, advisory generation, and maintenance.
"""

from celery.schedules import crontab
from app.tasks.celery_app import celery_app

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    # Weather data sync - every hour
    'sync-weather-data': {
        'task': 'app.tasks.jobs.sync_weather_data',
        'schedule': crontab(minute=0),  # Every hour
    },
    
    # Pest data sync - every 6 hours
    'sync-pest-data': {
        'task': 'app.tasks.jobs.sync_pest_data',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    
    # Price data sync - every 4 hours
    'sync-price-data': {
        'task': 'app.tasks.jobs.sync_price_data',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
    },
    
    # Knowledge base processing - daily at 2 AM
    'process-knowledge-base': {
        'task': 'app.tasks.jobs.process_knowledge_base',
        'schedule': crontab(minute=0, hour=2),  # Daily at 2 AM
    },
    
    # Advisory generation - every 30 minutes
    'generate-advisories': {
        'task': 'app.tasks.jobs.generate_advisories_for_farmer',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'args': ('all',),  # Generate for all farmers
    },
}

# Set timezone for beat schedule
celery_app.conf.timezone = 'Asia/Kolkata'
