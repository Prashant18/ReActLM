from typing import Any, Dict, Optional, TypeVar, Generic
import json
from datetime import datetime, UTC

import redis.asyncio as redis

from ..core.base import BaseMemory

T = TypeVar('T')

class RedisMemory(BaseMemory[T]):
    """Redis-based memory implementation"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        prefix: str = "reactlib:",
        ttl: Optional[int] = None  # Time to live in seconds
    ):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True
        )
        self.prefix = prefix
        self.ttl = ttl
    
    async def store(
        self,
        key: str,
        data: T,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store data in Redis"""
        try:
            # Prepare the data with metadata
            storage_data = {
                "data": data,
                "metadata": metadata or {},
                "timestamp": datetime.now(UTC).isoformat()
            }
            
            # Store in Redis
            full_key = f"{self.prefix}{key}"
            await self.client.set(
                full_key,
                json.dumps(storage_data, default=str),
                ex=self.ttl
            )
        except Exception as e:
            raise RuntimeError(f"Redis storage error: {str(e)}")
    
    async def retrieve(
        self,
        key: str,
        **kwargs: Any
    ) -> Optional[T]:
        """Retrieve data from Redis"""
        try:
            # Get from Redis
            full_key = f"{self.prefix}{key}"
            data = await self.client.get(full_key)
            
            if data is None:
                return None
            
            # Parse the stored data
            storage_data = json.loads(data)
            return storage_data["data"]
        except Exception as e:
            raise RuntimeError(f"Redis retrieval error: {str(e)}")
    
    async def delete(self, key: str) -> bool:
        """Delete data from Redis"""
        try:
            full_key = f"{self.prefix}{key}"
            result = await self.client.delete(full_key)
            return result > 0
        except Exception as e:
            raise RuntimeError(f"Redis deletion error: {str(e)}")
    
    async def clear(self) -> None:
        """Clear all data with our prefix"""
        try:
            # Find all keys with our prefix
            pattern = f"{self.prefix}*"
            cursor = 0
            while True:
                cursor, keys = await self.client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100
                )
                if keys:
                    await self.client.delete(*keys)
                if cursor == 0:
                    break
        except Exception as e:
            raise RuntimeError(f"Redis clear error: {str(e)}")
    
    async def close(self) -> None:
        """Close the Redis connection"""
        await self.client.close()

# Re-export
__all__ = ['RedisMemory'] 