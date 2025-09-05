"""
Geographic data mixins and utilities.

Provides PostGIS integration and geographic data handling.
"""

from typing import Optional, Tuple

from geoalchemy2 import Geometry
from sqlalchemy import Column, Float, func
from sqlalchemy.ext.declarative import declared_attr


class GeoMixin:
    """
    Mixin for models that need geographic data.
    
    Provides common geographic fields and methods.
    """

    @declared_attr
    def lat(cls):
        """Latitude column."""
        return Column(Float, nullable=True)

    @declared_attr
    def lon(cls):
        """Longitude column."""
        return Column(Float, nullable=True)

    @declared_attr
    def geom(cls):
        """PostGIS geometry column."""
        return Column(Geometry("POINT", srid=4326), nullable=True)

    @property
    def location(self) -> Optional[Tuple[float, float]]:
        """Get location as (lat, lon) tuple."""
        if self.lat and self.lon:
            return (self.lat, self.lon)
        return None

    @location.setter
    def location(self, value: Optional[Tuple[float, float]]) -> None:
        """Set location from (lat, lon) tuple."""
        if value:
            self.lat, self.lon = value
            # Update geometry if available
            if hasattr(self, 'geom'):
                self.geom = func.ST_SetSRID(
                    func.ST_MakePoint(self.lon, self.lat), 4326
                )
        else:
            self.lat = None
            self.lon = None
            if hasattr(self, 'geom'):
                self.geom = None

    def distance_to(self, other: "GeoMixin") -> Optional[float]:
        """
        Calculate distance to another geographic point.
        
        Args:
            other: Another object with lat/lon coordinates
            
        Returns:
            Distance in kilometers, or None if either point is missing coordinates
        """
        if not self.location or not other.location:
            return None
        
        from app.utils.geo import haversine_distance
        return haversine_distance(self.location, other.location)

    def is_within_radius(self, other: "GeoMixin", radius_km: float) -> bool:
        """
        Check if another point is within specified radius.
        
        Args:
            other: Another object with lat/lon coordinates
            radius_km: Radius in kilometers
            
        Returns:
            True if within radius, False otherwise
        """
        distance = self.distance_to(other)
        return distance is not None and distance <= radius_km
