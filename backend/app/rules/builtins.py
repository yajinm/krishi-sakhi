"""
Built-in rules for common advisory scenarios.

Provides predefined rules for weather, pest, and crop management.
"""

from app.rules.engine import RuleEngine, WeatherRule, PestRule, CropStageRule
from app.models import AdvisorySeverity


def get_builtin_rules() -> RuleEngine:
    """Get rule engine with built-in rules."""
    engine = RuleEngine()
    
    # Add all built-in rules
    rules = create_default_rules()
    for rule in rules:
        engine.add_rule(rule)
    
    return engine


def create_default_rules():
    """Create default built-in rules."""
    rules = []
    
    # Weather-based rules
    rules.extend([
        WeatherRule(
            name="Rain Advisory",
            condition="rain_forecast",
            advisory_text="മഴ പ്രതീക്ഷിക്കുന്നു. തളിക്കൽ ഒഴിവാക്കുക.",
            severity=AdvisorySeverity.MEDIUM
        ),
        WeatherRule(
            name="Wind Advisory", 
            condition="high_wind",
            advisory_text="ഉയർന്ന കാറ്റ്. തളിക്കൽ താമസിപ്പിക്കുക.",
            severity=AdvisorySeverity.MEDIUM
        ),
        WeatherRule(
            name="Heat Advisory",
            condition="high_temperature", 
            advisory_text="ഉയർന്ന താപനില. ജലസേചനം വർദ്ധിപ്പിക്കുക.",
            severity=AdvisorySeverity.HIGH
        ),
        WeatherRule(
            name="Cold Advisory",
            condition="low_temperature",
            advisory_text="താഴ്ന്ന താപനില. സസ്യ സംരക്ഷണം ആവശ്യമാണ്.",
            severity=AdvisorySeverity.MEDIUM
        ),
    ])
    
    # Pest-based rules
    rules.extend([
        PestRule(
            name="Rice Blast Alert",
            crop="Rice",
            pest_name="Rice Blast",
            severity=AdvisorySeverity.HIGH
        ),
        PestRule(
            name="Brown Plant Hopper Alert",
            crop="Rice", 
            pest_name="Brown Plant Hopper",
            severity=AdvisorySeverity.HIGH
        ),
        PestRule(
            name="Banana Aphid Alert",
            crop="Banana",
            pest_name="Banana Aphid", 
            severity=AdvisorySeverity.MEDIUM
        ),
        PestRule(
            name="Brinjal Fruit Borer Alert",
            crop="Brinjal",
            pest_name="Fruit Borer",
            severity=AdvisorySeverity.HIGH
        ),
    ])
    
    # Crop stage-based rules
    rules.extend([
        CropStageRule(
            name="Rice Harvest Time",
            crop="Rice",
            stage="maturity",
            advisory_text="പാട്ട വിളവെടുപ്പിന് തയ്യാറാണ്. വിളവെടുപ്പ് പദ്ധതിയാക്കുക."
        ),
        CropStageRule(
            name="Rice Transplanting Time",
            crop="Rice",
            stage="transplanting",
            advisory_text="പാട്ട നടാനുള്ള സമയമാണ്. നടൽ പദ്ധതിയാക്കുക."
        ),
        CropStageRule(
            name="Banana Harvest Time",
            crop="Banana",
            stage="maturity",
            advisory_text="വാഴ വിളവെടുപ്പിന് തയ്യാറാണ്. വിളവെടുപ്പ് പദ്ധതിയാക്കുക."
        ),
    ])
    
    return rules
