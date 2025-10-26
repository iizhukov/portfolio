import grpc
import asyncio
import sys
import os

from concurrent import futures
from core.config import settings
from core.logging import get_logger
from pathlib import Path

generated_path = Path(__file__).parent.parent / "generated"
sys.path.insert(0, str(generated_path))

from services.connection_service import ConnectionService
from services.status_service import StatusService
from services.working_service import WorkingService

try:
    from generated import connections_pb2, connections_pb2_grpc
except ImportError as e:
    logger = get_logger(__name__)
    logger.error(f"Failed to import gRPC files: {e}")
    logger.error(f"Generated path: {generated_path}")
    logger.error(f"Files in generated: {os.listdir(generated_path) if generated_path.exists() else 'Directory not found'}")
    sys.exit(1)


logger = get_logger(__name__)


class ConnectionsGrpcService(connections_pb2_grpc.ConnectionsServiceServicer):
    async def GetConnections(self, request, context):
        try:
            from core.database import db_manager

            async for db in db_manager.get_session():
                service = ConnectionService(db)
                connections = await service.get_all_connections()
                
                response = connections_pb2.GetConnectionsResponse()
                for conn in connections:
                    connection = response.connections.add()
                    connection.id = conn.id
                    connection.label = conn.label
                    connection.type = conn.type
                    connection.href = conn.href
                    connection.value = conn.value
                
                return response
        except Exception as e:
            logger.error(f"Error in GetConnections: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return connections_pb2.GetConnectionsResponse()
    
    async def GetImage(self, request, context):
        try:
            from core.database import db_manager
            from services.image_service import ImageService
            
            async for db in db_manager.get_session():
                service = ImageService(db)
                image = await service.get_image()
                
                if not image:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Image not found")
                    return connections_pb2.GetImageResponse()
                
                response = connections_pb2.GetImageResponse()
                response.image.id = image.id
                response.image.filename = image.filename
                response.image.content_type = image.content_type
                response.image.url = image.url
                
                return response
        except Exception as e:
            logger.error(f"Error in GetImage: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return connections_pb2.GetImageResponse()
    
    async def GetStatus(self, request, context):
        try:
            from core.database import db_manager
            async for db in db_manager.get_session():
                service = StatusService(db)
                status = await service.get_status()
                
                if not status:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Status not found")
                    return connections_pb2.GetStatusResponse()
                
                response = connections_pb2.GetStatusResponse()
                response.status.id = status.id
                response.status.status = status.status
                
                return response
        except Exception as e:
            logger.error(f"Error in GetStatus: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return connections_pb2.GetStatusResponse()
    
    async def GetWorking(self, request, context):
        try:
            from core.database import db_manager
            async for db in db_manager.get_session():
                service = WorkingService(db)
                working = await service.get_working_status()
                
                if not working:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Working status not found")
                    return connections_pb2.GetWorkingResponse()
                
                response = connections_pb2.GetWorkingResponse()
                response.working.id = working.id
                response.working.working_on = working.working_on
                response.working.percentage = working.percentage
                
                return response
        except Exception as e:
            logger.error(f"Error in GetWorking: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return connections_pb2.GetWorkingResponse()
    
    async def HealthCheck(self, request, context):
        try:
            from core.database import db_manager
            from services.health_service import HealthService
            from datetime import datetime
            
            async for db in db_manager.get_session():
                service = HealthService(db)
                health_status = await service.check_health()
                
                response = connections_pb2.HealthCheckResponse()
                response.status = health_status.status
                response.timestamp = health_status.timestamp.isoformat()
                response.database = health_status.database
                response.redpanda = health_status.redpanda
                response.modules_service = health_status.modules_service
                
                return response
        except Exception as e:
            logger.error(f"Error in HealthCheck: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            response = connections_pb2.HealthCheckResponse()
            response.status = "unhealthy"
            response.timestamp = datetime.now().isoformat()
            response.database = False
            response.redpanda = False
            response.modules_service = False
            return response


async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    connections_pb2_grpc.add_ConnectionsServiceServicer_to_server(
        ConnectionsGrpcService(), server
    )
    
    listen_addr = f'[::]:{settings.GRPC_PORT}'
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting gRPC server on {listen_addr}")
    await server.start()
    
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Shutting down gRPC server...")
        await server.stop(5)


if __name__ == '__main__':
    asyncio.run(serve())
