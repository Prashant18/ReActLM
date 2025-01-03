from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, ConfigDict
import asyncio
import uuid
from datetime import datetime

from .base import (
    BaseLLM,
    BaseTool,
    BaseMemory,
    BaseInput,
    BaseOutput,
    BaseTrace
)
from .types import (
    InputType,
    OutputType,
    ExecutionMode,
    AgentState
)

class AgentConfig(BaseModel):
    """Configuration for Agent behavior"""
    max_iterations: int = 10
    temperature: float = 0.7
    mode: ExecutionMode = ExecutionMode.STANDARD
    allowed_tools: List[str] = Field(default_factory=lambda: ["*"])
    memory_type: str = "default"
    trace_enabled: bool = True
    timeout: float = 30.0  # seconds
    max_tokens: Optional[int] = None
    stop_sequences: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)

class Agent:
    """Core Agent implementation with reactive architecture"""
    
    def __init__(
        self,
        llm: BaseLLM,
        config: AgentConfig,
        tools: Optional[Dict[str, BaseTool]] = None,
        memory: Optional[BaseMemory] = None
    ):
        self.llm = llm
        self.config = config
        self.tools = tools or {}
        self.memory = memory
        self.state = AgentState.IDLE
        self._session_id = str(uuid.uuid4())
        self._iteration = 0
        self._traces: List[BaseTrace] = []

    async def execute(
        self,
        input_data: Union[str, BaseInput],
        context: Optional[Dict[str, Any]] = None
    ) -> BaseOutput:
        """Execute the agent's reasoning and action loop"""
        try:
            # Convert string input to BaseInput if needed
            if isinstance(input_data, str):
                input_data = BaseInput(
                    type=InputType.TEXT,
                    content=input_data
                )

            # Initialize execution
            self.state = AgentState.THINKING
            self._iteration = 0
            context = context or {}
            final_answer = None
            
            # Main execution loop
            while self._iteration < self.config.max_iterations:
                self._iteration += 1
                
                # Generate next action using LLM
                self.state = AgentState.THINKING
                action = await self._generate_next_action(input_data, context)
                
                # Store trace if enabled
                if self.config.trace_enabled:
                    await self._store_trace(
                        action="llm_generation",
                        input=input_data,
                        output=action
                    )
                
                # Parse LLM response
                if action.type == OutputType.JSON:
                    response_data = action.content
                    
                    # Check if it's a final answer
                    if "final_answer" in response_data:
                        final_answer = BaseOutput(
                            type=OutputType.JSON,
                            content=response_data["final_answer"],
                            metadata=action.metadata
                        )
                        break
                    
                    # Check if we need to use a tool
                    elif "tool" in response_data:
                        self.state = AgentState.EXECUTING
                        tool_name = response_data["tool"]
                        tool_input = response_data.get("input", "")
                        
                        if tool_name in self.tools:
                            tool = self.tools[tool_name]
                            tool_result = await tool.execute(
                                BaseInput(
                                    type=InputType.TEXT,
                                    content=tool_input
                                )
                            )
                            
                            # Store trace if enabled
                            if self.config.trace_enabled:
                                await self._store_trace(
                                    action=f"tool_execution:{tool_name}",
                                    input=input_data,
                                    output=tool_result
                                )
                            
                            # Update context with tool result
                            context["last_tool_result"] = tool_result.content
                        else:
                            raise ValueError(f"Tool {tool_name} not found")
                
                # Check if we have a final answer
                if final_answer is not None:
                    self.state = AgentState.COMPLETED
                    return final_answer
            
            # If we reach here without a final answer, use the last action as the answer
            if final_answer is None and action is not None:
                final_answer = action
            
            # Max iterations reached
            if final_answer is None:
                self.state = AgentState.ERROR
                raise RuntimeError("Max iterations reached without completion")
                
            self.state = AgentState.COMPLETED
            return final_answer
            
        except Exception as e:
            self.state = AgentState.ERROR
            raise e

    async def add_tool(self, tool: BaseTool) -> None:
        """Dynamically add new tool"""
        if tool.name in self.tools:
            raise ValueError(f"Tool {tool.name} already exists")
        self.tools[tool.name] = tool

    async def remove_tool(self, tool_name: str) -> None:
        """Remove a tool by name"""
        if tool_name in self.tools:
            del self.tools[tool_name]

    async def _generate_next_action(
        self,
        input_data: BaseInput,
        context: Dict[str, Any]
    ) -> BaseOutput:
        """Generate the next action using the LLM"""
        # Construct prompt with context and available tools
        prompt = self._construct_prompt(input_data, context)
        
        # Generate response
        response = await self.llm.generate(
            prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stop_sequences=self.config.stop_sequences
        )
        
        return response

    def _construct_prompt(
        self,
        input_data: BaseInput,
        context: Dict[str, Any]
    ) -> str:
        """Construct the prompt for the LLM"""
        tools_str = "\n".join([
            f"- {name}: {tool.description}" 
            for name, tool in self.tools.items()
        ])
        
        return f"""You are a helpful AI assistant that can use tools to find information and answer questions.

Available Tools:
{tools_str}

To use a tool, respond with a JSON object in this format:
{{"tool": "tool_name", "input": "what to search for"}}

To provide a final answer, respond with a JSON object in this format:
{{"final_answer": {{"response": "your detailed response", "confidence": 0.9}}}}

Current Context:
{context}

User Query: {input_data.content}

Think step by step:
1. Do you need to use any tools to answer this question?
2. If yes, which tool would be most helpful?
3. If no, can you provide a final answer based on the current context?

Respond with either a tool call or a final answer in the JSON format specified above:"""

    async def _store_trace(
        self,
        action: str,
        input: BaseInput,
        output: BaseOutput
    ) -> None:
        """Store execution trace"""
        trace = BaseTrace(
            session_id=self._session_id,
            timestamp=datetime.utcnow(),
            action=action,
            input=input,
            output=output,
            metadata={
                "iteration": self._iteration,
                "state": self.state.value
            }
        )
        self._traces.append(trace)
        
        # Store in memory if available
        if self.memory:
            await self.memory.store(
                f"trace:{self._session_id}:{self._iteration}",
                trace
            )

    @property
    def traces(self) -> List[BaseTrace]:
        """Get all traces for current session"""
        return self._traces.copy()

# Re-export
__all__ = ['Agent', 'AgentConfig'] 