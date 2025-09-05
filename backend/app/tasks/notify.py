"""
Notification tasks for sending alerts and reminders.

Provides Celery tasks for sending notifications via various channels.
"""

from app.tasks.celery_app import celery_app
from app.providers import get_notification_provider


@celery_app.task
def send_sms_notification(phone: str, message: str):
    """Send SMS notification."""
    try:
        provider = get_notification_provider()
        result = provider.send_sms(phone, message)
        
        return {
            'status': 'completed',
            'channel': 'sms',
            'recipient': phone,
            'result': result,
        }
        
    except Exception as exc:
        return {
            'status': 'failed',
            'channel': 'sms',
            'recipient': phone,
            'error': str(exc),
        }


@celery_app.task
def send_whatsapp_notification(phone: str, message: str):
    """Send WhatsApp notification."""
    try:
        provider = get_notification_provider()
        result = provider.send_whatsapp(phone, message)
        
        return {
            'status': 'completed',
            'channel': 'whatsapp',
            'recipient': phone,
            'result': result,
        }
        
    except Exception as exc:
        return {
            'status': 'failed',
            'channel': 'whatsapp',
            'recipient': phone,
            'error': str(exc),
        }


@celery_app.task
def send_push_notification(device_id: str, title: str, message: str):
    """Send push notification."""
    try:
        provider = get_notification_provider()
        result = provider.send_push(device_id, title, message)
        
        return {
            'status': 'completed',
            'channel': 'push',
            'recipient': device_id,
            'result': result,
        }
        
    except Exception as exc:
        return {
            'status': 'failed',
            'channel': 'push',
            'recipient': device_id,
            'error': str(exc),
        }


@celery_app.task
def send_email_notification(email: str, subject: str, message: str):
    """Send email notification."""
    try:
        provider = get_notification_provider()
        result = provider.send_email(email, subject, message)
        
        return {
            'status': 'completed',
            'channel': 'email',
            'recipient': email,
            'result': result,
        }
        
    except Exception as exc:
        return {
            'status': 'failed',
            'channel': 'email',
            'recipient': email,
            'error': str(exc),
        }


@celery_app.task
def send_bulk_notifications(notifications: list):
    """Send bulk notifications."""
    results = []
    
    for notification in notifications:
        channel = notification.get('channel')
        recipient = notification.get('recipient')
        message = notification.get('message')
        title = notification.get('title', '')
        
        if channel == 'sms':
            result = send_sms_notification.delay(recipient, message)
        elif channel == 'whatsapp':
            result = send_whatsapp_notification.delay(recipient, message)
        elif channel == 'push':
            result = send_push_notification.delay(recipient, title, message)
        elif channel == 'email':
            result = send_email_notification.delay(recipient, title, message)
        else:
            result = {'status': 'failed', 'error': 'Unknown channel'}
        
        results.append(result)
    
    return {
        'status': 'completed',
        'total_notifications': len(notifications),
        'results': results,
    }
