"""
Knowledge Base router.

Handles knowledge base operations and search.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/search")
async def search_kb():
    """Search knowledge base."""
    return {"message": "KB search endpoint - to be implemented"}

@router.post("/ingest")
async def ingest_document():
    """Ingest document."""
    return {"message": "Document ingest endpoint - to be implemented"}
