"""
Rules engine for advisory generation.

Provides rule evaluation and advisory generation based on context.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from app.models import Farmer, Field, Advisory, AdvisorySeverity, AdvisorySource


class RuleEngine:
    """Rule engine for generating advisories."""
    
    def __init__(self):
        self.rules = []
        self.facts = {}
    
    def add_rule(self, rule: 'Rule'):
        """Add a rule to the engine."""
        self.rules.append(rule)
    
    def set_facts(self, facts: Dict[str, Any]):
        """Set facts for rule evaluation."""
        self.facts = facts
    
    def evaluate_rules(self) -> List[Dict[str, Any]]:
        """Evaluate all rules and return advisories."""
        advisories = []
        
        for rule in self.rules:
            if rule.evaluate(self.facts):
                advisory = rule.generate_advisory(self.facts)
                if advisory:
                    advisories.append(advisory)
        
        return advisories


class Rule:
    """Base rule class."""
    
    def __init__(self, name: str, priority: int = 100):
        self.name = name
        self.priority = priority
    
    def evaluate(self, facts: Dict[str, Any]) -> bool:
        """Evaluate rule against facts."""
        raise NotImplementedError
    
    def generate_advisory(self, facts: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate advisory if rule matches."""
        raise NotImplementedError


class WeatherRule(Rule):
    """Rule for weather-based advisories."""
    
    def __init__(self, name: str, condition: str, advisory_text: str, severity: AdvisorySeverity):
        super().__init__(name)
        self.condition = condition
        self.advisory_text = advisory_text
        self.severity = severity
    
    def evaluate(self, facts: Dict[str, Any]) -> bool:
        """Evaluate weather condition."""
        weather = facts.get('weather', {})
        
        if self.condition == 'rain_forecast':
            return weather.get('rain_24h_mm', 0) > 10
        
        elif self.condition == 'high_wind':
            return weather.get('wind_speed_ms', 0) > 6
        
        elif self.condition == 'high_temperature':
            return weather.get('temp_max_c', 0) > 35
        
        elif self.condition == 'low_temperature':
            return weather.get('temp_min_c', 0) < 20
        
        return False
    
    def generate_advisory(self, facts: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate weather advisory."""
        return {
            'title': f"Weather Advisory - {self.name}",
            'text': self.advisory_text,
            'severity': self.severity.value,
            'source': AdvisorySource.WEATHER.value,
            'tags': ['weather', self.condition],
            'metadata': {
                'rule_name': self.name,
                'condition': self.condition,
                'weather_data': facts.get('weather', {}),
            }
        }


class PestRule(Rule):
    """Rule for pest-based advisories."""
    
    def __init__(self, name: str, crop: str, pest_name: str, severity: AdvisorySeverity):
        super().__init__(name)
        self.crop = crop
        self.pest_name = pest_name
        self.severity = severity
    
    def evaluate(self, facts: Dict[str, Any]) -> bool:
        """Evaluate pest condition."""
        pest_reports = facts.get('pest_reports', [])
        farmer_crops = facts.get('farmer_crops', [])
        
        # Check if farmer has the affected crop
        if self.crop not in farmer_crops:
            return False
        
        # Check for recent pest reports
        for report in pest_reports:
            if (report.get('crop') == self.crop and 
                report.get('pest_name') == self.pest_name and
                report.get('severity') in ['high', 'critical']):
                return True
        
        return False
    
    def generate_advisory(self, facts: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate pest advisory."""
        return {
            'title': f"Pest Alert - {self.pest_name}",
            'text': f"{self.pest_name} detected in {self.crop}. Please take immediate action.",
            'severity': self.severity.value,
            'source': AdvisorySource.PEST_ALERT.value,
            'tags': ['pest', self.crop, self.pest_name],
            'metadata': {
                'rule_name': self.name,
                'crop': self.crop,
                'pest_name': self.pest_name,
                'pest_reports': facts.get('pest_reports', []),
            }
        }


class CropStageRule(Rule):
    """Rule for crop stage-based advisories."""
    
    def __init__(self, name: str, crop: str, stage: str, advisory_text: str):
        super().__init__(name)
        self.crop = crop
        self.stage = stage
        self.advisory_text = advisory_text
    
    def evaluate(self, facts: Dict[str, Any]) -> bool:
        """Evaluate crop stage."""
        fields = facts.get('fields', [])
        
        for field in fields:
            if (field.get('crop') == self.crop and 
                field.get('stage') == self.stage):
                return True
        
        return False
    
    def generate_advisory(self, facts: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate crop stage advisory."""
        return {
            'title': f"Crop Stage Advisory - {self.crop}",
            'text': self.advisory_text,
            'severity': AdvisorySeverity.MEDIUM.value,
            'source': AdvisorySource.CROP_CALENDAR.value,
            'tags': ['crop_stage', self.crop, self.stage],
            'metadata': {
                'rule_name': self.name,
                'crop': self.crop,
                'stage': self.stage,
                'fields': facts.get('fields', []),
            }
        }


def create_default_rules() -> List[Rule]:
    """Create default rules for the system."""
    rules = []
    
    # Weather rules
    rules.append(WeatherRule(
        name="Rain Advisory",
        condition="rain_forecast",
        advisory_text="മഴ പ്രതീക്ഷിക്കുന്നു. തളിക്കൽ ഒഴിവാക്കുക.",
        severity=AdvisorySeverity.MEDIUM
    ))
    
    rules.append(WeatherRule(
        name="Wind Advisory",
        condition="high_wind",
        advisory_text="ഉയർന്ന കാറ്റ്. തളിക്കൽ താമസിപ്പിക്കുക.",
        severity=AdvisorySeverity.MEDIUM
    ))
    
    rules.append(WeatherRule(
        name="Heat Advisory",
        condition="high_temperature",
        advisory_text="ഉയർന്ന താപനില. ജലസേചനം വർദ്ധിപ്പിക്കുക.",
        severity=AdvisorySeverity.HIGH
    ))
    
    # Pest rules
    rules.append(PestRule(
        name="Rice Blast Alert",
        crop="Rice",
        pest_name="Rice Blast",
        severity=AdvisorySeverity.HIGH
    ))
    
    rules.append(PestRule(
        name="Banana Aphid Alert",
        crop="Banana",
        pest_name="Banana Aphid",
        severity=AdvisorySeverity.MEDIUM
    ))
    
    # Crop stage rules
    rules.append(CropStageRule(
        name="Rice Harvest Time",
        crop="Rice",
        stage="maturity",
        advisory_text="പാട്ട വിളവെടുപ്പിന് തയ്യാറാണ്. വിളവെടുപ്പ് പദ്ധതിയാക്കുക."
    ))
    
    return rules
