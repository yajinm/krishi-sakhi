"""
Reminders router.

Handles reminder and notification management.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_reminders():
    """List reminders."""
    return {"message": "Reminders endpoint - to be implemented"}

@router.post("/")
async def create_reminder():
    """Create reminder."""
    return {"message": "Create reminder endpoint - to be implemented"}
