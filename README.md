# ReActLM 🤖

A powerful reactive agent framework powered by Language Models (LLMs). ReActLM provides a flexible architecture for building AI agents that can reason, use tools, and maintain memory of their actions.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🌟 Features

- 🧠 **Advanced Reasoning** - Chain of thought prompting with GPT-4 and other LLMs
- 🔍 **Research Tools** - Integrated Brave Search and Wikipedia research capabilities
- 💾 **Persistent Memory** - Redis-based memory system for maintaining context
- 📊 **Structured Output** - JSON-formatted responses for easy integration
- 🔄 **Async First** - Built with asyncio for high-performance operations
- 🛠️ **Extensible** - Plugin architecture for easy tool integration
- 📝 **Detailed Tracing** - Complete execution traces for debugging and analysis

## 🚀 Getting Started

Currently, this project is in development. To use it:

1. Clone the repository
```bash
git clone https://github.com/Prashant18/ReActLM.git
cd ReActLM
```

2. Set up your environment and build the project locally

### Basic Usage

```python
import asyncio
from reactlm import Agent, AgentConfig, OpenAILLM, BraveSearchTool

async def main():
    # Initialize agent
    agent = Agent(
        llm=OpenAILLM(api_key="your_openai_key"),
        config=AgentConfig(
            max_iterations=5,
            temperature=0.7
        )
    )
    
    # Add research capabilities
    await agent.add_tool(BraveSearchTool(api_key="your_brave_key"))
    
    # Execute a task
    result = await agent.execute(
        "What are the latest developments in quantum computing?"
    )
    print(result.content)

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔑 API Keys Setup

ReActLM requires API keys for various services. Create a `.env` file in your project root:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here
BRAVE_API_KEY=your_brave_api_key_here

# Optional (for memory persistence)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password  # If using authentication
```

⚠️ **Security Note**: Never commit your `.env` file to version control. Add it to your `.gitignore`:
```
# .gitignore
.env
*.pyc
__pycache__/
```

### Obtaining API Keys

1. **OpenAI API Key**:
   - Sign up at [OpenAI Platform](https://platform.openai.com)
   - Navigate to API Keys section
   - Create a new secret key

2. **Brave Search API Key**:
   - Visit [Brave Search API](https://brave.com/search/api/)
   - Sign up for API access
   - Get your API key (2,000 free searches/month)

3. **Redis Setup** (Optional):
   - Local: Install Redis using package manager
   - Cloud: Use services like Redis Labs
   - Configure authentication if needed

## 🛠️ Components

### LLM Providers
- OpenAI GPT-4/3.5
- Support for custom LLM implementations

### Research Tools
- Brave Search Integration
- Wikipedia Research
- Extensible tool system

### Memory Systems
- Redis-based persistence
- In-memory fallback
- Customizable storage backends

## 📚 Advanced Usage

### Chain of Thought Research

```python
from reactlm import Agent, AgentConfig, ExecutionMode

# Initialize agent with research configuration
agent = Agent(
    llm=OpenAILLM(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4"
    ),
    config=AgentConfig(
        max_iterations=5,
        mode=ExecutionMode.STANDARD,
        metadata={"purpose": "research"}
    )
)

# Add research tools
await agent.add_tool(BraveSearchTool())
await agent.add_tool(WikipediaTool())

# Execute research with context
result = await agent.execute(
    "Analyze quantum computing developments",
    context={
        "format": "structured",
        "depth": "comprehensive",
        "require_references": True
    }
)
```

### Memory Persistence

```python
from reactlm import RedisMemory

# Initialize memory system
memory = RedisMemory(
    host="localhost",
    port=6379,
    prefix="myapp:",
    ttl=3600  # 1 hour cache
)

# Use with agent
agent = Agent(
    llm=OpenAILLM(),
    config=AgentConfig(),
    memory=memory
)
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 