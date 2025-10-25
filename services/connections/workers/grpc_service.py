import grpc
import asyncio
import sys
import os

from concurrent import futures
from core.config import settings
from core.logging import get_logger
from pathlib import Path

# Add generated directory to Python path
generated_path = Path(__file__).parent.parent / "generated"
sys.path.insert(0, str(generated_path))

from services.connection_service import ConnectionService
from services.status_service import StatusService
from services.working_service import WorkingService

try:
    import connections_pb2
    import connections_pb2_grpc
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

            async with db_manager.get_session() as db:
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
                    connection.created_at = conn.created_at.isoformat() if conn.created_at else ""
                    connection.updated_at = conn.updated_at.isoformat() if conn.updated_at else ""
                
                return response
        except Exception as e:
            logger.error(f"Error in GetConnections: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return connections_pb2.GetConnectionsResponse()
    
    async def GetConnection(self, request, context):
        try:
            from core.database import db_manager
            async with db_manager.get_session() as db:
                service = ConnectionService(db)
                connection = await service.get_connection_by_id(request.id)
                
                if not connection:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Connection not found")
                    return connections_pb2.GetConnectionResponse()
                
                response = connections_pb2.GetConnectionResponse()
                response.connection.id = connection.id
                response.connection.label = connection.label
                response.connection.type = connection.type
                response.connection.href = connection.href
                response.connection.value = connection.value
                response.connection.created_at = connection.created_at.isoformat() if connection.created_at else ""
                response.connection.updated_at = connection.updated_at.isoformat() if connection.updated_at else ""
                
                return response
        except Exception as e:
            logger.error(f"Error in GetConnection: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return connections_pb2.GetConnectionResponse()
    
    async def GetStatus(self, request, context):
        try:
            from core.database import db_manager
            async with db_manager.get_session() as db:
                service = StatusService(db)
                status = await service.get_status()
                
                if not status:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Status not found")
                    return connections_pb2.GetStatusResponse()
                
                response = connections_pb2.GetStatusResponse()
                response.status.id = status.id
                response.status.status = status.status
                response.status.created_at = status.created_at.isoformat() if status.created_at else ""
                response.status.updated_at = status.updated_at.isoformat() if status.updated_at else ""
                
                return response
        except Exception as e:
            logger.error(f"Error in GetStatus: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return connections_pb2.GetStatusResponse()
    
    async def GetWorking(self, request, context):
        try:
            from core.database import db_manager
            async with db_manager.get_session() as db:
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
                response.working.created_at = working.created_at.isoformat() if working.created_at else ""
                response.working.updated_at = working.updated_at.isoformat() if working.updated_at else ""
                
                return response
        except Exception as e:
            logger.error(f"Error in GetWorking: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return connections_pb2.GetWorkingResponse()


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
