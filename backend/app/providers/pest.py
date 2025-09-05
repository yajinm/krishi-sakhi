"""
Pest data provider.

Handles pest and disease data ingestion and retrieval.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from app.config import settings


class PestProvider(ABC):
    """Abstract base class for pest data providers."""
    
    @abstractmethod
    async def get_pest_data(self, crop: str, district: str) -> List[Dict]:
        """Get pest data for crop and district."""
        pass
    
    @abstractmethod
    async def ingest_pest_data(self, data: List[Dict]) -> bool:
        """Ingest pest data."""
        pass


class CSVPestProvider(PestProvider):
    """CSV-based pest data provider."""
    
    def __init__(self):
        self.data = []
    
    async def get_pest_data(self, crop: str, district: str) -> List[Dict]:
        """Get pest data from CSV."""
        # Filter data by crop and district
        filtered_data = [
            item for item in self.data
            if item.get("crop", "").lower() == crop.lower()
            and item.get("district", "").lower() == district.lower()
        ]
        return filtered_data
    
    async def ingest_pest_data(self, data: List[Dict]) -> bool:
        """Ingest pest data from CSV."""
        try:
            self.data.extend(data)
            return True
        except Exception:
            return False


def get_pest_provider() -> PestProvider:
    """Get pest provider."""
    return CSVPestProvider()
