"""
Farmers router.

Handles farmer and farm management endpoints.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_farmers():
    """List farmers."""
    return {"message": "Farmers endpoint - to be implemented"}

@router.post("/")
async def create_farmer():
    """Create farmer."""
    return {"message": "Create farmer endpoint - to be implemented"}
