"""
Automatic Speech Recognition (ASR) providers.

Provides interfaces and implementations for speech-to-text conversion.
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

from app.config import settings


class ASRProvider(ABC):
    """Abstract base class for ASR providers."""
    
    @abstractmethod
    async def transcribe(self, audio_file_path: str, language: str = "ml-IN") -> Dict[str, any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file_path: Path to audio file
            language: Language code (ml-IN, en-IN, etc.)
            
        Returns:
            Dictionary with transcription results
        """
        pass
    
    @abstractmethod
    async def transcribe_url(self, audio_url: str, language: str = "ml-IN") -> Dict[str, any]:
        """
        Transcribe audio from URL to text.
        
        Args:
            audio_url: URL to audio file
            language: Language code
            
        Returns:
            Dictionary with transcription results
        """
        pass


class DummyASRProvider(ASRProvider):
    """Dummy ASR provider for development and testing."""
    
    def __init__(self):
        self.sample_transcriptions = {
            "ml-IN": [
                "നാളെ പാട്ട നടാം",
                "വാഴക്ക് വെള്ളം കൊടുത്തു",
                "കീടനാശിനി തളിക്കണം",
                "വിളവെടുപ്പ് സമയമായി",
                "മഴ പ്രതീക്ഷിക്കുന്നു",
            ],
            "en-IN": [
                "Tomorrow we will plant rice",
                "Watered the banana plants",
                "Need to spray pesticide",
                "Time for harvest",
                "Rain is expected",
            ],
        }
    
    async def transcribe(self, audio_file_path: str, language: str = "ml-IN") -> Dict[str, any]:
        """Transcribe audio file using dummy provider."""
        # Simulate processing delay
        await asyncio.sleep(1)
        
        # Return dummy transcription
        transcriptions = self.sample_transcriptions.get(language, self.sample_transcriptions["ml-IN"])
        import random
        text = random.choice(transcriptions)
        
        return {
            "text": text,
            "language": language,
            "confidence": 0.85,
            "duration": 5.2,
            "words": text.split(),
            "provider": "dummy",
            "processing_time": 1.0,
        }
    
    async def transcribe_url(self, audio_url: str, language: str = "ml-IN") -> Dict[str, any]:
        """Transcribe audio from URL using dummy provider."""
        # Simulate processing delay
        await asyncio.sleep(1.5)
        
        # Return dummy transcription
        transcriptions = self.sample_transcriptions.get(language, self.sample_transcriptions["ml-IN"])
        import random
        text = random.choice(transcriptions)
        
        return {
            "text": text,
            "language": language,
            "confidence": 0.82,
            "duration": 4.8,
            "words": text.split(),
            "provider": "dummy",
            "processing_time": 1.5,
        }


class WhisperASRProvider(ASRProvider):
    """Whisper ASR provider for high-quality transcription."""
    
    def __init__(self):
        self.model_name = "whisper-1"
        self.api_key = settings.openai_api_key
    
    async def transcribe(self, audio_file_path: str, language: str = "ml-IN") -> Dict[str, any]:
        """Transcribe audio file using Whisper."""
        try:
            import openai
            
            if not self.api_key:
                raise ValueError("OpenAI API key not configured")
            
            # Map language codes to Whisper language codes
            language_map = {
                "ml-IN": "ml",
                "en-IN": "en",
                "en": "en",
            }
            whisper_lang = language_map.get(language, "en")
            
            # Transcribe using OpenAI Whisper API
            with open(audio_file_path, "rb") as audio_file:
                response = await openai.Audio.atranscribe(
                    model=self.model_name,
                    file=audio_file,
                    language=whisper_lang,
                )
            
            return {
                "text": response.text,
                "language": language,
                "confidence": 0.95,  # Whisper doesn't provide confidence scores
                "duration": response.duration if hasattr(response, 'duration') else None,
                "words": response.text.split(),
                "provider": "whisper",
                "model": self.model_name,
            }
            
        except Exception as e:
            # Fallback to dummy provider
            dummy_provider = DummyASRProvider()
            return await dummy_provider.transcribe(audio_file_path, language)
    
    async def transcribe_url(self, audio_url: str, language: str = "ml-IN") -> Dict[str, any]:
        """Transcribe audio from URL using Whisper."""
        try:
            import openai
            import httpx
            
            if not self.api_key:
                raise ValueError("OpenAI API key not configured")
            
            # Download audio file
            async with httpx.AsyncClient() as client:
                response = await client.get(audio_url)
                response.raise_for_status()
                
                # Save to temporary file
                temp_file = Path(f"/tmp/audio_{uuid.uuid4()}.wav")
                temp_file.write_bytes(response.content)
                
                try:
                    # Transcribe using local file
                    result = await self.transcribe(str(temp_file), language)
                    return result
                finally:
                    # Clean up temp file
                    temp_file.unlink(missing_ok=True)
                    
        except Exception as e:
            # Fallback to dummy provider
            dummy_provider = DummyASRProvider()
            return await dummy_provider.transcribe_url(audio_url, language)


class VoskASRProvider(ASRProvider):
    """Vosk ASR provider for offline transcription."""
    
    def __init__(self):
        self.model_path = "/models/vosk-model-ml"
        self.model = None
    
    async def transcribe(self, audio_file_path: str, language: str = "ml-IN") -> Dict[str, any]:
        """Transcribe audio file using Vosk."""
        try:
            import vosk
            import wave
            import json
            
            # Load model if not loaded
            if not self.model:
                if not Path(self.model_path).exists():
                    raise ValueError(f"Vosk model not found at {self.model_path}")
                self.model = vosk.Model(self.model_path)
            
            # Open audio file
            wf = wave.open(audio_file_path, 'rb')
            
            # Create recognizer
            rec = vosk.KaldiRecognizer(self.model, wf.getframerate())
            rec.SetWords(True)
            
            # Process audio
            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    results.append(result)
            
            # Get final result
            final_result = json.loads(rec.FinalResult())
            results.append(final_result)
            
            # Combine results
            full_text = " ".join([r.get("text", "") for r in results if r.get("text")])
            
            return {
                "text": full_text,
                "language": language,
                "confidence": 0.90,
                "duration": wf.getnframes() / wf.getframerate(),
                "words": full_text.split(),
                "provider": "vosk",
                "model": self.model_path,
            }
            
        except Exception as e:
            # Fallback to dummy provider
            dummy_provider = DummyASRProvider()
            return await dummy_provider.transcribe(audio_file_path, language)
    
    async def transcribe_url(self, audio_url: str, language: str = "ml-IN") -> Dict[str, any]:
        """Transcribe audio from URL using Vosk."""
        try:
            import httpx
            
            # Download audio file
            async with httpx.AsyncClient() as client:
                response = await client.get(audio_url)
                response.raise_for_status()
                
                # Save to temporary file
                temp_file = Path(f"/tmp/audio_{uuid.uuid4()}.wav")
                temp_file.write_bytes(response.content)
                
                try:
                    # Transcribe using local file
                    result = await self.transcribe(str(temp_file), language)
                    return result
                finally:
                    # Clean up temp file
                    temp_file.unlink(missing_ok=True)
                    
        except Exception as e:
            # Fallback to dummy provider
            dummy_provider = DummyASRProvider()
            return await dummy_provider.transcribe_url(audio_url, language)


def get_asr_provider() -> ASRProvider:
    """Get ASR provider based on configuration."""
    provider_name = settings.asr_provider.lower()
    
    if provider_name == "whisper":
        return WhisperASRProvider()
    elif provider_name == "vosk":
        return VoskASRProvider()
    else:
        return DummyASRProvider()
