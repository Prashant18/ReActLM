"""
ReActLib - A powerful reactive agent library with multimodal support
"""

from .core.agent import Agent, AgentConfig
from .core.base import (
    BaseInput,
    BaseOutput,
    BaseLLM,
    BaseTool,
    BaseMemory,
    BaseTrace
)
from .core.types import (
    InputType,
    OutputType,
    ExecutionMode,
    AgentState
)

# Import implementations
from .llms import OpenAILLM
from .memory import RedisMemory
from .tools import SearchTool, MockSearchTool
from .prompts import (
    PromptTemplate,
    AGENT_PROMPT,
    CHAIN_OF_THOUGHT_PROMPT,
    TOOL_USE_PROMPT
)

__version__ = "0.1.0"

__all__ = [
    # Core classes
    'Agent',
    'AgentConfig',
    # Base classes
    'BaseInput',
    'BaseOutput',
    'BaseLLM',
    'BaseTool',
    'BaseMemory',
    'BaseTrace',
    # Types
    'InputType',
    'OutputType',
    'ExecutionMode',
    'AgentState',
    # LLM implementations
    'OpenAILLM',
    # Memory implementations
    'RedisMemory',
    # Tool implementations
    'SearchTool',
    'MockSearchTool',
    # Prompt templates
    'PromptTemplate',
    'AGENT_PROMPT',
    'CHAIN_OF_THOUGHT_PROMPT',
    'TOOL_USE_PROMPT',
] 