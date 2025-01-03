from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union, Optional, TypeVar, Generic, AsyncIterator
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from .types import (
    InputType,
    OutputType
)

T = TypeVar('T')

class BaseInput(BaseModel):
    """Base class for all input types"""
    type: InputType
    content: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class BaseOutput(BaseModel):
    """Base class for all output types"""
    type: OutputType
    content: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class BaseLLM(ABC):
    """Abstract base class for LLM providers"""
    @abstractmethod
    async def generate(
        self,
        prompt: Union[str, BaseInput],
        **kwargs: Any
    ) -> BaseOutput:
        """Generate a response from the LLM"""
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: Union[str, BaseInput],
        **kwargs: Any
    ) -> AsyncIterator[BaseOutput]:
        """Stream responses from the LLM"""
        pass

class BaseTool(ABC):
    """Abstract base class for tools"""
    name: str
    description: str
    input_types: List[InputType]
    output_type: OutputType
    version: str = "1.0.0"
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @abstractmethod
    async def execute(
        self,
        input_data: BaseInput,
        **kwargs: Any
    ) -> BaseOutput:
        """Execute the tool with given input"""
        pass

    @abstractmethod
    async def validate_input(
        self,
        input_data: BaseInput
    ) -> bool:
        """Validate that the input matches tool requirements"""
        pass

class BaseMemory(ABC, Generic[T]):
    """Abstract base class for memory systems"""
    @abstractmethod
    async def store(
        self,
        key: str,
        data: T,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store data in memory"""
        pass

    @abstractmethod
    async def retrieve(
        self,
        key: str,
        **kwargs: Any
    ) -> Optional[T]:
        """Retrieve data from memory"""
        pass

    @abstractmethod
    async def delete(
        self,
        key: str
    ) -> bool:
        """Delete data from memory"""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all data from memory"""
        pass

class BaseTrace(BaseModel):
    """Base class for execution traces"""
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str
    input: BaseInput
    output: BaseOutput
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)

# Re-export base classes
__all__ = [
    'BaseInput',
    'BaseOutput',
    'BaseLLM',
    'BaseTool',
    'BaseMemory',
    'BaseTrace',
] 