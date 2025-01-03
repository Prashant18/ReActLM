from enum import Enum
from typing import Dict, Any
from datetime import datetime

class InputType(Enum):
    """Enumeration of supported input types"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    BINARY = "binary"

class OutputType(Enum):
    """Enumeration of supported output types"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    BINARY = "binary"
    JSON = "json"

class ExecutionMode(Enum):
    """Enumeration of agent execution modes"""
    STANDARD = "standard"  # Step by step execution with user control
    YOLO = "yolo"         # Autonomous execution with safety checks

class AgentState(Enum):
    """Enumeration of possible agent states"""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"

# Re-export common types
__all__ = [
    'InputType',
    'OutputType',
    'ExecutionMode',
    'AgentState',
] 