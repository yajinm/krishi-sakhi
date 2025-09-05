"""
Notification providers.

Provides interfaces for sending notifications via various channels.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional

from app.config import settings


class NotificationProvider(ABC):
    """Abstract base class for notification providers."""
    
    @abstractmethod
    async def send_sms(self, phone: str, message: str) -> Dict[str, any]:
        """Send SMS notification."""
        pass
    
    @abstractmethod
    async def send_whatsapp(self, phone: str, message: str) -> Dict[str, any]:
        """Send WhatsApp notification."""
        pass
    
    @abstractmethod
    async def send_push(self, device_id: str, title: str, message: str) -> Dict[str, any]:
        """Send push notification."""
        pass
    
    @abstractmethod
    async def send_email(self, email: str, subject: str, message: str) -> Dict[str, any]:
        """Send email notification."""
        pass


class ConsoleNotificationProvider(NotificationProvider):
    """Console notification provider for development."""
    
    async def send_sms(self, phone: str, message: str) -> Dict[str, any]:
        """Send SMS to console."""
        print(f"📱 SMS to {phone}: {message}")
        return {"status": "sent", "provider": "console"}
    
    async def send_whatsapp(self, phone: str, message: str) -> Dict[str, any]:
        """Send WhatsApp to console."""
        print(f"💬 WhatsApp to {phone}: {message}")
        return {"status": "sent", "provider": "console"}
    
    async def send_push(self, device_id: str, title: str, message: str) -> Dict[str, any]:
        """Send push notification to console."""
        print(f"🔔 Push to {device_id}: {title} - {message}")
        return {"status": "sent", "provider": "console"}
    
    async def send_email(self, email: str, subject: str, message: str) -> Dict[str, any]:
        """Send email to console."""
        print(f"📧 Email to {email}: {subject} - {message}")
        return {"status": "sent", "provider": "console"}


class TwilioNotificationProvider(NotificationProvider):
    """Twilio notification provider."""
    
    def __init__(self):
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.phone_number = settings.twilio_phone_number
    
    async def send_sms(self, phone: str, message: str) -> Dict[str, any]:
        """Send SMS via Twilio."""
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            # Fallback to console
            console_provider = ConsoleNotificationProvider()
            return await console_provider.send_sms(phone, message)
        
        try:
            from twilio.rest import Client
            
            client = Client(self.account_sid, self.auth_token)
            
            message_obj = client.messages.create(
                body=message,
                from_=self.phone_number,
                to=phone
            )
            
            return {
                "status": "sent",
                "provider": "twilio",
                "message_id": message_obj.sid,
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "provider": "twilio",
                "error": str(e),
            }
    
    async def send_whatsapp(self, phone: str, message: str) -> Dict[str, any]:
        """Send WhatsApp via Twilio."""
        if not all([self.account_sid, self.auth_token]):
            # Fallback to console
            console_provider = ConsoleNotificationProvider()
            return await console_provider.send_whatsapp(phone, message)
        
        try:
            from twilio.rest import Client
            
            client = Client(self.account_sid, self.auth_token)
            
            # WhatsApp format: whatsapp:+1234567890
            whatsapp_phone = f"whatsapp:{phone}"
            whatsapp_from = f"whatsapp:{self.phone_number}"
            
            message_obj = client.messages.create(
                body=message,
                from_=whatsapp_from,
                to=whatsapp_phone
            )
            
            return {
                "status": "sent",
                "provider": "twilio_whatsapp",
                "message_id": message_obj.sid,
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "provider": "twilio_whatsapp",
                "error": str(e),
            }
    
    async def send_push(self, device_id: str, title: str, message: str) -> Dict[str, any]:
        """Send push notification (not supported by Twilio)."""
        # Fallback to console
        console_provider = ConsoleNotificationProvider()
        return await console_provider.send_push(device_id, title, message)
    
    async def send_email(self, email: str, subject: str, message: str) -> Dict[str, any]:
        """Send email (not supported by Twilio)."""
        # Fallback to console
        console_provider = ConsoleNotificationProvider()
        return await console_provider.send_email(email, subject, message)


def get_notification_provider() -> NotificationProvider:
    """Get notification provider based on configuration."""
    if settings.twilio_account_sid and settings.twilio_auth_token:
        return TwilioNotificationProvider()
    else:
        return ConsoleNotificationProvider()
