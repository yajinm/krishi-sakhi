"""
Seed script for demo data.

Creates sample farmers, farms, fields, crops, and other demo data for testing.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import AsyncSessionLocal, Base, async_engine
from app.models import (
    Activity,
    ActivityKind,
    Advisory,
    AdvisoryRule,
    AdvisorySeverity,
    AdvisorySource,
    AuthProvider,
    Consent,
    ConsentKind,
    Crop,
    CropType,
    Doc,
    DocSource,
    DocType,
    Embedding,
    Farm,
    Farmer,
    Field,
    IrrigationSource,
    Media,
    MediaType,
    Notification,
    NotificationChannel,
    NotificationStatus,
    PestReport,
    PestSeverity,
    PricePoint,
    PriceSource,
    Reminder,
    ReminderKind,
    Soil,
    SoilType,
    Trigger,
    TriggerType,
    User,
    UserRole,
    WeatherObs,
    WeatherSource,
)


async def create_demo_users(session: AsyncSession) -> list[User]:
    """Create demo users."""
    users = []
    
    # Demo farmers
    farmer_data = [
        {
            "phone": "+919876543210",
            "role": UserRole.FARMER,
            "locale": "ml-IN",
            "consent_flags": json.dumps({
                "data_processing": True,
                "notifications": True,
                "location": True,
                "voice_recording": True,
            }),
        },
        {
            "phone": "+919876543211",
            "role": UserRole.FARMER,
            "locale": "ml-IN",
            "consent_flags": json.dumps({
                "data_processing": True,
                "notifications": True,
                "location": True,
                "voice_recording": False,
            }),
        },
        {
            "phone": "+919876543212",
            "role": UserRole.FARMER,
            "locale": "en-IN",
            "consent_flags": json.dumps({
                "data_processing": True,
                "notifications": True,
                "location": True,
                "voice_recording": True,
            }),
        },
    ]
    
    for user_data in farmer_data:
        user = User(**user_data)
        session.add(user)
        users.append(user)
    
    # Demo staff user
    staff_user = User(
        phone="+919876543213",
        role=UserRole.STAFF,
        locale="en-IN",
        consent_flags=json.dumps({"data_processing": True}),
    )
    session.add(staff_user)
    users.append(staff_user)
    
    await session.commit()
    return users


async def create_demo_farmers(session: AsyncSession, users: list[User]) -> list[Farmer]:
    """Create demo farmers."""
    farmers = []
    
    farmer_data = [
        {
            "name": "രാജൻ പിള്ള",
            "district": "തൃശൂർ",
            "panchayat": "കുറുമ്പ്രാമം",
            "village": "കുറുമ്പ്രാമം",
            "lat": 10.5167,
            "lon": 76.2167,
            "soil_type": SoilType.LOAMY,
            "irrig_src": IrrigationSource.WELL,
            "experience_years": 15,
            "farm_size_ha": 2.5,
            "primary_crops": json.dumps(["പാട്ട", "വാഴ", "കാട്ടുകുരുമ"]),
            "farming_method": "organic",
            "education_level": "high_school",
            "annual_income": 150000,
            "family_size": 4,
        },
        {
            "name": "ലക്ഷ്മി അമ്മ",
            "district": "കോഴിക്കോട്",
            "panchayat": "കോഴിക്കോട്",
            "village": "കോഴിക്കോട്",
            "lat": 11.2588,
            "lon": 75.7804,
            "soil_type": SoilType.RED_SOIL,
            "irrig_src": IrrigationSource.RAIN_FED,
            "experience_years": 20,
            "farm_size_ha": 1.8,
            "primary_crops": json.dumps(["വാഴ", "കാട്ടുകുരുമ", "കുരുമ"]),
            "farming_method": "conventional",
            "education_level": "primary",
            "annual_income": 120000,
            "family_size": 3,
        },
        {
            "name": "Suresh Kumar",
            "district": "Ernakulam",
            "panchayat": "Kochi",
            "village": "Kochi",
            "lat": 9.9312,
            "lon": 76.2673,
            "soil_type": SoilType.ALLUVIAL,
            "irrig_src": IrrigationSource.CANAL,
            "experience_years": 12,
            "farm_size_ha": 3.2,
            "primary_crops": json.dumps(["Rice", "Banana", "Coconut"]),
            "farming_method": "mixed",
            "education_level": "college",
            "annual_income": 200000,
            "family_size": 5,
        },
    ]
    
    for i, farmer_data in enumerate(farmer_data):
        farmer = Farmer(user_id=users[i].id, **farmer_data)
        session.add(farmer)
        farmers.append(farmer)
    
    await session.commit()
    return farmers


async def create_demo_crops(session: AsyncSession) -> list[Crop]:
    """Create demo crops."""
    crops = []
    
    crop_data = [
        {
            "name": "Rice",
            "name_ml": "പാട്ട",
            "scientific_name": "Oryza sativa",
            "crop_type": CropType.CEREAL,
            "season": "kharif",
            "duration_days": 120,
            "water_requirement": "high",
            "soil_preference": json.dumps(["loamy", "alluvial"]),
            "climate_requirement": "tropical",
            "planting_method": "transplanting",
            "spacing": "20x20 cm",
            "fertilizer_requirement": json.dumps({"N": 120, "P": 60, "K": 60}),
            "pest_susceptibility": json.dumps(["brown_plant_hopper", "rice_blast", "bacterial_blight"]),
            "disease_susceptibility": json.dumps(["rice_blast", "bacterial_blight", "sheath_blight"]),
            "yield_per_ha": 3000,
            "market_price_range": json.dumps({"min": 25, "max": 35}),
            "description": "Staple food crop of Kerala",
        },
        {
            "name": "Banana",
            "name_ml": "വാഴ",
            "scientific_name": "Musa acuminata",
            "crop_type": CropType.FRUIT,
            "season": "year_round",
            "duration_days": 365,
            "water_requirement": "medium",
            "soil_preference": json.dumps(["loamy", "red_soil"]),
            "climate_requirement": "tropical",
            "planting_method": "suckers",
            "spacing": "2x2 m",
            "fertilizer_requirement": json.dumps({"N": 200, "P": 100, "K": 300}),
            "pest_susceptibility": json.dumps(["banana_aphid", "banana_weevil", "nematodes"]),
            "disease_susceptibility": json.dumps(["panama_disease", "sigatoka", "bunchy_top"]),
            "yield_per_ha": 25000,
            "market_price_range": json.dumps({"min": 15, "max": 25}),
            "description": "Important fruit crop of Kerala",
        },
        {
            "name": "Brinjal",
            "name_ml": "കാട്ടുകുരുമ",
            "scientific_name": "Solanum melongena",
            "crop_type": CropType.VEGETABLE,
            "season": "year_round",
            "duration_days": 150,
            "water_requirement": "medium",
            "soil_preference": json.dumps(["loamy", "red_soil"]),
            "climate_requirement": "tropical",
            "planting_method": "seedlings",
            "spacing": "60x45 cm",
            "fertilizer_requirement": json.dumps({"N": 100, "P": 50, "K": 50}),
            "pest_susceptibility": json.dumps(["fruit_borer", "aphids", "whitefly"]),
            "disease_susceptibility": json.dumps(["bacterial_wilt", "damping_off", "leaf_spot"]),
            "yield_per_ha": 20000,
            "market_price_range": json.dumps({"min": 20, "max": 40}),
            "description": "Popular vegetable crop",
        },
    ]
    
    for crop_data in crop_data:
        crop = Crop(**crop_data)
        session.add(crop)
        crops.append(crop)
    
    await session.commit()
    return crops


async def create_demo_soils(session: AsyncSession) -> list[Soil]:
    """Create demo soil types."""
    soils = []
    
    soil_data = [
        {
            "name": "Loamy Soil",
            "name_ml": "ചെളിമണ്ണ്",
            "soil_type": SoilType.LOAMY,
            "ph": 6.5,
            "organic_matter": 2.5,
            "nitrogen": 0.15,
            "phosphorus": 0.08,
            "potassium": 0.12,
            "water_holding_capacity": 25,
            "drainage": "good",
            "texture": "medium",
            "color": "brown",
            "description": "Ideal for most crops",
        },
        {
            "name": "Red Soil",
            "name_ml": "ചുവന്ന മണ്ണ്",
            "soil_type": SoilType.RED_SOIL,
            "ph": 5.8,
            "organic_matter": 1.8,
            "nitrogen": 0.12,
            "phosphorus": 0.06,
            "potassium": 0.10,
            "water_holding_capacity": 20,
            "drainage": "moderate",
            "texture": "fine",
            "color": "red",
            "description": "Common in Kerala hills",
        },
        {
            "name": "Alluvial Soil",
            "name_ml": "അലുവിയൽ മണ്ണ്",
            "soil_type": SoilType.ALLUVIAL,
            "ph": 7.0,
            "organic_matter": 3.0,
            "nitrogen": 0.18,
            "phosphorus": 0.10,
            "potassium": 0.15,
            "water_holding_capacity": 30,
            "drainage": "excellent",
            "texture": "medium",
            "color": "dark_brown",
            "description": "Rich in nutrients",
        },
    ]
    
    for soil_data in soil_data:
        soil = Soil(**soil_data)
        session.add(soil)
        soils.append(soil)
    
    await session.commit()
    return soils


async def create_demo_farms(session: AsyncSession, farmers: list[Farmer]) -> list[Farm]:
    """Create demo farms."""
    farms = []
    
    farm_data = [
        {
            "name": "രാജൻ പിള്ളയുടെ കൃഷിഭൂമി",
            "area_ha": 2.5,
            "description": "പാട്ട, വാഴ, കാട്ടുകുരുമ കൃഷി",
        },
        {
            "name": "ലക്ഷ്മി അമ്മയുടെ കൃഷിഭൂമി",
            "area_ha": 1.8,
            "description": "വാഴ, കാട്ടുകുരുമ കൃഷി",
        },
        {
            "name": "Suresh Kumar's Farm",
            "area_ha": 3.2,
            "description": "Rice, Banana, Coconut cultivation",
        },
    ]
    
    for i, farm_data in enumerate(farm_data):
        farm = Farm(farmer_id=farmers[i].id, **farm_data)
        session.add(farm)
        farms.append(farm)
    
    await session.commit()
    return farms


async def create_demo_fields(session: AsyncSession, farms: list[Farm], crops: list[Crop], soils: list[Soil]) -> list[Field]:
    """Create demo fields."""
    fields = []
    
    field_data = [
        {
            "name": "പാട്ട കൃഷി",
            "crop": "Rice",
            "variety": "Jyothi",
            "sow_date": datetime.utcnow() - timedelta(days=30),
            "area_ha": 1.0,
        },
        {
            "name": "വാഴ കൃഷി",
            "crop": "Banana",
            "variety": "Nendran",
            "sow_date": datetime.utcnow() - timedelta(days=180),
            "area_ha": 0.8,
        },
        {
            "name": "കാട്ടുകുരുമ കൃഷി",
            "crop": "Brinjal",
            "variety": "Pusa Purple",
            "sow_date": datetime.utcnow() - timedelta(days=45),
            "area_ha": 0.7,
        },
    ]
    
    for i, field_data in enumerate(field_data):
        field = Field(
            farm_id=farms[i].id,
            soil_id=soils[i].id,
            **field_data
        )
        session.add(field)
        fields.append(field)
    
    await session.commit()
    return fields


async def create_demo_activities(session: AsyncSession, farmers: list[Farmer], fields: list[Field]) -> list[Activity]:
    """Create demo activities."""
    activities = []
    
    activity_data = [
        {
            "kind": ActivityKind.SOWING,
            "text_raw": "നാളെ പാട്ട നടാം",
            "text_processed": "നാളെ പാട്ട നടാം",
            "data_json": json.dumps({
                "crop": "പാട്ട",
                "activity": "നടൽ",
                "date": "നാളെ",
                "quantity": None,
                "unit": None,
            }),
            "language": "ml-IN",
            "confidence_score": 85,
        },
        {
            "kind": ActivityKind.IRRIGATION,
            "text_raw": "വാഴക്ക് വെള്ളം കൊടുത്തു",
            "text_processed": "വാഴക്ക് വെള്ളം കൊടുത്തു",
            "data_json": json.dumps({
                "crop": "വാഴ",
                "activity": "വെള്ളം കൊടുക്കൽ",
                "quantity": None,
                "unit": None,
            }),
            "language": "ml-IN",
            "confidence_score": 90,
        },
        {
            "kind": ActivityKind.FERTILIZER,
            "text_raw": "Applied NPK fertilizer to brinjal field",
            "text_processed": "Applied NPK fertilizer to brinjal field",
            "data_json": json.dumps({
                "crop": "brinjal",
                "activity": "fertilizer_application",
                "fertilizer_type": "NPK",
                "quantity": None,
                "unit": None,
            }),
            "language": "en",
            "confidence_score": 88,
        },
    ]
    
    for i, activity_data in enumerate(activity_data):
        activity = Activity(
            farmer_id=farmers[i].id,
            field_id=fields[i].id,
            **activity_data
        )
        session.add(activity)
        activities.append(activity)
    
    await session.commit()
    return activities


async def create_demo_advisories(session: AsyncSession, farmers: list[Farmer], fields: list[Field]) -> list[Advisory]:
    """Create demo advisories."""
    advisories = []
    
    advisory_data = [
        {
            "title": "മഴ പ്രതീക്ഷിക്കുന്നു",
            "title_ml": "മഴ പ്രതീക്ഷിക്കുന്നു",
            "text": "നാളെ മഴ പ്രതീക്ഷിക്കുന്നു. തളിക്കൽ ഒഴിവാക്കുക.",
            "text_ml": "നാളെ മഴ പ്രതീക്ഷിക്കുന്നു. തളിക്കൽ ഒഴിവാക്കുക.",
            "severity": AdvisorySeverity.MEDIUM,
            "tags": json.dumps(["weather", "spraying", "rain"]),
            "source": AdvisorySource.WEATHER,
            "source_data": json.dumps({"rain_forecast": 15, "wind_speed": 8}),
        },
        {
            "title": "കീട ശ്രദ്ധ",
            "title_ml": "കീട ശ്രദ്ധ",
            "text": "വാഴ ഇലക്കീടം കാണാൻ തുടങ്ങിയിരിക്കുന്നു. നിരീക്ഷണം നടത്തുക.",
            "text_ml": "വാഴ ഇലക്കീടം കാണാൻ തുടങ്ങിയിരിക്കുന്നു. നിരീക്ഷണം നടത്തുക.",
            "severity": AdvisorySeverity.HIGH,
            "tags": json.dumps(["pest", "banana", "monitoring"]),
            "source": AdvisorySource.PEST_ALERT,
            "source_data": json.dumps({"pest": "banana_leaf_hopper", "severity": "high"}),
        },
        {
            "title": "Harvest Time",
            "title_ml": "വിളവെടുപ്പ് സമയം",
            "text": "Rice is ready for harvest. Plan harvesting activities.",
            "text_ml": "പാട്ട വിളവെടുപ്പിന് തയ്യാറാണ്. വിളവെടുപ്പ് പദ്ധതിയാക്കുക.",
            "severity": AdvisorySeverity.LOW,
            "tags": json.dumps(["harvest", "rice", "timing"]),
            "source": AdvisorySource.CROP_CALENDAR,
            "source_data": json.dumps({"crop_stage": "maturity", "days_since_sowing": 120}),
        },
    ]
    
    for i, advisory_data in enumerate(advisory_data):
        advisory = Advisory(
            farmer_id=farmers[i].id,
            field_id=fields[i].id,
            **advisory_data
        )
        session.add(advisory)
        advisories.append(advisory)
    
    await session.commit()
    return advisories


async def create_demo_weather_data(session: AsyncSession) -> list[WeatherObs]:
    """Create demo weather observations."""
    weather_obs = []
    
    districts = ["തൃശൂർ", "കോഴിക്കോട്", "Ernakulam"]
    
    for district in districts:
        for i in range(7):  # Last 7 days
            obs = WeatherObs(
                district=district,
                timestamp=datetime.utcnow() - timedelta(days=i),
                temp_c=28 + (i % 3) * 2,
                temp_min_c=22 + (i % 3),
                temp_max_c=32 + (i % 3) * 2,
                humidity=75 + (i % 2) * 10,
                wind_speed_ms=3 + (i % 2) * 2,
                wind_direction=180 + (i % 4) * 45,
                pressure_hpa=1013 + (i % 3),
                rain_mm=0 if i % 3 != 0 else 5 + (i % 2) * 3,
                rain_24h_mm=0 if i % 3 != 0 else 8 + (i % 2) * 5,
                visibility_km=10,
                uv_index=6 + (i % 2),
                cloud_cover=30 + (i % 3) * 20,
                source=WeatherSource.OPENWEATHER,
                source_data=json.dumps({"station_id": f"station_{district}_{i}"}),
            )
            session.add(obs)
            weather_obs.append(obs)
    
    await session.commit()
    return weather_obs


async def create_demo_pest_reports(session: AsyncSession) -> list[PestReport]:
    """Create demo pest reports."""
    pest_reports = []
    
    pest_data = [
        {
            "crop": "Rice",
            "pest_name": "Brown Plant Hopper",
            "pest_name_ml": "തവിട്ട് ചെടി ഹോപ്പർ",
            "scientific_name": "Nilaparvata lugens",
            "district": "തൃശൂർ",
            "severity": PestSeverity.HIGH,
            "affected_area_ha": 50,
            "damage_percentage": 15,
            "stage": "flowering",
            "symptoms": "Yellowing of leaves, stunted growth",
            "symptoms_ml": "ഇലകൾ മഞ്ഞയാകൽ, വളർച്ച കുറവ്",
            "control_measures": "Apply neem oil, remove affected plants",
            "control_measures_ml": "വേപ്പെണ്ണ പുരട്ടുക, ബാധിത സസ്യങ്ങൾ നീക്കുക",
            "source": "field_survey",
        },
        {
            "crop": "Banana",
            "pest_name": "Banana Aphid",
            "pest_name_ml": "വാഴ അഫിഡ്",
            "scientific_name": "Pentalonia nigronervosa",
            "district": "കോഴിക്കോട്",
            "severity": PestSeverity.MEDIUM,
            "affected_area_ha": 25,
            "damage_percentage": 8,
            "stage": "vegetative",
            "symptoms": "Curling of leaves, honeydew secretion",
            "symptoms_ml": "ഇലകൾ ചുരുങ്ങൽ, തേൻ ദ്രവം സ്രവണം",
            "control_measures": "Spray soap solution, introduce natural predators",
            "control_measures_ml": "സോപ്പ് ലായനി തളിക്കുക, പ്രകൃതി ശത്രുക്കളെ അവതരിപ്പിക്കുക",
            "source": "farmer_report",
        },
    ]
    
    for pest_data in pest_data:
        pest_report = PestReport(**pest_data)
        session.add(pest_report)
        pest_reports.append(pest_report)
    
    await session.commit()
    return pest_reports


async def create_demo_price_data(session: AsyncSession) -> list[PricePoint]:
    """Create demo price data."""
    price_points = []
    
    markets = ["തൃശൂർ മാർക്കറ്റ്", "കോഴിക്കോട് മാർക്കറ്റ്", "Kochi Market"]
    commodities = ["Rice", "Banana", "Brinjal"]
    
    for market in markets:
        for commodity in commodities:
            for i in range(5):  # Last 5 days
                price_point = PricePoint(
                    market=market,
                    market_ml=market if "മാർക്കറ്റ്" in market else f"{market} മാർക്കറ്റ്",
                    commodity=commodity,
                    commodity_ml={
                        "Rice": "പാട്ട",
                        "Banana": "വാഴ",
                        "Brinjal": "കാട്ടുകുരുമ",
                    }.get(commodity, commodity),
                    timestamp=datetime.utcnow() - timedelta(days=i),
                    min_price=20 + (i % 3) * 2,
                    max_price=30 + (i % 3) * 3,
                    modal_price=25 + (i % 3) * 2,
                    avg_price=24 + (i % 3) * 2,
                    unit="kg",
                    quantity=1000 + (i % 5) * 200,
                    quality="A",
                    source=PriceSource.MARKET,
                    source_data=json.dumps({"market_id": f"market_{market}_{i}"}),
                )
                session.add(price_point)
                price_points.append(price_point)
    
    await session.commit()
    return price_points


async def create_demo_knowledge_base(session: AsyncSession) -> list[Doc]:
    """Create demo knowledge base documents."""
    docs = []
    
    doc_data = [
        {
            "title": "പാട്ട കൃഷി മാർഗ്ഗനിർദ്ദേശങ്ങൾ",
            "title_ml": "പാട്ട കൃഷി മാർഗ്ഗനിർദ്ദേശങ്ങൾ",
            "source": DocSource.SYSTEM,
            "doc_type": DocType.TEXT,
            "content": "പാട്ട കൃഷിയിൽ ശ്രദ്ധിക്കേണ്ട കാര്യങ്ങൾ:\n1. മണ്ണ് തയ്യാറാക്കൽ\n2. വിത്ത് തിരഞ്ഞെടുക്കൽ\n3. നടൽ\n4. വെള്ളം കൊടുക്കൽ\n5. വളപ്രയോഗം\n6. കീടനിയന്ത്രണം\n7. വിളവെടുപ്പ്",
            "summary": "പാട്ട കൃഷിയുടെ പ്രധാന ഘട്ടങ്ങൾ",
            "summary_ml": "പാട്ട കൃഷിയുടെ പ്രധാന ഘട്ടങ്ങൾ",
            "language": "ml-IN",
            "meta_json": json.dumps({"category": "crop_guide", "crop": "rice"}),
        },
        {
            "title": "വാഴ കൃഷി കാലാവസ്ഥാ മാർഗ്ഗനിർദ്ദേശങ്ങൾ",
            "title_ml": "വാഴ കൃഷി കാലാവസ്ഥാ മാർഗ്ഗനിർദ്ദേശങ്ങൾ",
            "source": DocSource.SYSTEM,
            "doc_type": DocType.TEXT,
            "content": "വാഴ കൃഷിയിൽ കാലാവസ്ഥയുടെ സ്വാധീനം:\n1. മഴ - അധികമായാൽ വേര് കുഴയും\n2. കാറ്റ് - ഉയർന്ന കാറ്റ് ചെടികൾ തകർക്കും\n3. താപനില - 25-35°C ആദർശം\n4. ആർദ്രത - 60-80% ആദർശം",
            "summary": "വാഴ കൃഷിയിൽ കാലാവസ്ഥാ ഘടകങ്ങൾ",
            "summary_ml": "വാഴ കൃഷിയിൽ കാലാവസ്ഥാ ഘടകങ്ങൾ",
            "language": "ml-IN",
            "meta_json": json.dumps({"category": "weather_guide", "crop": "banana"}),
        },
        {
            "title": "കാട്ടുകുരുമ കീടനിയന്ത്രണം",
            "title_ml": "കാട്ടുകുരുമ കീടനിയന്ത്രണം",
            "source": DocSource.SYSTEM,
            "doc_type": DocType.TEXT,
            "content": "കാട്ടുകുരുമ കീടങ്ങൾ:\n1. ഫലം കുത്തി - ഫലത്തിൽ ദ്വാരങ്ങൾ\n2. അഫിഡ് - ഇലകൾ ചുരുങ്ങൽ\n3. വൈറ്റ് ഫ്ലൈ - ഇലകൾ മഞ്ഞയാകൽ\n\nനിയന്ത്രണ മാർഗ്ഗങ്ങൾ:\n1. ജൈവ കീടനാശിനി\n2. നീം എണ്ണ\n3. പ്രകൃതി ശത്രുക്കൾ",
            "summary": "കാട്ടുകുരുമ കീടങ്ങളും നിയന്ത്രണ മാർഗ്ഗങ്ങളും",
            "summary_ml": "കാട്ടുകുരുമ കീടങ്ങളും നിയന്ത്രണ മാർഗ്ഗങ്ങളും",
            "language": "ml-IN",
            "meta_json": json.dumps({"category": "pest_control", "crop": "brinjal"}),
        },
    ]
    
    for doc_data in doc_data:
        doc = Doc(**doc_data)
        session.add(doc)
        docs.append(doc)
    
    await session.commit()
    return docs


async def create_demo_consents(session: AsyncSession, users: list[User]) -> list[Consent]:
    """Create demo consent records."""
    consents = []
    
    for user in users:
        if user.role == UserRole.FARMER:
            consent_data = [
                {
                    "kind": ConsentKind.DATA_PROCESSING,
                    "granted": True,
                    "purpose": "Provide personalized farming advice and services",
                    "purpose_ml": "വ്യക്തിഗത കൃഷി ഉപദേശങ്ങളും സേവനങ്ങളും നൽകാൻ",
                    "legal_basis": "Consent",
                    "retention_period": "7 years",
                },
                {
                    "kind": ConsentKind.NOTIFICATIONS,
                    "granted": True,
                    "purpose": "Send farming alerts and reminders",
                    "purpose_ml": "കൃഷി അലേർട്ടുകളും ഓർമ്മപ്പെടുത്തലുകളും അയയ്ക്കാൻ",
                    "legal_basis": "Consent",
                    "retention_period": "Until revoked",
                },
                {
                    "kind": ConsentKind.LOCATION,
                    "granted": True,
                    "purpose": "Provide location-based weather and pest alerts",
                    "purpose_ml": "സ്ഥാനാധിഷ്ഠിത കാലാവസ്ഥാ, കീട അലേർട്ടുകൾ നൽകാൻ",
                    "legal_basis": "Consent",
                    "retention_period": "7 years",
                },
            ]
            
            for consent_data in consent_data:
                consent = Consent(
                    user_id=user.id,
                    **consent_data
                )
                session.add(consent)
                consents.append(consent)
    
    await session.commit()
    return consents


async def main():
    """Main seed function."""
    print("🌱 Starting demo data seeding...")
    
    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        try:
            # Create demo data
            print("👥 Creating demo users...")
            users = await create_demo_users(session)
            
            print("🌾 Creating demo farmers...")
            farmers = await create_demo_farmers(session, users)
            
            print("🌱 Creating demo crops...")
            crops = await create_demo_crops(session)
            
            print("🏞️ Creating demo soils...")
            soils = await create_demo_soils(session)
            
            print("🚜 Creating demo farms...")
            farms = await create_demo_farms(session, farmers)
            
            print("🌾 Creating demo fields...")
            fields = await create_demo_fields(session, farms, crops, soils)
            
            print("📝 Creating demo activities...")
            activities = await create_demo_activities(session, farmers, fields)
            
            print("💡 Creating demo advisories...")
            advisories = await create_demo_advisories(session, farmers, fields)
            
            print("🌤️ Creating demo weather data...")
            weather_obs = await create_demo_weather_data(session)
            
            print("🐛 Creating demo pest reports...")
            pest_reports = await create_demo_pest_reports(session)
            
            print("💰 Creating demo price data...")
            price_points = await create_demo_price_data(session)
            
            print("📚 Creating demo knowledge base...")
            docs = await create_demo_knowledge_base(session)
            
            print("✅ Creating demo consents...")
            consents = await create_demo_consents(session, users)
            
            print(f"✅ Demo data seeding completed successfully!")
            print(f"   - {len(users)} users created")
            print(f"   - {len(farmers)} farmers created")
            print(f"   - {len(crops)} crops created")
            print(f"   - {len(soils)} soils created")
            print(f"   - {len(farms)} farms created")
            print(f"   - {len(fields)} fields created")
            print(f"   - {len(activities)} activities created")
            print(f"   - {len(advisories)} advisories created")
            print(f"   - {len(weather_obs)} weather observations created")
            print(f"   - {len(pest_reports)} pest reports created")
            print(f"   - {len(price_points)} price points created")
            print(f"   - {len(docs)} knowledge base documents created")
            print(f"   - {len(consents)} consent records created")
            
        except Exception as e:
            print(f"❌ Error seeding demo data: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
