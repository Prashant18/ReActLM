from typing import Dict, Any, List
from pydantic import BaseModel, Field

class PromptTemplate(BaseModel):
    """Base class for prompt templates"""
    template: str
    variables: List[str] = Field(default_factory=list)
    
    def format(self, **kwargs: Any) -> str:
        """Format the template with provided variables"""
        return self.template.format(**kwargs)
    
    def validate_variables(self, **kwargs: Any) -> bool:
        """Validate that all required variables are provided"""
        return all(var in kwargs for var in self.variables)

# Standard prompt templates
AGENT_PROMPT = PromptTemplate(
    template="""You are a helpful AI assistant that can use tools to find information and answer questions.

Available Tools:
{tools_description}

To use a tool, respond with a JSON object in this format:
{{"tool": "tool_name", "input": "what to search for"}}

To provide a final answer, respond with a JSON object in this format:
{{"final_answer": {{"response": "your detailed response", "confidence": 0.9}}}}

Current Context:
{context}

User Query: {query}

Think step by step:
1. Do you need to use any tools to answer this question?
2. If yes, which tool would be most helpful?
3. If no, can you provide a final answer based on the current context?

Respond with either a tool call or a final answer in the JSON format specified above:""",
    variables=["tools_description", "context", "query"]
)

CHAIN_OF_THOUGHT_PROMPT = PromptTemplate(
    template="""Let's approach this step-by-step:

1. Question: {query}

2. Available Information:
{context}

3. Available Tools:
{tools_description}

4. Let's think about this:
- What do we know?
- What do we need to find out?
- Which tools could help us?

5. Plan:
{plan}

6. Next Step:
Based on this analysis, we should:

Respond with either a tool call or a final answer in JSON format:""",
    variables=["query", "context", "tools_description", "plan"]
)

TOOL_USE_PROMPT = PromptTemplate(
    template="""Tool: {tool_name}
Description: {tool_description}

Input: {tool_input}

Previous Results:
{previous_results}

Think about:
1. Is this the right tool for the task?
2. Is the input properly formatted?
3. How should we use the results?

Provide your next action in JSON format:""",
    variables=["tool_name", "tool_description", "tool_input", "previous_results"]
)

# Re-export
__all__ = [
    'PromptTemplate',
    'AGENT_PROMPT',
    'CHAIN_OF_THOUGHT_PROMPT',
    'TOOL_USE_PROMPT'
] 