"""
Natural Language Understanding (NLU) providers.

Provides interfaces and implementations for intent recognition and entity extraction.
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from app.config import settings


class NLUProvider(ABC):
    """Abstract base class for NLU providers."""
    
    @abstractmethod
    async def process_text(self, text: str, language: str = "ml-IN") -> Dict[str, any]:
        """
        Process text to extract intents and entities.
        
        Args:
            text: Input text
            language: Language code
            
        Returns:
            Dictionary with NLU results
        """
        pass


class DummyNLUProvider(NLUProvider):
    """Dummy NLU provider for development and testing."""
    
    def __init__(self):
        self.intent_keywords = {
            "ml-IN": {
                "log_activity": ["നടൽ", "തളിക്കൽ", "വെള്ളം", "വളം", "വിളവെടുപ്പ്", "കൃഷി"],
                "ask_kb": ["എന്ത്", "എങ്ങനെ", "എപ്പോൾ", "എവിടെ", "എന്തുകൊണ്ട്", "സഹായം"],
                "request_advice": ["ഉപദേശം", "സഹായം", "എന്ത് ചെയ്യണം", "എങ്ങനെ ചെയ്യണം"],
                "smalltalk_other": ["നമസ്കാരം", "ഹലോ", "ധന്യവാദം", "വിട"],
            },
            "en": {
                "log_activity": ["plant", "sow", "water", "fertilizer", "pesticide", "harvest", "farming"],
                "ask_kb": ["what", "how", "when", "where", "why", "help"],
                "request_advice": ["advice", "help", "what to do", "how to"],
                "smalltalk_other": ["hello", "hi", "thanks", "bye"],
            },
        }
        
        self.entity_patterns = {
            "ml-IN": {
                "crop": r"(പാട്ട|വാഴ|കാട്ടുകുരുമ|കുരുമ|കോഴിക്കോട്|തക്കാളി)",
                "activity": r"(നടൽ|തളിക്കൽ|വെള്ളം|വളം|വിളവെടുപ്പ്|കീടനാശിനി)",
                "quantity": r"(\d+)\s*(കിലോ|ലിറ്റർ|ഗ്രാം|കിലോഗ്രാം)",
                "time": r"(നാളെ|ഇന്ന്|ഇന്നലെ|ഈ ആഴ്ച|അടുത്ത ആഴ്ച)",
            },
            "en": {
                "crop": r"(rice|banana|brinjal|tomato|coconut)",
                "activity": r"(plant|sow|water|fertilizer|pesticide|harvest)",
                "quantity": r"(\d+)\s*(kg|liter|gram|kilogram)",
                "time": r"(tomorrow|today|yesterday|this week|next week)",
            },
        }
    
    async def process_text(self, text: str, language: str = "ml-IN") -> Dict[str, any]:
        """Process text using dummy NLU."""
        text_lower = text.lower()
        
        # Detect intent
        intent = self._detect_intent(text_lower, language)
        
        # Extract entities
        entities = self._extract_entities(text, language)
        
        # Calculate confidence
        confidence = self._calculate_confidence(text_lower, intent, language)
        
        return {
            "intent": intent,
            "entities": entities,
            "confidence": confidence,
            "language": language,
            "text": text,
            "provider": "dummy",
        }
    
    def _detect_intent(self, text: str, language: str) -> str:
        """Detect intent from text."""
        keywords = self.intent_keywords.get(language, self.intent_keywords["en"])
        
        # Count keyword matches for each intent
        intent_scores = {}
        for intent, intent_keywords in keywords.items():
            score = sum(1 for keyword in intent_keywords if keyword in text)
            if score > 0:
                intent_scores[intent] = score
        
        # Return intent with highest score
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return "smalltalk_other"
    
    def _extract_entities(self, text: str, language: str) -> Dict[str, List[str]]:
        """Extract entities from text."""
        entities = {}
        patterns = self.entity_patterns.get(language, self.entity_patterns["en"])
        
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        
        return entities
    
    def _calculate_confidence(self, text: str, intent: str, language: str) -> float:
        """Calculate confidence score."""
        keywords = self.intent_keywords.get(language, self.intent_keywords["en"])
        intent_keywords = keywords.get(intent, [])
        
        if not intent_keywords:
            return 0.5
        
        # Count keyword matches
        matches = sum(1 for keyword in intent_keywords if keyword in text)
        confidence = min(matches / len(intent_keywords), 1.0)
        
        return confidence


class RuleBasedNLUProvider(NLUProvider):
    """Rule-based NLU provider with more sophisticated patterns."""
    
    def __init__(self):
        self.dummy_provider = DummyNLUProvider()
        
        # More sophisticated patterns
        self.patterns = {
            "ml-IN": {
                "log_activity": [
                    r"(.+?)\s+(നടൽ|തളിക്കൽ|വെള്ളം|വളം|വിളവെടുപ്പ്)",
                    r"(നാളെ|ഇന്ന്|ഇന്നലെ)\s+(.+?)\s+(ചെയ്യണം|ചെയ്തു)",
                ],
                "ask_kb": [
                    r"(.+?)\s+(എന്ത്|എങ്ങനെ|എപ്പോൾ|എവിടെ)",
                    r"(.+?)\s+(സഹായം|ഉപദേശം)",
                ],
            },
            "en": {
                "log_activity": [
                    r"(.+?)\s+(plant|sow|water|fertilizer|pesticide|harvest)",
                    r"(tomorrow|today|yesterday)\s+(.+?)\s+(need to do|did)",
                ],
                "ask_kb": [
                    r"(.+?)\s+(what|how|when|where)",
                    r"(.+?)\s+(help|advice)",
                ],
            },
        }
    
    async def process_text(self, text: str, language: str = "ml-IN") -> Dict[str, any]:
        """Process text using rule-based NLU."""
        # Try sophisticated patterns first
        result = self._process_with_patterns(text, language)
        
        if result["confidence"] > 0.7:
            return result
        
        # Fallback to dummy provider
        return await self.dummy_provider.process_text(text, language)
    
    def _process_with_patterns(self, text: str, language: str) -> Dict[str, any]:
        """Process text using sophisticated patterns."""
        patterns = self.patterns.get(language, self.patterns["en"])
        
        best_intent = "smalltalk_other"
        best_confidence = 0.0
        entities = {}
        
        for intent, intent_patterns in patterns.items():
            for pattern in intent_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    confidence = len(match.groups()) / len(intent_patterns)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_intent = intent
                        entities = self._extract_entities_from_match(match, intent)
        
        return {
            "intent": best_intent,
            "entities": entities,
            "confidence": best_confidence,
            "language": language,
            "text": text,
            "provider": "rule_based",
        }
    
    def _extract_entities_from_match(self, match, intent: str) -> Dict[str, List[str]]:
        """Extract entities from regex match."""
        entities = {}
        
        if intent == "log_activity":
            groups = match.groups()
            if len(groups) >= 2:
                entities["crop"] = [groups[0].strip()]
                entities["activity"] = [groups[1].strip()]
        
        return entities


class FastTextNLUProvider(NLUProvider):
    """FastText-based NLU provider for better accuracy."""
    
    def __init__(self):
        self.dummy_provider = DummyNLUProvider()
        self.model_path = "/models/fasttext_model.bin"
        self.model = None
    
    async def process_text(self, text: str, language: str = "ml-IN") -> Dict[str, any]:
        """Process text using FastText model."""
        try:
            # Load model if not loaded
            if not self.model:
                import fasttext
                if Path(self.model_path).exists():
                    self.model = fasttext.load_model(self.model_path)
                else:
                    # Fallback to dummy provider
                    return await self.dummy_provider.process_text(text, language)
            
            # Predict intent
            prediction = self.model.predict(text)
            intent = prediction[0][0].replace("__label__", "")
            confidence = float(prediction[1][0])
            
            # Extract entities using patterns
            entities = self.dummy_provider._extract_entities(text, language)
            
            return {
                "intent": intent,
                "entities": entities,
                "confidence": confidence,
                "language": language,
                "text": text,
                "provider": "fasttext",
            }
            
        except Exception as e:
            # Fallback to dummy provider
            return await self.dummy_provider.process_text(text, language)


def get_nlu_provider() -> NLUProvider:
    """Get NLU provider based on configuration."""
    # For now, return rule-based provider
    # In production, this would check settings
    return RuleBasedNLUProvider()
