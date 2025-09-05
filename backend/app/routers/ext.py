"""
External data router.

Handles weather, pest, and price data endpoints.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/weather")
async def get_weather():
    """Get weather data."""
    return {"message": "Weather endpoint - to be implemented"}

@router.get("/pest")
async def get_pest_data():
    """Get pest data."""
    return {"message": "Pest data endpoint - to be implemented"}

@router.get("/prices")
async def get_price_data():
    """Get price data."""
    return {"message": "Price data endpoint - to be implemented"}
