"""
User-related schemas.

Provides Pydantic models for user data validation and serialization.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models import UserRole


class UserBase(BaseModel):
    """Base user schema."""
    phone: str = Field(..., description="Phone number with country code")
    role: UserRole = Field(default=UserRole.FARMER, description="User role")
    locale: str = Field(default="ml-IN", description="User locale")


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    role: Optional[UserRole] = None
    locale: Optional[str] = None
    consent_flags: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: uuid.UUID = Field(..., description="User ID")
    consent_flags: Optional[str] = Field(None, description="Consent flags")
    is_active: bool = Field(..., description="Is user active")
    is_verified: bool = Field(..., description="Is user verified")
    last_login_at: Optional[datetime] = Field(None, description="Last login time")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")

    class Config:
        from_attributes = True
