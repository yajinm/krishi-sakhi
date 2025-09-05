"""
SQLAlchemy models for Krishi Sakhi backend.

This module contains all database models organized by domain:
- User management and authentication
- Farmer and farm profiling
- Activity tracking
- Advisory system
- Knowledge base
- External data integration
- Audit and privacy
"""

from app.models.audit import AuditLog, Consent
from app.models.farmer import Crop, Farm, Farmer, Field, Soil
from app.models.user import AuthProvider, User
from app.models.activity import Activity, Media
from app.models.advisory import Advisory, AdvisoryRule, Trigger
from app.models.reminder import Notification, Reminder
from app.models.kb import Chunk, Doc, Embedding
from app.models.ext import PestReport, PricePoint, WeatherObs
from app.models.geo import GeoMixin

__all__ = [
    # User and Auth
    "User",
    "AuthProvider",
    # Farmer and Farm
    "Farmer",
    "Farm",
    "Field",
    "Soil",
    "Crop",
    # Activity
    "Activity",
    "Media",
    # Advisory
    "Advisory",
    "AdvisoryRule",
    "Trigger",
    # Reminder
    "Reminder",
    "Notification",
    # Knowledge Base
    "Doc",
    "Chunk",
    "Embedding",
    # External Data
    "WeatherObs",
    "PestReport",
    "PricePoint",
    # Audit and Privacy
    "AuditLog",
    "Consent",
    # Mixins
    "GeoMixin",
]
