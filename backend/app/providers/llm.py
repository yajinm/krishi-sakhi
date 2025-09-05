"""
LLM provider for text generation.

Provides interfaces for language model integration.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from app.config import settings


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate response from prompt."""
        pass
    
    @abstractmethod
    async def generate_advisory(self, context: Dict) -> str:
        """Generate farming advisory."""
        pass


class LocalRuleLLMProvider(LLMProvider):
    """Local rule-based LLM provider."""
    
    def __init__(self):
        self.rules = {
            "rain": "മഴ പ്രതീക്ഷിക്കുന്നു. തളിക്കൽ ഒഴിവാക്കുക.",
            "wind": "ഉയർന്ന കാറ്റ്. തളിക്കൽ താമസിപ്പിക്കുക.",
            "pest": "കീട ശ്രദ്ധ. നിരീക്ഷണം നടത്തുക.",
        }
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate response using rules."""
        prompt_lower = prompt.lower()
        
        for keyword, response in self.rules.items():
            if keyword in prompt_lower:
                return response
        
        return "ഞാൻ സഹായിക്കാൻ തയ്യാറാണ്. കൂടുതൽ വിവരങ്ങൾ നൽകുക."
    
    async def generate_advisory(self, context: Dict) -> str:
        """Generate advisory based on context."""
        if context.get("rain_forecast", 0) > 10:
            return "മഴ പ്രതീക്ഷിക്കുന്നു. തളിക്കൽ ഒഴിവാക്കുക."
        
        if context.get("wind_speed", 0) > 6:
            return "ഉയർന്ന കാറ്റ്. തളിക്കൽ താമസിപ്പിക്കുക."
        
        if context.get("pest_alert"):
            return "കീട ശ്രദ്ധ. നിരീക്ഷണം നടത്തുക."
        
        return "സാധാരണ കൃഷി പ്രവർത്തനങ്ങൾ തുടരാം."


class OpenAILLMProvider(LLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate response using OpenAI."""
        if not self.api_key:
            # Fallback to local provider
            local_provider = LocalRuleLLMProvider()
            return await local_provider.generate_response(prompt, context)
        
        try:
            import openai
            
            messages = [
                {"role": "system", "content": "You are a helpful farming assistant for Kerala farmers. Respond in Malayalam."},
                {"role": "user", "content": prompt}
            ]
            
            if context:
                messages.insert(-1, {"role": "system", "content": f"Context: {context}"})
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                max_tokens=200,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Fallback to local provider
            local_provider = LocalRuleLLMProvider()
            return await local_provider.generate_response(prompt, context)
    
    async def generate_advisory(self, context: Dict) -> str:
        """Generate advisory using OpenAI."""
        if not self.api_key:
            # Fallback to local provider
            local_provider = LocalRuleLLMProvider()
            return await local_provider.generate_advisory(context)
        
        try:
            import openai
            
            prompt = f"Generate a farming advisory based on this context: {context}"
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a farming expert. Generate helpful advisories in Malayalam."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.5,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Fallback to local provider
            local_provider = LocalRuleLLMProvider()
            return await local_provider.generate_advisory(context)


def get_llm_provider() -> LLMProvider:
    """Get LLM provider based on configuration."""
    provider_name = settings.llm_provider.lower()
    
    if provider_name == "openai":
        return OpenAILLMProvider()
    else:
        return LocalRuleLLMProvider()
