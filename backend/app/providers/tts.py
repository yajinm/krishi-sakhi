"""
Text-to-Speech (TTS) providers.

Provides interfaces and implementations for text-to-speech conversion.
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional

from app.config import settings


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""
    
    @abstractmethod
    async def synthesize(self, text: str, language: str = "ml-IN", voice: Optional[str] = None) -> Dict[str, any]:
        """
        Synthesize text to speech.
        
        Args:
            text: Text to synthesize
            language: Language code (ml-IN, en-IN, etc.)
            voice: Voice identifier (optional)
            
        Returns:
            Dictionary with synthesis results
        """
        pass


class DummyTTSProvider(TTSProvider):
    """Dummy TTS provider for development and testing."""
    
    def __init__(self):
        self.media_root = Path(settings.media_root)
        self.media_root.mkdir(parents=True, exist_ok=True)
    
    async def synthesize(self, text: str, language: str = "ml-IN", voice: Optional[str] = None) -> Dict[str, any]:
        """Synthesize text to speech using dummy provider."""
        # Simulate processing delay
        await asyncio.sleep(2)
        
        # Generate dummy audio file
        audio_filename = f"tts_{uuid.uuid4()}.wav"
        audio_path = self.media_root / "tts" / audio_filename
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a dummy WAV file (silence)
        self._create_dummy_wav(str(audio_path), duration=len(text) * 0.1)
        
        return {
            "audio_url": f"/media/tts/{audio_filename}",
            "audio_path": str(audio_path),
            "text": text,
            "language": language,
            "voice": voice or "default",
            "duration": len(text) * 0.1,
            "provider": "dummy",
            "processing_time": 2.0,
        }
    
    def _create_dummy_wav(self, file_path: str, duration: float = 1.0):
        """Create a dummy WAV file with silence."""
        import wave
        import struct
        
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        
        with wave.open(file_path, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # Write silence
            for _ in range(num_samples):
                wav_file.writeframes(struct.pack('<h', 0))


class AzureTTSProvider(TTSProvider):
    """Azure Cognitive Services TTS provider."""
    
    def __init__(self):
        self.speech_key = settings.azure_speech_key
        self.speech_region = settings.azure_speech_region
        self.media_root = Path(settings.media_root)
        self.media_root.mkdir(parents=True, exist_ok=True)
    
    async def synthesize(self, text: str, language: str = "ml-IN", voice: Optional[str] = None) -> Dict[str, any]:
        """Synthesize text to speech using Azure TTS."""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            if not self.speech_key or not self.speech_region:
                raise ValueError("Azure Speech credentials not configured")
            
            # Configure speech synthesis
            speech_config = speechsdk.SpeechConfig(
                subscription=self.speech_key,
                region=self.speech_region
            )
            
            # Set voice based on language
            voice_map = {
                "ml-IN": "ml-IN-MidhunNeural",
                "en-IN": "en-IN-NeerjaNeural",
                "en": "en-US-AriaNeural",
            }
            selected_voice = voice or voice_map.get(language, "en-US-AriaNeural")
            speech_config.speech_synthesis_voice_name = selected_voice
            
            # Generate audio file
            audio_filename = f"tts_{uuid.uuid4()}.wav"
            audio_path = self.media_root / "tts" / audio_filename
            audio_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Configure audio output
            audio_config = speechsdk.audio.AudioOutputConfig(filename=str(audio_path))
            
            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            
            # Synthesize
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return {
                    "audio_url": f"/media/tts/{audio_filename}",
                    "audio_path": str(audio_path),
                    "text": text,
                    "language": language,
                    "voice": selected_voice,
                    "duration": result.audio_duration.total_seconds(),
                    "provider": "azure",
                    "processing_time": 1.5,
                }
            else:
                raise Exception(f"Speech synthesis failed: {result.reason}")
                
        except Exception as e:
            # Fallback to dummy provider
            dummy_provider = DummyTTSProvider()
            return await dummy_provider.synthesize(text, language, voice)


class GoogleTTSProvider(TTSProvider):
    """Google Cloud Text-to-Speech provider."""
    
    def __init__(self):
        self.credentials_path = settings.google_application_credentials
        self.media_root = Path(settings.media_root)
        self.media_root.mkdir(parents=True, exist_ok=True)
    
    async def synthesize(self, text: str, language: str = "ml-IN", voice: Optional[str] = None) -> Dict[str, any]:
        """Synthesize text to speech using Google TTS."""
        try:
            from google.cloud import texttospeech
            
            if not self.credentials_path or not Path(self.credentials_path).exists():
                raise ValueError("Google Cloud credentials not configured")
            
            # Initialize client
            client = texttospeech.TextToSpeechClient()
            
            # Configure synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Configure voice
            voice_map = {
                "ml-IN": texttospeech.VoiceSelectionParams(
                    language_code="ml-IN",
                    name="ml-IN-Wavenet-A",
                ),
                "en-IN": texttospeech.VoiceSelectionParams(
                    language_code="en-IN",
                    name="en-IN-Wavenet-A",
                ),
                "en": texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    name="en-US-Wavenet-A",
                ),
            }
            voice_config = voice_map.get(language, voice_map["en"])
            
            # Configure audio
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16
            )
            
            # Perform synthesis
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice_config,
                audio_config=audio_config
            )
            
            # Save audio file
            audio_filename = f"tts_{uuid.uuid4()}.wav"
            audio_path = self.media_root / "tts" / audio_filename
            audio_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(audio_path, "wb") as out:
                out.write(response.audio_content)
            
            return {
                "audio_url": f"/media/tts/{audio_filename}",
                "audio_path": str(audio_path),
                "text": text,
                "language": language,
                "voice": voice_config.name,
                "duration": len(response.audio_content) / 16000,  # Approximate
                "provider": "google",
                "processing_time": 1.2,
            }
            
        except Exception as e:
            # Fallback to dummy provider
            dummy_provider = DummyTTSProvider()
            return await dummy_provider.synthesize(text, language, voice)


class CoquiTTSProvider(TTSProvider):
    """Coqui TTS provider for open-source text-to-speech."""
    
    def __init__(self):
        self.media_root = Path(settings.media_root)
        self.media_root.mkdir(parents=True, exist_ok=True)
        self.model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        self.tts = None
    
    async def synthesize(self, text: str, language: str = "ml-IN", voice: Optional[str] = None) -> Dict[str, any]:
        """Synthesize text to speech using Coqui TTS."""
        try:
            import TTS
            
            # Initialize TTS if not already done
            if not self.tts:
                self.tts = TTS.TTS(self.model_name)
            
            # Generate audio file
            audio_filename = f"tts_{uuid.uuid4()}.wav"
            audio_path = self.media_root / "tts" / audio_filename
            audio_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Synthesize
            self.tts.tts_to_file(
                text=text,
                speaker_wav=None,  # Use default speaker
                language=language.split("-")[0],  # Extract language code
                file_path=str(audio_path)
            )
            
            return {
                "audio_url": f"/media/tts/{audio_filename}",
                "audio_path": str(audio_path),
                "text": text,
                "language": language,
                "voice": "default",
                "duration": len(text) * 0.08,  # Approximate
                "provider": "coqui",
                "processing_time": 2.5,
            }
            
        except Exception as e:
            # Fallback to dummy provider
            dummy_provider = DummyTTSProvider()
            return await dummy_provider.synthesize(text, language, voice)


def get_tts_provider() -> TTSProvider:
    """Get TTS provider based on configuration."""
    provider_name = settings.tts_provider.lower()
    
    if provider_name == "azure":
        return AzureTTSProvider()
    elif provider_name == "google":
        return GoogleTTSProvider()
    elif provider_name == "coqui":
        return CoquiTTSProvider()
    else:
        return DummyTTSProvider()
