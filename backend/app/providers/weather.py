"""
Weather data providers.

Provides interfaces and implementations for weather data retrieval.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import httpx

from app.config import settings


class WeatherProvider(ABC):
    """Abstract base class for weather providers."""
    
    @abstractmethod
    async def get_current_weather(self, lat: float, lon: float) -> Dict[str, any]:
        """Get current weather for coordinates."""
        pass
    
    @abstractmethod
    async def get_forecast(self, lat: float, lon: float, days: int = 5) -> List[Dict[str, any]]:
        """Get weather forecast for coordinates."""
        pass
    
    @abstractmethod
    async def get_weather_by_district(self, district: str) -> Dict[str, any]:
        """Get weather for district."""
        pass


class DummyWeatherProvider(WeatherProvider):
    """Dummy weather provider for development and testing."""
    
    async def get_current_weather(self, lat: float, lon: float) -> Dict[str, any]:
        """Get dummy current weather."""
        await asyncio.sleep(0.5)
        
        return {
            "temp_c": 28.5,
            "temp_min_c": 24.0,
            "temp_max_c": 32.0,
            "humidity": 75,
            "wind_speed_ms": 3.2,
            "wind_direction": 180,
            "pressure_hpa": 1013.25,
            "rain_mm": 0.0,
            "visibility_km": 10.0,
            "uv_index": 6,
            "cloud_cover": 30,
            "description": "Partly cloudy",
            "timestamp": datetime.utcnow(),
            "provider": "dummy",
        }
    
    async def get_forecast(self, lat: float, lon: float, days: int = 5) -> List[Dict[str, any]]:
        """Get dummy weather forecast."""
        await asyncio.sleep(0.8)
        
        forecast = []
        for i in range(days):
            forecast.append({
                "date": datetime.utcnow() + timedelta(days=i),
                "temp_min_c": 22 + (i % 3),
                "temp_max_c": 30 + (i % 4),
                "humidity": 70 + (i % 2) * 10,
                "wind_speed_ms": 2 + (i % 3),
                "rain_mm": 0 if i % 3 != 0 else 5 + (i % 2) * 3,
                "description": "Partly cloudy" if i % 2 == 0 else "Sunny",
                "provider": "dummy",
            })
        
        return forecast
    
    async def get_weather_by_district(self, district: str) -> Dict[str, any]:
        """Get dummy weather for district."""
        return await self.get_current_weather(10.5167, 76.2167)  # Default to Thrissur


class OpenWeatherProvider(WeatherProvider):
    """OpenWeatherMap API provider."""
    
    def __init__(self):
        self.api_key = settings.openweather_api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def get_current_weather(self, lat: float, lon: float) -> Dict[str, any]:
        """Get current weather from OpenWeatherMap."""
        if not self.api_key:
            # Fallback to dummy provider
            dummy_provider = DummyWeatherProvider()
            return await dummy_provider.get_current_weather(lat, lon)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.api_key,
                        "units": "metric",
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "temp_c": data["main"]["temp"],
                    "temp_min_c": data["main"]["temp_min"],
                    "temp_max_c": data["main"]["temp_max"],
                    "humidity": data["main"]["humidity"],
                    "wind_speed_ms": data["wind"]["speed"],
                    "wind_direction": data["wind"].get("deg", 0),
                    "pressure_hpa": data["main"]["pressure"],
                    "rain_mm": data.get("rain", {}).get("1h", 0),
                    "visibility_km": data.get("visibility", 10000) / 1000,
                    "uv_index": 0,  # Not available in current weather
                    "cloud_cover": data["clouds"]["all"],
                    "description": data["weather"][0]["description"],
                    "timestamp": datetime.utcnow(),
                    "provider": "openweather",
                }
                
        except Exception as e:
            # Fallback to dummy provider
            dummy_provider = DummyWeatherProvider()
            return await dummy_provider.get_current_weather(lat, lon)
    
    async def get_forecast(self, lat: float, lon: float, days: int = 5) -> List[Dict[str, any]]:
        """Get weather forecast from OpenWeatherMap."""
        if not self.api_key:
            # Fallback to dummy provider
            dummy_provider = DummyWeatherProvider()
            return await dummy_provider.get_forecast(lat, lon, days)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/forecast",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.api_key,
                        "units": "metric",
                        "cnt": days * 8,  # 8 forecasts per day
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                
                # Group forecasts by date
                daily_forecasts = {}
                for item in data["list"]:
                    date = datetime.fromtimestamp(item["dt"]).date()
                    if date not in daily_forecasts:
                        daily_forecasts[date] = []
                    daily_forecasts[date].append(item)
                
                # Create daily summaries
                forecast = []
                for date, items in list(daily_forecasts.items())[:days]:
                    temps = [item["main"]["temp"] for item in items]
                    humidities = [item["main"]["humidity"] for item in items]
                    wind_speeds = [item["wind"]["speed"] for item in items]
                    rains = [item.get("rain", {}).get("3h", 0) for item in items]
                    
                    forecast.append({
                        "date": datetime.combine(date, datetime.min.time()),
                        "temp_min_c": min(temps),
                        "temp_max_c": max(temps),
                        "humidity": sum(humidities) / len(humidities),
                        "wind_speed_ms": sum(wind_speeds) / len(wind_speeds),
                        "rain_mm": sum(rains),
                        "description": items[0]["weather"][0]["description"],
                        "provider": "openweather",
                    })
                
                return forecast
                
        except Exception as e:
            # Fallback to dummy provider
            dummy_provider = DummyWeatherProvider()
            return await dummy_provider.get_forecast(lat, lon, days)
    
    async def get_weather_by_district(self, district: str) -> Dict[str, any]:
        """Get weather for district using coordinates."""
        # Kerala district coordinates
        district_coords = {
            "തൃശൂർ": (10.5167, 76.2167),
            "കോഴിക്കോട്": (11.2588, 75.7804),
            "Ernakulam": (9.9312, 76.2673),
            "Thrissur": (10.5167, 76.2167),
            "Kozhikode": (11.2588, 75.7804),
        }
        
        coords = district_coords.get(district, (10.5167, 76.2167))
        return await self.get_current_weather(coords[0], coords[1])


def get_weather_provider() -> WeatherProvider:
    """Get weather provider based on configuration."""
    provider_name = settings.weather_provider.lower()
    
    if provider_name == "openweather":
        return OpenWeatherProvider()
    else:
        return DummyWeatherProvider()
