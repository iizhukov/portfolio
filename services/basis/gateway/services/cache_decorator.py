import functools
import inspect
from typing import Callable, Optional
import logging

from services.redis_manager import RedisManager

logger = logging.getLogger(__name__)


def cache_response(
    ttl: Optional[int] = None,
    key_prefix: Optional[str] = None,
    include_params: bool = True
):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            redis_manager = None

            for arg in args:
                if isinstance(arg, RedisManager):
                    redis_manager = arg
                    break
            
            if not redis_manager:
                logger.warning("RedisManager not found in function arguments, skipping cache")
                return await func(*args, **kwargs)
            
            cache_key = _generate_cache_key(func, args, kwargs, key_prefix, include_params)
            
            cached_data = await redis_manager.get(cache_key)

            if cached_data is not None:
                logger.info(f"Cache hit for {func.__name__}")
                return cached_data
            
            logger.info(f"Cache miss for {func.__name__}, executing function")
            result = await func(*args, **kwargs)
            
            cache_ttl = ttl
            if cache_ttl is None:
                cache_ttl = await redis_manager.get_ttl_for_endpoint(f"/api/v1/{func.__name__}")
            
            await redis_manager.set(cache_key, result, cache_ttl)
            logger.info(f"Result cached for {func.__name__} with TTL {cache_ttl}s")
            
            return result
        
        return wrapper
    return decorator


def _generate_cache_key(
    func: Callable,
    args: tuple,
    kwargs: dict,
    key_prefix: Optional[str],
    include_params: bool
) -> str:
    if key_prefix:
        base_key = key_prefix
    else:
        base_key = f"gateway:{func.__name__}"
    
    if not include_params:
        return base_key
    
    params = {}
    
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    
    for param_name, param_value in bound_args.arguments.items():
        if param_name != 'redis_manager' and param_value is not None:
            if hasattr(param_value, 'dict'):
                params[param_name] = param_value.dict()
            elif hasattr(param_value, '__dict__'):
                params[param_name] = str(param_value)
            else:
                params[param_name] = param_value
    
    if params:
        import json
        params_str = json.dumps(params, sort_keys=True, default=str)

        params_hash = str(hash(params_str))[-8:]
        return f"{base_key}:{params_hash}"
    
    return base_key


def invalidate_cache(pattern: str):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            redis_manager = None
            for arg in args:
                if isinstance(arg, RedisManager):
                    redis_manager = arg
                    break
            
            result = await func(*args, **kwargs)
            
            if redis_manager:
                await redis_manager.delete_pattern(pattern)
                logger.info(f"Cache invalidated for pattern: {pattern}")
            
            return result
        
        return wrapper
    return decorator
