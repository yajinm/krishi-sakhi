"""
Dependency injection helpers for FastAPI.

Provides common dependencies for authentication, database access, and other services.
"""

import uuid
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_async_session
from app.models import User
from app.security import verify_token, extract_user_id_from_token
from app.security.rbac import check_permission, Permission

# HTTP Bearer token security
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> User:
    """
    Get current authenticated user.
    
    Args:
        credentials: HTTP Bearer credentials
        session: Database session
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    # Verify token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user ID
    user_id = extract_user_id_from_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Active user
        
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current verified user.
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Verified user
        
    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not verified"
        )
    return current_user


def require_permission(permission: Permission):
    """
    Dependency to require a specific permission.
    
    Args:
        permission: Required permission
        
    Returns:
        Dependency function
    """
    async def permission_dependency(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if not check_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value}"
            )
        return current_user
    
    return permission_dependency


def require_permissions(permissions: list[Permission]):
    """
    Dependency to require multiple permissions.
    
    Args:
        permissions: List of required permissions
        
    Returns:
        Dependency function
    """
    async def permissions_dependency(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        for permission in permissions:
            if not check_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission.value}"
                )
        return current_user
    
    return permissions_dependency


def require_admin():
    """
    Dependency to require admin role.
    
    Returns:
        Dependency function
    """
    return require_permission(Permission.ADMIN_READ)


def require_staff():
    """
    Dependency to require staff or admin role.
    
    Returns:
        Dependency function
    """
    async def staff_dependency(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in ["staff", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff or admin access required"
            )
        return current_user
    
    return staff_dependency


def require_farmer():
    """
    Dependency to require farmer role.
    
    Returns:
        Dependency function
    """
    async def farmer_dependency(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role != "farmer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Farmer access required"
            )
        return current_user
    
    return farmer_dependency


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    
    Args:
        credentials: Optional HTTP Bearer credentials
        session: Database session
        
    Returns:
        Current user or None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, session)
    except HTTPException:
        return None


# Common dependency aliases
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
CurrentVerifiedUser = Annotated[User, Depends(get_current_verified_user)]
OptionalUser = Annotated[Optional[User], Depends(get_optional_user)]
DatabaseSession = Annotated[AsyncSession, Depends(get_async_session)]

# Permission-based dependencies
AdminUser = Annotated[User, Depends(require_admin())]
StaffUser = Annotated[User, Depends(require_staff())]
FarmerUser = Annotated[User, Depends(require_farmer())]

# Specific permission dependencies
UserReadPermission = Annotated[User, Depends(require_permission(Permission.USER_READ))]
UserWritePermission = Annotated[User, Depends(require_permission(Permission.USER_WRITE))]
FarmerReadPermission = Annotated[User, Depends(require_permission(Permission.FARMER_READ))]
FarmerWritePermission = Annotated[User, Depends(require_permission(Permission.FARMER_WRITE))]
ActivityReadPermission = Annotated[User, Depends(require_permission(Permission.ACTIVITY_READ))]
ActivityWritePermission = Annotated[User, Depends(require_permission(Permission.ACTIVITY_WRITE))]
AdvisoryReadPermission = Annotated[User, Depends(require_permission(Permission.ADVISORY_READ))]
AdvisoryWritePermission = Annotated[User, Depends(require_permission(Permission.ADVISORY_WRITE))]
KBReadPermission = Annotated[User, Depends(require_permission(Permission.KB_READ))]
KBWritePermission = Annotated[User, Depends(require_permission(Permission.KB_WRITE))]
PrivacyPermission = Annotated[User, Depends(require_permission(Permission.PRIVACY_EXPORT))]
