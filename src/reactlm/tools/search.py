from typing import Any, Dict, List
from datetime import datetime, UTC
import aiohttp

from ..core.base import BaseTool, BaseInput, BaseOutput
from ..core.types import InputType, OutputType

class SearchTool(BaseTool):
    """Web search tool implementation"""
    name = "search"
    description = "Search for information about a topic using a web search API"
    input_types = [InputType.TEXT]
    output_type = OutputType.JSON
    version = "1.0.0"
    
    def __init__(
        self,
        api_key: str,
        endpoint: str = "https://api.bing.microsoft.com/v7.0/search",
        max_results: int = 5
    ):
        self.api_key = api_key
        self.endpoint = endpoint
        self.max_results = max_results
        self.headers = {
            "Ocp-Apim-Subscription-Key": api_key,
            "Accept": "application/json"
        }
    
    async def execute(
        self,
        input_data: BaseInput,
        **kwargs: Any
    ) -> BaseOutput:
        """Execute a web search"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.endpoint,
                    headers=self.headers,
                    params={"q": input_data.content}
                ) as response:
                    if response.status != 200:
                        raise RuntimeError(
                            f"Search API error: {response.status} - {await response.text()}"
                        )
                    
                    data = await response.json()
                    
                    # Process and format results
                    results = []
                    for item in data.get("webPages", {}).get("value", [])[:self.max_results]:
                        results.append({
                            "title": item.get("name", ""),
                            "snippet": item.get("snippet", ""),
                            "url": item.get("url", ""),
                            "date_published": item.get("datePublished", "")
                        })
                    
                    return BaseOutput(
                        type=OutputType.JSON,
                        content={
                            "query": input_data.content,
                            "results": results,
                            "metadata": {
                                "total_results": len(results),
                                "timestamp": datetime.now(UTC).isoformat(),
                                "source": "bing"
                            }
                        }
                    )
        except Exception as e:
            raise RuntimeError(f"Search execution error: {str(e)}")
    
    async def validate_input(
        self,
        input_data: BaseInput
    ) -> bool:
        """Validate search input"""
        return (
            input_data.type in self.input_types and
            isinstance(input_data.content, str) and
            len(input_data.content.strip()) > 0
        )

class MockSearchTool(BaseTool):
    """Mock search tool for testing"""
    name = "search"
    description = "Search for information (simulated results)"
    input_types = [InputType.TEXT]
    output_type = OutputType.JSON
    version = "1.0.0"
    
    async def execute(
        self,
        input_data: BaseInput,
        **kwargs: Any
    ) -> BaseOutput:
        """Return simulated search results"""
        results = [
            {
                "title": f"Result 1 for {input_data.content}",
                "snippet": "This is a simulated search result with relevant information.",
                "url": "https://example.com/1",
                "date_published": datetime.now(UTC).isoformat()
            },
            {
                "title": f"Result 2 for {input_data.content}",
                "snippet": "Another simulated result with different information.",
                "url": "https://example.com/2",
                "date_published": datetime.now(UTC).isoformat()
            }
        ]
        
        return BaseOutput(
            type=OutputType.JSON,
            content={
                "query": input_data.content,
                "results": results,
                "metadata": {
                    "total_results": len(results),
                    "timestamp": datetime.now(UTC).isoformat(),
                    "source": "mock"
                }
            }
        )
    
    async def validate_input(
        self,
        input_data: BaseInput
    ) -> bool:
        """Validate search input"""
        return (
            input_data.type in self.input_types and
            isinstance(input_data.content, str) and
            len(input_data.content.strip()) > 0
        )

# Re-export
__all__ = ['SearchTool', 'MockSearchTool'] 