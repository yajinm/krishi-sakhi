"""
Provider interfaces and adapters.

Provides pluggable interfaces for external services like ASR, TTS, Weather, NLU, etc.
"""

from app.providers.asr import ASRProvider, DummyASRProvider, WhisperASRProvider
from app.providers.tts import TTSProvider, DummyTTSProvider, AzureTTSProvider
from app.providers.weather import WeatherProvider, DummyWeatherProvider, OpenWeatherProvider
from app.providers.nlu import NLUProvider, DummyNLUProvider, RuleBasedNLUProvider
from app.providers.embed import EmbeddingProvider, SentenceTransformerProvider
from app.providers.llm import LLMProvider, LocalRuleLLMProvider, OpenAILLMProvider
from app.providers.notify import NotificationProvider, ConsoleNotificationProvider, TwilioNotificationProvider
from app.providers.pest import PestProvider, CSVPestProvider
from app.providers.prices import PriceProvider, CSVPriceProvider

__all__ = [
    # ASR
    "ASRProvider",
    "DummyASRProvider", 
    "WhisperASRProvider",
    # TTS
    "TTSProvider",
    "DummyTTSProvider",
    "AzureTTSProvider",
    # Weather
    "WeatherProvider",
    "DummyWeatherProvider",
    "OpenWeatherProvider",
    # NLU
    "NLUProvider",
    "DummyNLUProvider",
    "RuleBasedNLUProvider",
    # Embedding
    "EmbeddingProvider",
    "SentenceTransformerProvider",
    # LLM
    "LLMProvider",
    "LocalRuleLLMProvider",
    "OpenAILLMProvider",
    # Notification
    "NotificationProvider",
    "ConsoleNotificationProvider",
    "TwilioNotificationProvider",
    # Pest
    "PestProvider",
    "CSVPestProvider",
    # Price
    "PriceProvider",
    "CSVPriceProvider",
]
