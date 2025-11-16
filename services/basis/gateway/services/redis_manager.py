import json
import redis.asyncio as redis

from typing import Any, Optional, Dict

from core.config import settings
from core.logging import get_logger


logger = get_logger(__name__)


class RedisManager:    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self._initialized = False
    
    async def initialize(self):
        if self._initialized:
            return
            
        try:
            logger.info("Initializing Redis connection...")
            
            redis_kwargs = {
                "encoding": "utf-8",
                "decode_responses": True
            }
            
            if settings.REDIS_PASSWORD:
                redis_kwargs["password"] = settings.REDIS_PASSWORD
            
            self.redis = redis.from_url(
                settings.REDIS_URL,
                **redis_kwargs
            )
            
            await self.redis.ping()
            self._initialized = True
            
            logger.info("Redis connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    async def close(self):
        if self.redis:
            await self.redis.close()
            self._initialized = False
            logger.info("Redis connection closed")
    
    def _generate_cache_key(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        if params:
            sorted_params = sorted(params.items())
            params_str = json.dumps(sorted_params, sort_keys=True)
            params_hash = str(hash(params_str))[-8:]
            return f"gateway:{endpoint}:{params_hash}"
        return f"gateway:{endpoint}"
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        if not self._initialized:
            return
        
        if self.redis is None:
            logger.warning("Redis client is not initialized")
            return

        try:
            cache_key = self._generate_cache_key(endpoint, params)
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                logger.debug(f"Cache hit for key: {cache_key}")
                return json.loads(cached_data)
            else:
                logger.debug(f"Cache miss for key: {cache_key}")
                return
                
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return
    
    async def set(self, endpoint: str, data: Any, ttl: int, params: Optional[Dict[str, Any]] = None):
        if not self._initialized:
            return
        
        if self.redis is None:
            logger.warning("Redis client is not initialized")
            return
            
        try:
            cache_key = self._generate_cache_key(endpoint, params)
            json_data = json.dumps(data, default=str)
            
            await self.redis.setex(cache_key, ttl, json_data)
            logger.debug(f"Data cached with key: {cache_key}, TTL: {ttl}s")
            
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
    
    async def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None):
        if not self._initialized:
            return
        
        if self.redis is None:
            logger.warning("Redis client is not initialized")
            return
            
        try:
            cache_key = self._generate_cache_key(endpoint, params)
            await self.redis.delete(cache_key)
            logger.debug(f"Cache deleted for key: {cache_key}")
            
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
    
    async def delete_pattern(self, pattern: str):
        if not self._initialized:
            return
        
        if self.redis is None:
            logger.warning("Redis client is not initialized")
            return
            
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
                logger.debug(f"Deleted {len(keys)} keys matching pattern: {pattern}")
                
        except Exception as e:
            logger.error(f"Error deleting pattern {pattern}: {e}")
    
    async def get_ttl_for_endpoint(self, endpoint: str) -> int:
        if endpoint.startswith("/api/v1/connections"):
            return settings.CACHE_TTL_CONNECTIONS
        elif endpoint.startswith("/api/v1/modules"):
            return settings.CACHE_TTL_MODULES
        elif endpoint.startswith("/api/v1/admin"):
            return settings.CACHE_TTL_ADMIN
        else:
            return 300
    
    async def health_check(self) -> bool:
        if not self._initialized:
            return False
        
        if self.redis is None:
            logger.warning("Redis client is not initialized")
            return False
            
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
