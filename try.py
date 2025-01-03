import asyncio
import os
import json
from datetime import datetime, UTC
from typing import Dict, Any, Optional

from dotenv import load_dotenv
import aiohttp

from reactlm import (
    Agent, AgentConfig, ExecutionMode,
    OpenAILLM, RedisMemory, SearchTool,
    CHAIN_OF_THOUGHT_PROMPT, TOOL_USE_PROMPT
)
from reactlm.core.base import BaseInput, BaseOutput, BaseTool
from reactlm.core.types import InputType, OutputType

# Load environment variables
load_dotenv()

def print_json(obj: Any) -> None:
    """Pretty print JSON objects"""
    print(json.dumps(obj, indent=2, default=str))

class BraveSearchTool(BaseTool):
    """Brave Search Tool with proper API integration"""
    name = "search"
    description = "Search the web for current information about a topic using Brave Search"
    input_types = [InputType.TEXT]
    output_type = OutputType.JSON
    version = "1.0.0"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")
        if not self.api_key:
            raise ValueError("Brave Search API key not found")
        
        self.endpoint = "https://api.search.brave.com/res/v1/web/search"
        self.headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        }
    
    async def execute(
        self,
        input_data: BaseInput,
        **kwargs: Any
    ) -> BaseOutput:
        """Execute a web search using Brave Search"""
        try:
            params = {
                "q": input_data.content,
                "count": 5,  # Number of results
                "search_lang": "en",
                "safesearch": "moderate",
                "text_format": "plain",
                "source": "web"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.endpoint,
                    headers=self.headers,
                    params=params
                ) as response:
                    if response.status != 200:
                        raise RuntimeError(
                            f"Brave Search failed: {response.status} - {await response.text()}"
                        )
                    
                    data = await response.json()
                    
                    # Process and format results
                    results = []
                    for item in data.get("web", {}).get("results", []):
                        results.append({
                            "title": item.get("title", ""),
                            "snippet": item.get("description", ""),
                            "url": item.get("url", ""),
                            "published": item.get("published_date", ""),
                            "source": item.get("source_name", ""),
                            "score": item.get("score", 0)
                        })
                    
                    return BaseOutput(
                        type=OutputType.JSON,
                        content={
                            "query": input_data.content,
                            "results": results,
                            "metadata": {
                                "total_results": len(results),
                                "timestamp": datetime.now(UTC).isoformat(),
                                "source": "brave_search",
                                "query_info": {
                                    "language": data.get("query", {}).get("language", ""),
                                    "total_matches": data.get("web", {}).get("total", 0)
                                }
                            }
                        }
                    )
                    
        except Exception as e:
            raise RuntimeError(f"Brave Search error: {str(e)}")
    
    async def validate_input(self, input_data: BaseInput) -> bool:
        """Validate search input"""
        return (
            input_data.type in self.input_types and
            isinstance(input_data.content, str) and
            len(input_data.content.strip()) > 0
        )

class WikipediaTool(BaseTool):
    """Wikipedia research tool"""
    name = "wikipedia"
    description = "Search Wikipedia articles for detailed information about a topic"
    input_types = [InputType.TEXT]
    output_type = OutputType.JSON
    version = "1.0.0"
    
    async def execute(
        self,
        input_data: BaseInput,
        **kwargs: Any
    ) -> BaseOutput:
        """Search Wikipedia and get article extracts"""
        try:
            # Wikipedia API endpoint
            endpoint = "https://en.wikipedia.org/w/api.php"
            
            async with aiohttp.ClientSession() as session:
                # First search for articles
                search_params = {
                    "action": "query",
                    "format": "json",
                    "list": "search",
                    "srsearch": input_data.content,
                    "srlimit": 3
                }
                
                async with session.get(endpoint, params=search_params) as response:
                    if response.status != 200:
                        raise RuntimeError(f"Wikipedia search failed: {response.status}")
                    
                    search_data = await response.json()
                    articles = search_data["query"]["search"]
                    
                    # Get extracts for each article
                    results = []
                    for article in articles:
                        extract_params = {
                            "action": "query",
                            "format": "json",
                            "pageids": article["pageid"],
                            "prop": "extracts|info",
                            "exintro": True,
                            "explaintext": True,
                            "inprop": "url"
                        }
                        
                        async with session.get(endpoint, params=extract_params) as extract_response:
                            if extract_response.status == 200:
                                extract_data = await extract_response.json()
                                page = list(extract_data["query"]["pages"].values())[0]
                                
                                results.append({
                                    "title": page["title"],
                                    "extract": page["extract"][:500] + "...",
                                    "url": page.get("fullurl", ""),
                                    "last_modified": page.get("touched", "")
                                })
                    
                    return BaseOutput(
                        type=OutputType.JSON,
                        content={
                            "query": input_data.content,
                            "results": results,
                            "metadata": {
                                "total_results": len(results),
                                "timestamp": datetime.now(UTC).isoformat(),
                                "source": "wikipedia"
                            }
                        }
                    )
                    
        except Exception as e:
            raise RuntimeError(f"Wikipedia tool error: {str(e)}")
    
    async def validate_input(self, input_data: BaseInput) -> bool:
        return (
            input_data.type in self.input_types and
            isinstance(input_data.content, str) and
            len(input_data.content.strip()) > 0
        )

async def setup_memory() -> RedisMemory:
    """Setup Redis memory with error handling"""
    try:
        memory = RedisMemory(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD"),
            prefix="reactlib_demo:",
            ttl=3600  # 1 hour TTL
        )
        # Test connection
        await memory.store("test", "test")
        await memory.delete("test")
        return memory
    except Exception as e:
        print(f"⚠️ Redis connection failed: {str(e)}")
        print("Continuing without memory persistence...")
        return None

async def main():
    try:
        # Initialize memory
        memory = await setup_memory()
        
        # Initialize the agent with chain of thought capabilities
        agent = Agent(
            llm=OpenAILLM(
                api_key=os.getenv("OPENAI_API_KEY"),
                model="gpt-4o-mini"  # Using GPT-4 for better reasoning
            ),
            config=AgentConfig(
                max_iterations=5,
                mode=ExecutionMode.STANDARD,
                temperature=0.7,
                metadata={"purpose": "research"}
            ),
            memory=memory
        )
        
        # Add research tools
        await agent.add_tool(BraveSearchTool())
        await agent.add_tool(WikipediaTool())
        
        print("\n🤖 ReActLib Research Assistant Demo")
        print("=" * 50)
        
        # Complex research query
        query = """
        I want to know everything possible about Amazon Bedrock:
        1. Major breakthroughs in the last 2 years
        2. Current challenges and limitations
        3. Potential impact on LLM and AI in general
        
        Please provide a structured analysis with references.
        """
        
        print(f"\n📝 Research Query:")
        print(query)
        print("\n⚙️ Processing...")
        
        # Execute research task
        result = await agent.execute(
            query,
            context={
                "purpose": "research",
                "format": "structured",
                "depth": "comprehensive",
                "require_references": True
            }
        )
        
        print("\n📊 Research Results:")
        print_json(result.content)
        
        print("\n🔍 Research Process:")
        for trace in agent.traces:
            print("\n---")
            print(f"Step: {trace.action}")
            print(f"Timestamp: {trace.timestamp}")
            
            if "tool_execution" in trace.action:
                print("\nTool Used:")
                print(f"- Input: {trace.input.content}")
                print("\nResults:")
                if isinstance(trace.output.content, dict) and "results" in trace.output.content:
                    for idx, res in enumerate(trace.output.content["results"], 1):
                        print(f"\n{idx}. {res.get('title', 'Result')}")
                        print(f"   {res.get('snippet', res.get('extract', 'No excerpt available'))}")
            
        # Clean up
        if memory:
            await memory.close()
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 