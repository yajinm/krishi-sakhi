"""
Conversation router.

Handles conversational interface for Malayalam and English.
"""

from fastapi import APIRouter

router = APIRouter()

@router.post("/send")
async def send_message():
    """Send conversation message."""
    return {"message": "Conversation endpoint - to be implemented"}
