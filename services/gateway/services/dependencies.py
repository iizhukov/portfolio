from typing import Optional
from services.grpc_client_manager import GrpcClientManager
from services.redis_manager import RedisManager


_grpc_manager: Optional[GrpcClientManager] = None
_redis_manager: Optional[RedisManager] = None


def get_grpc_manager() -> GrpcClientManager:
    global _grpc_manager

    if _grpc_manager is None:
        _grpc_manager = GrpcClientManager()

    return _grpc_manager


def get_redis_manager() -> RedisManager:
    global _redis_manager

    if _redis_manager is None:
        _redis_manager = RedisManager()

    return _redis_manager


async def initialize_services():
    global _grpc_manager, _redis_manager
    
    if _grpc_manager is None:
        _grpc_manager = GrpcClientManager()
        await _grpc_manager.initialize()
    
    if _redis_manager is None:
        _redis_manager = RedisManager()
        await _redis_manager.initialize()


async def close_services():
    global _grpc_manager, _redis_manager
    
    if _grpc_manager:
        await _grpc_manager.close()
        _grpc_manager = None
    
    if _redis_manager:
        await _redis_manager.close()
        _redis_manager = None
