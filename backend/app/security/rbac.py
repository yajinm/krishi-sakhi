"""
Role-Based Access Control (RBAC) utilities.

Handles permissions, roles, and access control for the application.
"""

from enum import Enum
from typing import List, Set

from app.models import User, UserRole


class Permission(str, Enum):
    """System permissions."""
    
    # User management
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    
    # Farmer management
    FARMER_READ = "farmer:read"
    FARMER_WRITE = "farmer:write"
    FARMER_DELETE = "farmer:delete"
    
    # Farm management
    FARM_READ = "farm:read"
    FARM_WRITE = "farm:write"
    FARM_DELETE = "farm:delete"
    
    # Field management
    FIELD_READ = "field:read"
    FIELD_WRITE = "field:write"
    FIELD_DELETE = "field:delete"
    
    # Activity management
    ACTIVITY_READ = "activity:read"
    ACTIVITY_WRITE = "activity:write"
    ACTIVITY_DELETE = "activity:delete"
    
    # Advisory management
    ADVISORY_READ = "advisory:read"
    ADVISORY_WRITE = "advisory:write"
    ADVISORY_DELETE = "advisory:delete"
    ADVISORY_GENERATE = "advisory:generate"
    
    # Reminder management
    REMINDER_READ = "reminder:read"
    REMINDER_WRITE = "reminder:write"
    REMINDER_DELETE = "reminder:delete"
    
    # Knowledge base
    KB_READ = "kb:read"
    KB_WRITE = "kb:write"
    KB_DELETE = "kb:delete"
    KB_INGEST = "kb:ingest"
    
    # External data
    EXT_READ = "ext:read"
    EXT_WRITE = "ext:write"
    EXT_SYNC = "ext:sync"
    
    # Admin operations
    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"
    ADMIN_DELETE = "admin:delete"
    ADMIN_CONFIG = "admin:config"
    
    # Privacy operations
    PRIVACY_EXPORT = "privacy:export"
    PRIVACY_DELETE = "privacy:delete"
    PRIVACY_CONSENT = "privacy:consent"
    
    # System operations
    SYSTEM_HEALTH = "system:health"
    SYSTEM_METRICS = "system:metrics"
    SYSTEM_LOGS = "system:logs"


# Role-permission mapping
ROLE_PERMISSIONS = {
    UserRole.FARMER: {
        # Own data access
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.FARMER_READ,
        Permission.FARMER_WRITE,
        Permission.FARM_READ,
        Permission.FARM_WRITE,
        Permission.FIELD_READ,
        Permission.FIELD_WRITE,
        Permission.ACTIVITY_READ,
        Permission.ACTIVITY_WRITE,
        Permission.ADVISORY_READ,
        Permission.REMINDER_READ,
        Permission.REMINDER_WRITE,
        Permission.KB_READ,
        Permission.EXT_READ,
        Permission.PRIVACY_EXPORT,
        Permission.PRIVACY_CONSENT,
    },
    UserRole.STAFF: {
        # All farmer permissions plus staff-specific
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.FARMER_READ,
        Permission.FARMER_WRITE,
        Permission.FARM_READ,
        Permission.FARM_WRITE,
        Permission.FIELD_READ,
        Permission.FIELD_WRITE,
        Permission.ACTIVITY_READ,
        Permission.ACTIVITY_WRITE,
        Permission.ADVISORY_READ,
        Permission.ADVISORY_WRITE,
        Permission.ADVISORY_GENERATE,
        Permission.REMINDER_READ,
        Permission.REMINDER_WRITE,
        Permission.KB_READ,
        Permission.KB_WRITE,
        Permission.KB_INGEST,
        Permission.EXT_READ,
        Permission.EXT_WRITE,
        Permission.EXT_SYNC,
        Permission.ADMIN_READ,
        Permission.SYSTEM_HEALTH,
        Permission.SYSTEM_METRICS,
    },
    UserRole.ADMIN: {
        # All permissions
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_DELETE,
        Permission.FARMER_READ,
        Permission.FARMER_WRITE,
        Permission.FARMER_DELETE,
        Permission.FARM_READ,
        Permission.FARM_WRITE,
        Permission.FARM_DELETE,
        Permission.FIELD_READ,
        Permission.FIELD_WRITE,
        Permission.FIELD_DELETE,
        Permission.ACTIVITY_READ,
        Permission.ACTIVITY_WRITE,
        Permission.ACTIVITY_DELETE,
        Permission.ADVISORY_READ,
        Permission.ADVISORY_WRITE,
        Permission.ADVISORY_DELETE,
        Permission.ADVISORY_GENERATE,
        Permission.REMINDER_READ,
        Permission.REMINDER_WRITE,
        Permission.REMINDER_DELETE,
        Permission.KB_READ,
        Permission.KB_WRITE,
        Permission.KB_DELETE,
        Permission.KB_INGEST,
        Permission.EXT_READ,
        Permission.EXT_WRITE,
        Permission.EXT_SYNC,
        Permission.ADMIN_READ,
        Permission.ADMIN_WRITE,
        Permission.ADMIN_DELETE,
        Permission.ADMIN_CONFIG,
        Permission.PRIVACY_EXPORT,
        Permission.PRIVACY_DELETE,
        Permission.PRIVACY_CONSENT,
        Permission.SYSTEM_HEALTH,
        Permission.SYSTEM_METRICS,
        Permission.SYSTEM_LOGS,
    },
}


def get_user_permissions(user: User) -> Set[Permission]:
    """
    Get permissions for a user based on their role.
    
    Args:
        user: User object
        
    Returns:
        Set of permissions
    """
    return ROLE_PERMISSIONS.get(user.role, set())


def check_permission(user: User, permission: Permission) -> bool:
    """
    Check if user has a specific permission.
    
    Args:
        user: User object
        permission: Permission to check
        
    Returns:
        True if user has permission, False otherwise
    """
    user_permissions = get_user_permissions(user)
    return permission in user_permissions


def check_permissions(user: User, permissions: List[Permission]) -> bool:
    """
    Check if user has all specified permissions.
    
    Args:
        user: User object
        permissions: List of permissions to check
        
    Returns:
        True if user has all permissions, False otherwise
    """
    user_permissions = get_user_permissions(user)
    return all(permission in user_permissions for permission in permissions)


def check_any_permission(user: User, permissions: List[Permission]) -> bool:
    """
    Check if user has any of the specified permissions.
    
    Args:
        user: User object
        permissions: List of permissions to check
        
    Returns:
        True if user has any permission, False otherwise
    """
    user_permissions = get_user_permissions(user)
    return any(permission in user_permissions for permission in permissions)


def require_permission(permission: Permission):
    """
    Decorator to require a specific permission.
    
    Args:
        permission: Required permission
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would be used with dependency injection in FastAPI
            # Implementation depends on how user is passed to the function
            pass
        return wrapper
    return decorator


def require_permissions(permissions: List[Permission]):
    """
    Decorator to require multiple permissions.
    
    Args:
        permissions: List of required permissions
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would be used with dependency injection in FastAPI
            # Implementation depends on how user is passed to the function
            pass
        return wrapper
    return decorator


def require_role(role: UserRole):
    """
    Decorator to require a specific role.
    
    Args:
        role: Required role
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would be used with dependency injection in FastAPI
            # Implementation depends on how user is passed to the function
            pass
        return wrapper
    return decorator


def is_admin(user: User) -> bool:
    """
    Check if user is admin.
    
    Args:
        user: User object
        
    Returns:
        True if user is admin, False otherwise
    """
    return user.role == UserRole.ADMIN


def is_staff(user: User) -> bool:
    """
    Check if user is staff or admin.
    
    Args:
        user: User object
        
    Returns:
        True if user is staff or admin, False otherwise
    """
    return user.role in [UserRole.STAFF, UserRole.ADMIN]


def is_farmer(user: User) -> bool:
    """
    Check if user is farmer.
    
    Args:
        user: User object
        
    Returns:
        True if user is farmer, False otherwise
    """
    return user.role == UserRole.FARMER


def can_access_resource(user: User, resource_owner_id: str) -> bool:
    """
    Check if user can access a resource owned by another user.
    
    Args:
        user: User object
        resource_owner_id: ID of resource owner
        
    Returns:
        True if user can access resource, False otherwise
    """
    # Admin and staff can access all resources
    if is_staff(user):
        return True
    
    # Farmers can only access their own resources
    return str(user.id) == resource_owner_id


def get_accessible_resources(user: User, all_resources: List[dict]) -> List[dict]:
    """
    Filter resources based on user permissions.
    
    Args:
        user: User object
        all_resources: List of all resources
        
    Returns:
        List of accessible resources
    """
    if is_staff(user):
        return all_resources
    
    # Filter to only user's own resources
    return [resource for resource in all_resources if resource.get("owner_id") == str(user.id)]
