"""
Admin router.

Handles administrative operations and system management.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def admin_health():
    """Admin health check."""
    return {"message": "Admin health endpoint - to be implemented"}

@router.get("/rules")
async def list_rules():
    """List advisory rules."""
    return {"message": "Rules endpoint - to be implemented"}
