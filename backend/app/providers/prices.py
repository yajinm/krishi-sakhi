"""
Price data provider.

Handles commodity price data ingestion and retrieval.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from app.config import settings


class PriceProvider(ABC):
    """Abstract base class for price data providers."""
    
    @abstractmethod
    async def get_price_data(self, commodity: str, market: str) -> List[Dict]:
        """Get price data for commodity and market."""
        pass
    
    @abstractmethod
    async def ingest_price_data(self, data: List[Dict]) -> bool:
        """Ingest price data."""
        pass


class CSVPriceProvider(PriceProvider):
    """CSV-based price data provider."""
    
    def __init__(self):
        self.data = []
    
    async def get_price_data(self, commodity: str, market: str) -> List[Dict]:
        """Get price data from CSV."""
        # Filter data by commodity and market
        filtered_data = [
            item for item in self.data
            if item.get("commodity", "").lower() == commodity.lower()
            and item.get("market", "").lower() == market.lower()
        ]
        return filtered_data
    
    async def ingest_price_data(self, data: List[Dict]) -> bool:
        """Ingest price data from CSV."""
        try:
            self.data.extend(data)
            return True
        except Exception:
            return False


def get_price_provider() -> PriceProvider:
    """Get price provider."""
    return CSVPriceProvider()
