import grpc

from typing import Dict, Any
from grpc import aio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from core.config import settings
from core.logging import get_logger


logger = get_logger(__name__)


class GrpcClientManager:    
    def __init__(self):
        self.clients: Dict[str, Any] = {}
        self.channels: Dict[str, aio.Channel] = {}
        self._initialized = False
    
    async def initialize(self):
        if self._initialized:
            return
            
        logger.info("Initializing gRPC clients...")

        await self._create_connections_channel()
        await self._create_modules_channel()
        await self._create_admin_channel()
        
        self._initialized = True
        logger.info("All gRPC clients initialized successfully")
    
    async def _create_connections_channel(self):
        try:
            options = [
                ('grpc.keepalive_time_ms', 30000),
                ('grpc.keepalive_timeout_ms', 5000),
                ('grpc.keepalive_permit_without_calls', True),
                ('grpc.http2.max_pings_without_data', 0),
                ('grpc.http2.min_time_between_pings_ms', 10000),
                ('grpc.http2.min_ping_interval_without_data_ms', 300000),
                ('grpc.max_connection_idle_ms', 30000),
                ('grpc.max_connection_age_ms', 300000),
                ('grpc.max_connection_age_grace_ms', 5000),
            ]
            
            channel = aio.insecure_channel(
                f"{settings.CONNECTIONS_SERVICE_HOST}:{settings.CONNECTIONS_SERVICE_PORT}",
                options=options
            )
            self.channels["connections"] = channel

            from generated.connections import connections_pb2_grpc
            self.clients["connections"] = connections_pb2_grpc.ConnectionsServiceStub(channel)
            
            logger.info(f"Connections service channel created with pooling: {settings.CONNECTIONS_SERVICE_HOST}:{settings.CONNECTIONS_SERVICE_PORT}")
        except Exception as e:
            logger.error(f"Failed to create connections channel: {e}")
    
    async def _create_modules_channel(self):
        try:
            options = [
                ('grpc.keepalive_time_ms', 30000),
                ('grpc.keepalive_timeout_ms', 5000),
                ('grpc.keepalive_permit_without_calls', True),
            ]

            channel = aio.insecure_channel(
                f"{settings.MODULES_SERVICE_HOST}:{settings.MODULES_SERVICE_PORT}",
                options=options,
            )
            self.channels["modules"] = channel

            from generated.modules import modules_pb2_grpc

            self.clients["modules"] = modules_pb2_grpc.ModulesServiceStub(channel)

            logger.info(
                "Modules service channel created: %s:%s",
                settings.MODULES_SERVICE_HOST,
                settings.MODULES_SERVICE_PORT,
            )
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to create modules channel: {e}")
    
    async def _create_admin_channel(self):
        try:
            options = [
                ('grpc.keepalive_time_ms', 30000),
                ('grpc.keepalive_timeout_ms', 5000),
                ('grpc.keepalive_permit_without_calls', True),
            ]

            channel = aio.insecure_channel(
                f"{settings.ADMIN_SERVICE_HOST}:{settings.ADMIN_SERVICE_PORT}",
                options=options,
            )
            self.channels["admin"] = channel

            from generated.admin import admin_pb2_grpc
            self.clients["admin"] = admin_pb2_grpc.AdminServiceStub(channel)

            logger.info(
                "Admin service channel created: %s:%s",
                settings.ADMIN_SERVICE_HOST,
                settings.ADMIN_SERVICE_PORT,
            )
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to create admin channel: {e}")
    
    async def get_client(self, service_name: str):
        if not self._initialized:
            await self.initialize()
        
        if service_name not in self.clients:
            raise ValueError(f"Service '{service_name}' not found")
        
        return self.clients[service_name]
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(grpc.RpcError)
    )
    async def call_grpc_with_retry(self, client, method, request, timeout=30):
        try:
            return await method(request, timeout=timeout)
        except grpc.RpcError as e:
            logger.error(f"gRPC call failed: {e.code()} - {e.details()}")
            raise
    
    async def get_available_services(self) -> Dict[str, str]:
        return {
            "connections": f"{settings.CONNECTIONS_SERVICE_HOST}:{settings.CONNECTIONS_SERVICE_PORT}",
            "modules": f"{settings.MODULES_SERVICE_HOST}:{settings.MODULES_SERVICE_PORT}",
            "admin": f"{settings.ADMIN_SERVICE_HOST}:{settings.ADMIN_SERVICE_PORT}",
        }
    
    async def check_services_health(self) -> Dict[str, bool]:
        health_status = {}
        
        for service_name, channel in self.channels.items():
            try:
                state = channel.get_state()
                # IDLE or READY states mean the channel is available
                # CONNECTING means it's attempting to connect
                # Other states (TRANSIENT_FAILURE, SHUTDOWN) are unhealthy
                healthy_states = [
                    grpc.ChannelConnectivity.READY,
                    grpc.ChannelConnectivity.IDLE,
                    grpc.ChannelConnectivity.CONNECTING
                ]
                health_status[service_name] = state in healthy_states
                
                logger.debug(f"Service {service_name} state: {state.name}, healthy: {health_status[service_name]}")
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                health_status[service_name] = False
        
        return health_status
    
    async def close(self):
        logger.info("Closing gRPC channels...")
        
        for service_name, channel in self.channels.items():
            try:
                await channel.close()
                logger.info(f"Channel for {service_name} closed")
            except Exception as e:
                logger.error(f"Error closing channel for {service_name}: {e}")
        
        self.channels.clear()
        self.clients.clear()
        self._initialized = False
