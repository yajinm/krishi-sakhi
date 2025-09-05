"""
OTP (One-Time Password) utilities.

Handles OTP generation, verification, and storage for phone-based authentication.
"""

import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional

import redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import AsyncSessionLocal
from app.models import User

# Redis client for OTP storage
redis_client = redis.from_url(settings.redis_url)


class OTPManager:
    """Manages OTP generation, storage, and verification."""
    
    def __init__(self):
        self.redis_client = redis_client
        self.otp_expire_minutes = settings.otp_expire_minutes
        self.otp_max_attempts = settings.otp_max_attempts
        self.dev_code = settings.otp_dev_code
    
    def _get_otp_key(self, phone: str) -> str:
        """Get Redis key for OTP storage."""
        return f"otp:{phone}"
    
    def _get_attempts_key(self, phone: str) -> str:
        """Get Redis key for attempt tracking."""
        return f"otp_attempts:{phone}"
    
    def _get_lock_key(self, phone: str) -> str:
        """Get Redis key for rate limiting."""
        return f"otp_lock:{phone}"
    
    def generate_otp(self, phone: str) -> str:
        """
        Generate OTP for phone number.
        
        Args:
            phone: Phone number
            
        Returns:
            Generated OTP string
        """
        # Use dev code in development
        if settings.dev_mode:
            return self.dev_code
        
        # Generate 6-digit OTP
        otp = str(secrets.randbelow(1000000)).zfill(6)
        
        # Store OTP with expiration
        otp_key = self._get_otp_key(phone)
        self.redis_client.setex(
            otp_key,
            timedelta(minutes=self.otp_expire_minutes),
            otp
        )
        
        # Reset attempts counter
        attempts_key = self._get_attempts_key(phone)
        self.redis_client.delete(attempts_key)
        
        return otp
    
    def verify_otp(self, phone: str, otp: str) -> bool:
        """
        Verify OTP for phone number.
        
        Args:
            phone: Phone number
            otp: OTP to verify
            
        Returns:
            True if OTP is valid, False otherwise
        """
        # Check if phone is locked
        if self.is_phone_locked(phone):
            return False
        
        # Check attempts limit
        if self.get_attempts_count(phone) >= self.otp_max_attempts:
            self.lock_phone(phone)
            return False
        
        # Get stored OTP
        otp_key = self._get_otp_key(phone)
        stored_otp = self.redis_client.get(otp_key)
        
        if not stored_otp:
            self.increment_attempts(phone)
            return False
        
        # Verify OTP
        is_valid = stored_otp.decode() == otp
        
        if is_valid:
            # Clear OTP and attempts on successful verification
            self.redis_client.delete(otp_key)
            self.redis_client.delete(self._get_attempts_key(phone))
        else:
            # Increment attempts on failed verification
            self.increment_attempts(phone)
        
        return is_valid
    
    def get_attempts_count(self, phone: str) -> int:
        """
        Get number of failed attempts for phone.
        
        Args:
            phone: Phone number
            
        Returns:
            Number of failed attempts
        """
        attempts_key = self._get_attempts_key(phone)
        attempts = self.redis_client.get(attempts_key)
        return int(attempts.decode()) if attempts else 0
    
    def increment_attempts(self, phone: str) -> None:
        """
        Increment failed attempts for phone.
        
        Args:
            phone: Phone number
        """
        attempts_key = self._get_attempts_key(phone)
        self.redis_client.incr(attempts_key)
        self.redis_client.expire(attempts_key, timedelta(hours=1))
    
    def is_phone_locked(self, phone: str) -> bool:
        """
        Check if phone is locked due to too many attempts.
        
        Args:
            phone: Phone number
            
        Returns:
            True if locked, False otherwise
        """
        lock_key = self._get_lock_key(phone)
        return self.redis_client.exists(lock_key) > 0
    
    def lock_phone(self, phone: str, duration_minutes: int = 30) -> None:
        """
        Lock phone for specified duration.
        
        Args:
            phone: Phone number
            duration_minutes: Lock duration in minutes
        """
        lock_key = self._get_lock_key(phone)
        self.redis_client.setex(
            lock_key,
            timedelta(minutes=duration_minutes),
            "locked"
        )
    
    def unlock_phone(self, phone: str) -> None:
        """
        Unlock phone.
        
        Args:
            phone: Phone number
        """
        lock_key = self._get_lock_key(phone)
        self.redis_client.delete(lock_key)
    
    def clear_otp(self, phone: str) -> None:
        """
        Clear OTP for phone.
        
        Args:
            phone: Phone number
        """
        otp_key = self._get_otp_key(phone)
        attempts_key = self._get_attempts_key(phone)
        self.redis_client.delete(otp_key)
        self.redis_client.delete(attempts_key)
    
    def get_otp_remaining_time(self, phone: str) -> int:
        """
        Get remaining time for OTP in seconds.
        
        Args:
            phone: Phone number
            
        Returns:
            Remaining time in seconds, 0 if expired
        """
        otp_key = self._get_otp_key(phone)
        return self.redis_client.ttl(otp_key)


# Global OTP manager instance
otp_manager = OTPManager()


def generate_otp(phone: str) -> str:
    """
    Generate OTP for phone number.
    
    Args:
        phone: Phone number
        
    Returns:
        Generated OTP string
    """
    return otp_manager.generate_otp(phone)


def verify_otp(phone: str, otp: str) -> bool:
    """
    Verify OTP for phone number.
    
    Args:
        phone: Phone number
        otp: OTP to verify
        
    Returns:
        True if OTP is valid, False otherwise
    """
    return otp_manager.verify_otp(phone, otp)


def is_phone_locked(phone: str) -> bool:
    """
    Check if phone is locked.
    
    Args:
        phone: Phone number
        
    Returns:
        True if locked, False otherwise
    """
    return otp_manager.is_phone_locked(phone)


def get_attempts_count(phone: str) -> int:
    """
    Get failed attempts count for phone.
    
    Args:
        phone: Phone number
        
    Returns:
        Number of failed attempts
    """
    return otp_manager.get_attempts_count(phone)


def get_otp_remaining_time(phone: str) -> int:
    """
    Get OTP remaining time.
    
    Args:
        phone: Phone number
        
    Returns:
        Remaining time in seconds
    """
    return otp_manager.get_otp_remaining_time(phone)


async def get_or_create_user_by_phone(phone: str) -> User:
    """
    Get existing user or create new user by phone number.
    
    Args:
        phone: Phone number
        
    Returns:
        User object
    """
    async with AsyncSessionLocal() as session:
        # Try to find existing user
        result = await session.execute(select(User).where(User.phone == phone))
        user = result.scalar_one_or_none()
        
        if user:
            return user
        
        # Create new user
        user = User(
            phone=phone,
            role="farmer",  # Default role
            locale="ml-IN",  # Default locale
            consent_flags='{"data_processing": false}',  # Default consent
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return user
