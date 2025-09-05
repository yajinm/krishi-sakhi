"""
External data models.

Defines WeatherObs, PestReport, and PricePoint models for external data integration.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db import Base


class WeatherSource(str, Enum):
    """Sources of weather data."""

    OPENWEATHER = "openweather"
    IMD = "imd"  # India Meteorological Department
    MANUAL = "manual"
    SENSOR = "sensor"
    API = "api"


class PestSeverity(str, Enum):
    """Pest severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PriceSource(str, Enum):
    """Sources of price data."""

    MARKET = "market"
    MANDI = "mandi"
    API = "api"
    MANUAL = "manual"
    GOVERNMENT = "government"


class WeatherObs(Base):
    """
    Weather observation model for storing weather data.
    
    Contains temperature, humidity, wind, rain, and other weather metrics.
    """

    __tablename__ = "weather_obs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    district = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    temp_c = Column(Float, nullable=True)  # Temperature in Celsius
    temp_min_c = Column(Float, nullable=True)  # Minimum temperature
    temp_max_c = Column(Float, nullable=True)  # Maximum temperature
    humidity = Column(Float, nullable=True)  # Relative humidity percentage
    wind_speed_ms = Column(Float, nullable=True)  # Wind speed in m/s
    wind_direction = Column(Float, nullable=True)  # Wind direction in degrees
    pressure_hpa = Column(Float, nullable=True)  # Atmospheric pressure in hPa
    rain_mm = Column(Float, nullable=True)  # Rainfall in mm
    rain_24h_mm = Column(Float, nullable=True)  # 24-hour rainfall
    visibility_km = Column(Float, nullable=True)  # Visibility in km
    uv_index = Column(Float, nullable=True)  # UV index
    cloud_cover = Column(Float, nullable=True)  # Cloud cover percentage
    source = Column(SQLEnum(WeatherSource), nullable=False)
    source_data = Column(JSONB, nullable=True)  # Raw source data
    is_forecast = Column(Boolean, default=False, nullable=False)  # Forecast vs observation
    forecast_hours = Column(Integer, nullable=True)  # Hours ahead for forecast
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<WeatherObs(id={self.id}, district={self.district}, temp={self.temp_c}°C)>"

    @property
    def is_rainy(self) -> bool:
        """Check if it's raining (rain > 0)."""
        return self.rain_mm and self.rain_mm > 0

    @property
    def is_heavy_rain(self) -> bool:
        """Check if it's heavy rain (> 10mm)."""
        return self.rain_mm and self.rain_mm > 10

    @property
    def is_high_wind(self) -> bool:
        """Check if wind speed is high (> 6 m/s)."""
        return self.wind_speed_ms and self.wind_speed_ms > 6

    @property
    def is_hot(self) -> bool:
        """Check if temperature is hot (> 35°C)."""
        return self.temp_c and self.temp_c > 35

    @property
    def is_cold(self) -> bool:
        """Check if temperature is cold (< 20°C)."""
        return self.temp_c and self.temp_c < 20


class PestReport(Base):
    """
    Pest report model for storing pest and disease information.
    
    Contains pest details, severity, location, and control measures.
    """

    __tablename__ = "pest_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop = Column(String(100), nullable=False, index=True)
    pest_name = Column(String(255), nullable=False, index=True)
    pest_name_ml = Column(String(255), nullable=True)  # Malayalam name
    scientific_name = Column(String(255), nullable=True)
    district = Column(String(100), nullable=False, index=True)
    panchayat = Column(String(100), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    severity = Column(SQLEnum(PestSeverity), nullable=False)
    affected_area_ha = Column(Float, nullable=True)  # Affected area in hectares
    damage_percentage = Column(Float, nullable=True)  # Damage percentage
    stage = Column(String(50), nullable=True)  # Crop growth stage
    symptoms = Column(Text, nullable=True)  # Pest symptoms
    symptoms_ml = Column(Text, nullable=True)  # Malayalam symptoms
    control_measures = Column(Text, nullable=True)  # Control recommendations
    control_measures_ml = Column(Text, nullable=True)  # Malayalam control measures
    source = Column(String(100), nullable=False)  # Data source
    source_data = Column(JSONB, nullable=True)  # Raw source data
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_by = Column(String(255), nullable=True)  # Who verified the report
    verified_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<PestReport(id={self.id}, crop={self.crop}, pest={self.pest_name})>"

    @property
    def is_severe(self) -> bool:
        """Check if pest severity is high or critical."""
        return self.severity in [PestSeverity.HIGH, PestSeverity.CRITICAL]

    @property
    def is_recent(self) -> bool:
        """Check if report is recent (within 7 days)."""
        if not self.timestamp:
            return False
        days_ago = (datetime.utcnow() - self.timestamp).days
        return days_ago <= 7

    def verify(self, verified_by: str) -> None:
        """Mark pest report as verified."""
        self.is_verified = True
        self.verified_by = verified_by
        self.verified_at = datetime.utcnow()


class PricePoint(Base):
    """
    Price point model for storing commodity price data.
    
    Contains market prices for various agricultural commodities.
    """

    __tablename__ = "price_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market = Column(String(255), nullable=False, index=True)
    market_ml = Column(String(255), nullable=True)  # Malayalam market name
    commodity = Column(String(100), nullable=False, index=True)
    commodity_ml = Column(String(100), nullable=True)  # Malayalam commodity name
    variety = Column(String(100), nullable=True)  # Commodity variety
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    min_price = Column(Float, nullable=True)  # Minimum price per unit
    max_price = Column(Float, nullable=True)  # Maximum price per unit
    modal_price = Column(Float, nullable=True)  # Modal (most common) price
    avg_price = Column(Float, nullable=True)  # Average price
    unit = Column(String(50), nullable=False, default="kg")  # Price unit (kg, quintal, etc.)
    quantity = Column(Float, nullable=True)  # Available quantity
    quality = Column(String(50), nullable=True)  # Quality grade
    source = Column(SQLEnum(PriceSource), nullable=False)
    source_data = Column(JSONB, nullable=True)  # Raw source data
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_by = Column(String(255), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<PricePoint(id={self.id}, commodity={self.commodity}, price={self.modal_price})>"

    @property
    def price_range(self) -> Optional[tuple[float, float]]:
        """Get price range as (min, max) tuple."""
        if self.min_price and self.max_price:
            return (self.min_price, self.max_price)
        return None

    @property
    def is_high_price(self) -> bool:
        """Check if price is high (above average)."""
        if not self.avg_price or not self.modal_price:
            return False
        return self.modal_price > self.avg_price * 1.2  # 20% above average

    @property
    def is_low_price(self) -> bool:
        """Check if price is low (below average)."""
        if not self.avg_price or not self.modal_price:
            return False
        return self.modal_price < self.avg_price * 0.8  # 20% below average

    @property
    def is_recent(self) -> bool:
        """Check if price is recent (within 1 day)."""
        if not self.timestamp:
            return False
        hours_ago = (datetime.utcnow() - self.timestamp).total_seconds() / 3600
        return hours_ago <= 24

    def verify(self, verified_by: str) -> None:
        """Mark price point as verified."""
        self.is_verified = True
        self.verified_by = verified_by
        self.verified_at = datetime.utcnow()
