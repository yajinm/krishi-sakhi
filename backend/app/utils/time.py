"""
Time utilities.

Provides functions for timezone handling and time operations.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional

import pytz

from app.config import settings


# IST timezone
IST = pytz.timezone(settings.timezone)


def now_ist() -> datetime:
    """
    Get current time in IST.
    
    Returns:
        Current datetime in IST
    """
    return datetime.now(IST)


def utc_to_ist(utc_dt: datetime) -> datetime:
    """
    Convert UTC datetime to IST.
    
    Args:
        utc_dt: UTC datetime
        
    Returns:
        IST datetime
    """
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    
    return utc_dt.astimezone(IST)


def ist_to_utc(ist_dt: datetime) -> datetime:
    """
    Convert IST datetime to UTC.
    
    Args:
        ist_dt: IST datetime
        
    Returns:
        UTC datetime
    """
    if ist_dt.tzinfo is None:
        ist_dt = IST.localize(ist_dt)
    
    return ist_dt.astimezone(timezone.utc)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string.
    
    Args:
        dt: Datetime object
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    Parse datetime string.
    
    Args:
        dt_str: Datetime string
        format_str: Format string
        
    Returns:
        Parsed datetime or None
    """
    try:
        return datetime.strptime(dt_str, format_str)
    except ValueError:
        return None


def get_time_ago(dt: datetime) -> str:
    """
    Get human-readable time ago string.
    
    Args:
        dt: Datetime object
        
    Returns:
        Time ago string
    """
    now = now_ist()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hours ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minutes ago"
    else:
        return "Just now"
