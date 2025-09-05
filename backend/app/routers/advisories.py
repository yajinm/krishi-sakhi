"""
Advisories router.

Handles advisory generation and management.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_advisories():
    """List advisories."""
    return {"message": "Advisories endpoint - to be implemented"}

@router.post("/generate")
async def generate_advisory():
    """Generate advisory."""
    return {"message": "Generate advisory endpoint - to be implemented"}
