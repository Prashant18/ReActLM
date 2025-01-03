from typing import Any, Dict, Union, AsyncIterator, Optional
from datetime import datetime, UTC

from openai import AsyncOpenAI
import json

from ..core.base import BaseLLM, BaseInput, BaseOutput
from ..core.types import OutputType

class OpenAILLM(BaseLLM):
    """OpenAI LLM implementation with GPT models"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        organization: Optional[str] = None
    ):
        self.client = AsyncOpenAI(
            api_key=api_key,
            organization=organization
        )
        self.model = model
        
        if not self.client.api_key:
            raise ValueError("OpenAI API key not found")
    
    async def generate(
        self,
        prompt: Union[str, BaseInput],
        **kwargs: Any
    ) -> BaseOutput:
        try:
            # Convert BaseInput to string if needed
            if isinstance(prompt, BaseInput):
                prompt = prompt.content
            
            # Create system message that enforces JSON output
            system_message = {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant that always responds in valid JSON format. "
                    "Your responses should either be tool usage requests or final answers. "
                    "Always maintain the specified JSON structure in your responses."
                )
            }
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    system_message,
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 500),
                response_format={"type": "json_object"}
            )
            
            content = json.loads(response.choices[0].message.content)
            
            return BaseOutput(
                type=OutputType.JSON,
                content=content,
                metadata={
                    "model": self.model,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                }
            )
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    async def stream(
        self,
        prompt: Union[str, BaseInput],
        **kwargs: Any
    ) -> AsyncIterator[BaseOutput]:
        try:
            if isinstance(prompt, BaseInput):
                prompt = prompt.content
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 500),
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield BaseOutput(
                        type=OutputType.TEXT,
                        content=chunk.choices[0].delta.content,
                        metadata={
                            "model": self.model,
                            "timestamp": datetime.now(UTC).isoformat(),
                            "chunk": True
                        }
                    )
        except Exception as e:
            raise RuntimeError(f"OpenAI API streaming error: {str(e)}")

# Re-export
__all__ = ['OpenAILLM'] 