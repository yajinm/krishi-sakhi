"""
Geographic utilities.

Provides functions for distance calculations and geographic operations.
"""

import math
from typing import Tuple


def haversine_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    
    Args:
        point1: (latitude, longitude) of first point
        point2: (latitude, longitude) of second point
        
    Returns:
        Distance in kilometers
    """
    lat1, lon1 = point1
    lat2, lon2 = point2
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r


def is_within_radius(
    point1: Tuple[float, float], 
    point2: Tuple[float, float], 
    radius_km: float
) -> bool:
    """
    Check if two points are within specified radius.
    
    Args:
        point1: (latitude, longitude) of first point
        point2: (latitude, longitude) of second point
        radius_km: Radius in kilometers
        
    Returns:
        True if within radius, False otherwise
    """
    distance = haversine_distance(point1, point2)
    return distance <= radius_km


def get_bounding_box(lat: float, lon: float, radius_km: float) -> Tuple[float, float, float, float]:
    """
    Get bounding box for a point with given radius.
    
    Args:
        lat: Latitude
        lon: Longitude
        radius_km: Radius in kilometers
        
    Returns:
        (min_lat, min_lon, max_lat, max_lon)
    """
    # Approximate conversion from km to degrees
    lat_delta = radius_km / 111.0  # 1 degree latitude ≈ 111 km
    lon_delta = radius_km / (111.0 * math.cos(math.radians(lat)))
    
    return (
        lat - lat_delta,  # min_lat
        lon - lon_delta,  # min_lon
        lat + lat_delta,  # max_lat
        lon + lon_delta,  # max_lon
    )
