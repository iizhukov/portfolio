from typing import Optional

from services.grpc_client_manager import GrpcClientManager
from services.redis_manager import RedisManager
from services.admin_client import AdminClient


_grpc_manager: Optional[GrpcClientManager] = None
_redis_manager: Optional[RedisManager] = None
_admin_client: Optional[AdminClient] = None


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


def get_admin_client() -> AdminClient:
    global _admin_client

    if _admin_client is None:
        _admin_client = AdminClient()

    return _admin_client


async def initialize_services():
    global _grpc_manager, _redis_manager, _admin_client
    
    if _grpc_manager is None:
        _grpc_manager = GrpcClientManager()
        await _grpc_manager.initialize()
    
    if _redis_manager is None:
        _redis_manager = RedisManager()
        await _redis_manager.initialize()

    if _admin_client is None:
        _admin_client = AdminClient()
        await _admin_client.initialize()


async def close_services():
    global _grpc_manager, _redis_manager, _admin_client
    
    if _grpc_manager:
        await _grpc_manager.close()
        _grpc_manager = None
    
    if _redis_manager:
        await _redis_manager.close()
        _redis_manager = None

    if _admin_client:
        await _admin_client.close()
        _admin_client = None
