"""
Farmer and farm-related models.

Defines Farmer, Farm, Field, Soil, and Crop models for farm profiling.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class SoilType(str, Enum):
    """Soil types in Kerala."""

    CLAY = "clay"
    SANDY = "sandy"
    LOAMY = "loamy"
    RED_SOIL = "red_soil"
    LATERITE = "laterite"
    ALLUVIAL = "alluvial"
    BLACK_SOIL = "black_soil"


class IrrigationSource(str, Enum):
    """Irrigation sources."""

    RAIN_FED = "rain_fed"
    WELL = "well"
    BORE_WELL = "bore_well"
    CANAL = "canal"
    TANK = "tank"
    SPRINKLER = "sprinkler"
    DRIP = "drip"
    FLOOD = "flood"


class CropType(str, Enum):
    """Crop types."""

    CEREAL = "cereal"
    PULSE = "pulse"
    OILSEED = "oilseed"
    SPICE = "spice"
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    PLANTATION = "plantation"
    MEDICINAL = "medicinal"
    FLOWER = "flower"


class Farmer(Base):
    """
    Farmer model for storing farmer profile information.
    
    Contains personal details, location, and farming preferences.
    """

    __tablename__ = "farmers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    district = Column(String(100), nullable=False, index=True)
    panchayat = Column(String(100), nullable=True)
    village = Column(String(100), nullable=True)
    lat = Column(Float, nullable=True)  # Latitude
    lon = Column(Float, nullable=True)  # Longitude
    soil_type = Column(SQLEnum(SoilType), nullable=True)
    irrig_src = Column(SQLEnum(IrrigationSource), nullable=True)
    experience_years = Column(Integer, nullable=True)
    farm_size_ha = Column(Float, nullable=True)
    primary_crops = Column(Text, nullable=True)  # JSON array of crop names
    farming_method = Column(String(100), nullable=True)  # organic, conventional, mixed
    education_level = Column(String(50), nullable=True)
    annual_income = Column(Float, nullable=True)
    family_size = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="farmer")
    farms = relationship("Farm", back_populates="farmer", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="farmer", cascade="all, delete-orphan")
    advisories = relationship("Advisory", back_populates="farmer", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="farmer", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="farmer", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Farmer(id={self.id}, name={self.name}, district={self.district})>"

    @property
    def location(self) -> Optional[tuple[float, float]]:
        """Get farmer location as (lat, lon) tuple."""
        if self.lat and self.lon:
            return (self.lat, self.lon)
        return None


class Farm(Base):
    """
    Farm model for storing farm information.
    
    Represents a physical farm owned by a farmer.
    """

    __tablename__ = "farms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    area_ha = Column(Float, nullable=False)
    geom = Column(Geometry("POLYGON", srid=4326), nullable=True)  # PostGIS geometry
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    farmer = relationship("Farmer", back_populates="farms")
    fields = relationship("Field", back_populates="farm", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Farm(id={self.id}, name={self.name}, area_ha={self.area_ha})>"


class Field(Base):
    """
    Field model for storing individual field information.
    
    Represents a specific field within a farm with crop information.
    """

    __tablename__ = "fields"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUID(as_uuid=True), ForeignKey("farms.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    crop = Column(String(100), nullable=True)  # Current crop name
    variety = Column(String(100), nullable=True)  # Crop variety
    sow_date = Column(DateTime(timezone=True), nullable=True)  # Sowing date
    area_ha = Column(Float, nullable=False)
    geom = Column(Geometry("POLYGON", srid=4326), nullable=True)  # PostGIS geometry
    soil_id = Column(UUID(as_uuid=True), ForeignKey("soils.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    farm = relationship("Farm", back_populates="fields")
    soil = relationship("Soil", back_populates="fields")
    activities = relationship("Activity", back_populates="field", cascade="all, delete-orphan")
    advisories = relationship("Advisory", back_populates="field", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="field", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Field(id={self.id}, name={self.name}, crop={self.crop})>"


class Soil(Base):
    """
    Soil model for storing soil information.
    
    Contains soil analysis data and characteristics.
    """

    __tablename__ = "soils"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    soil_type = Column(SQLEnum(SoilType), nullable=False)
    ph = Column(Float, nullable=True)  # pH level
    organic_matter = Column(Float, nullable=True)  # Organic matter percentage
    nitrogen = Column(Float, nullable=True)  # Nitrogen content
    phosphorus = Column(Float, nullable=True)  # Phosphorus content
    potassium = Column(Float, nullable=True)  # Potassium content
    water_holding_capacity = Column(Float, nullable=True)  # Water holding capacity
    drainage = Column(String(50), nullable=True)  # Good, moderate, poor
    texture = Column(String(50), nullable=True)  # Fine, medium, coarse
    color = Column(String(50), nullable=True)  # Red, black, brown, etc.
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    fields = relationship("Field", back_populates="soil")

    def __repr__(self) -> str:
        return f"<Soil(id={self.id}, name={self.name}, type={self.soil_type})>"


class Crop(Base):
    """
    Crop model for storing crop information.
    
    Contains crop details, growing seasons, and requirements.
    """

    __tablename__ = "crops"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    name_ml = Column(String(255), nullable=True)  # Malayalam name
    scientific_name = Column(String(255), nullable=True)
    crop_type = Column(SQLEnum(CropType), nullable=False)
    season = Column(String(50), nullable=True)  # kharif, rabi, summer
    duration_days = Column(Integer, nullable=True)  # Growing duration in days
    water_requirement = Column(String(50), nullable=True)  # Low, medium, high
    soil_preference = Column(Text, nullable=True)  # JSON array of preferred soil types
    climate_requirement = Column(String(100), nullable=True)
    planting_method = Column(String(100), nullable=True)
    spacing = Column(String(100), nullable=True)  # Plant spacing
    fertilizer_requirement = Column(Text, nullable=True)  # JSON object with NPK requirements
    pest_susceptibility = Column(Text, nullable=True)  # JSON array of common pests
    disease_susceptibility = Column(Text, nullable=True)  # JSON array of common diseases
    yield_per_ha = Column(Float, nullable=True)  # Expected yield per hectare
    market_price_range = Column(Text, nullable=True)  # JSON object with min/max prices
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Crop(id={self.id}, name={self.name}, type={self.crop_type})>"
