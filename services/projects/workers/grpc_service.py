import grpc
import asyncio
import sys
import os

from concurrent import futures
from core.config import settings
from core.logging import get_logger
from pathlib import Path

generated_path = Path(__file__).parent.parent / "generated" / "projects"
sys.path.insert(0, str(generated_path))

from services.project_service import ProjectService

try:
    from generated.projects import projects_pb2, projects_pb2_grpc
except ImportError as e:
    logger = get_logger(__name__)
    logger.error(f"Failed to import gRPC files: {e}")
    logger.error(f"Generated path: {generated_path}")
    logger.error(f"Files in generated: {os.listdir(generated_path) if generated_path.exists() else 'Directory not found'}")
    sys.exit(1)


logger = get_logger(__name__)


def project_model_to_proto(project_model, proto_project):
    proto_project.id = project_model.id
    proto_project.name = project_model.name
    proto_project.type = project_model.type
    proto_project.icon = project_model.icon
    if project_model.file_type:
        proto_project.file_type = project_model.file_type
    if project_model.parent_id:
        proto_project.parent_id = project_model.parent_id
    if project_model.url:
        proto_project.url = project_model.url
    proto_project.created_at = project_model.created_at.isoformat() if project_model.created_at else ""
    proto_project.updated_at = project_model.updated_at.isoformat() if project_model.updated_at else ""
    
    if project_model.children:
        for child in project_model.children:
            child_proto = proto_project.children.add()
            project_model_to_proto(child, child_proto)


class ProjectsGrpcService(projects_pb2_grpc.ProjectsServiceServicer):
    async def GetProjects(self, request, context):
        try:
            from core.database import db_manager

            async for db in db_manager.get_session():
                service = ProjectService(db)
                parent_id = request.parent_id if request.HasField("parent_id") else None
                projects = await service.get_all_projects(parent_id=parent_id)
                
                response = projects_pb2.GetProjectsResponse()
                for project in projects:
                    proto_project = response.projects.add()
                    project_model_to_proto(project, proto_project)
                
                return response
        except Exception as e:
            logger.error(f"Error in GetProjects: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return projects_pb2.GetProjectsResponse()
    
    async def GetProjectById(self, request, context):
        try:
            from core.database import db_manager

            async for db in db_manager.get_session():
                service = ProjectService(db)
                project = await service.get_project_by_id(request.id)
                
                if not project:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Project not found")
                    return projects_pb2.GetProjectByIdResponse()
                
                response = projects_pb2.GetProjectByIdResponse()
                project_model_to_proto(project, response.project)
                
                return response
        except Exception as e:
            logger.error(f"Error in GetProjectById: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return projects_pb2.GetProjectByIdResponse()
    
    async def GetProjectTree(self, request, context):
        try:
            from core.database import db_manager

            async for db in db_manager.get_session():
                service = ProjectService(db)
                root_id = request.root_id if request.HasField("root_id") else None
                projects = await service.get_project_tree(root_id=root_id)
                
                response = projects_pb2.GetProjectTreeResponse()
                for project in projects:
                    proto_project = response.projects.add()
                    project_model_to_proto(project, proto_project)
                
                return response
        except Exception as e:
            logger.error(f"Error in GetProjectTree: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return projects_pb2.GetProjectTreeResponse()
    
    async def HealthCheck(self, request, context):
        try:
            from core.database import db_manager
            from services.health_service import HealthService
            from datetime import datetime
            
            async for db in db_manager.get_session():
                service = HealthService(db)
                health_status = await service.check_health()
                
                response = projects_pb2.HealthCheckResponse()
                response.status = health_status["status"]
                response.timestamp = health_status["timestamp"]
                response.database = health_status["database"]
                response.redpanda = health_status["redpanda"]
                response.modules_service = health_status["modules_service"]
                
                return response
        except Exception as e:
            logger.error(f"Error in HealthCheck: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            response = projects_pb2.HealthCheckResponse()
            response.status = "unhealthy"
            response.timestamp = datetime.now().isoformat()
            response.database = False
            response.redpanda = False
            response.modules_service = False
            return response


async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    projects_pb2_grpc.add_ProjectsServiceServicer_to_server(
        ProjectsGrpcService(), server
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

