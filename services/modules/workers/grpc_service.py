import asyncio
import sys

from pathlib import Path
from datetime import datetime

import grpc
from google.protobuf import empty_pb2

from core.config import settings
from core.logging import get_logger
from services.registry import ServiceRegistry


BASE_DIR = Path(__file__).resolve().parent.parent
GENERATED_ROOT = BASE_DIR / "generated"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from generated.modules import modules_pb2, modules_pb2_grpc
except ImportError as exc:
    logger = get_logger(__name__)
    logger.error("Failed to import generated gRPC modules: %s", exc)
    raise


logger = get_logger(__name__)
registry = ServiceRegistry(settings.DEFAULT_TTL_SECONDS)


class ModulesGrpcService(modules_pb2_grpc.ModulesServiceServicer):
    async def Register(
        self,
        request: modules_pb2.RegisterRequest,
        context: grpc.aio.ServicerContext,
    ) -> modules_pb2.RegisterResponse:
        if not request.service_name.strip():
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("service_name is required")
            return modules_pb2.RegisterResponse()

        if not request.version.strip():
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("version is required")
            return modules_pb2.RegisterResponse()

        if not request.admin_topic.strip():
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("admin_topic is required")
            return modules_pb2.RegisterResponse()

        try:
            record = await registry.register(
                service_name=request.service_name,
                version=request.version,
                admin_topic=request.admin_topic,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to register service %s: %s", request.service_name, exc)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to register service")
            return modules_pb2.RegisterResponse()

        instance_id = str(record.id)

        logger.info(
            "Service registered: %s (instance=%s, version=%s, admin_topic=%s)",
            record.service_name,
            instance_id,
            record.version,
            record.admin_topic,
        )

        return modules_pb2.RegisterResponse(
            instance_id=instance_id,
            ttl_seconds=record.ttl_seconds,
        )

    async def Heartbeat(
        self,
        request: modules_pb2.HeartbeatRequest,
        context: grpc.aio.ServicerContext,
    ) -> modules_pb2.HeartbeatResponse:
        try:
            record = await registry.heartbeat(request.instance_id)
        except Exception as exc:  # noqa: BLE001
            logger.error("Heartbeat processing failed for %s: %s", request.instance_id, exc)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to process heartbeat")
            return modules_pb2.HeartbeatResponse()

        if not record:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Instance not registered")
            return modules_pb2.HeartbeatResponse()

        logger.debug("Heartbeat received from %s", record.id)

        return modules_pb2.HeartbeatResponse(
            ok=True,
            ttl_seconds=record.ttl_seconds,
        )

    async def Deregister(
        self,
        request: modules_pb2.DeregisterRequest,
        context: grpc.aio.ServicerContext,
    ) -> empty_pb2.Empty:
        try:
            removed = await registry.deregister(request.instance_id)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to deregister %s: %s", request.instance_id, exc)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to deregister service")
            return empty_pb2.Empty()

        if not removed:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Instance not registered")

        else:
            logger.info("Service deregistered: %s", request.instance_id)

        return empty_pb2.Empty()

    async def ListServices(
        self,
        request: modules_pb2.ListServicesRequest,
        context: grpc.aio.ServicerContext,
    ) -> modules_pb2.ListServicesResponse:
        try:
            records = await registry.list_services()
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to list services: %s", exc)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to list services")
            return modules_pb2.ListServicesResponse()

        response = modules_pb2.ListServicesResponse()

        for record in records:
            info = response.services.add()
            info.id = record.id or 0
            info.service_name = record.service_name or ""
            info.version = record.version or ""
            info.admin_topic = record.admin_topic or ""
            info.ttl_seconds = record.ttl_seconds or 0
            info.status = record.status or "UNKNOWN"
            info.created_at = _datetime_to_str(record.created_at)
            info.updated_at = _datetime_to_str(record.updated_at)

        return response

    async def GetService(
        self,
        request: modules_pb2.GetServiceRequest,
        context: grpc.aio.ServicerContext,
    ) -> modules_pb2.GetServiceResponse:
        if not request.service_name.strip():
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("service_name is required")
            return modules_pb2.GetServiceResponse()

        try:
            record = await registry.get_service(request.service_name)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to fetch service %s: %s", request.service_name, exc)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to fetch service")
            return modules_pb2.GetServiceResponse()

        if record is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Service not found")
            return modules_pb2.GetServiceResponse()

        info = modules_pb2.ServiceInfo(
            id=record.id or 0,
            service_name=record.service_name or "",
            version=record.version or "",
            admin_topic=record.admin_topic or "",
            ttl_seconds=record.ttl_seconds or 0,
            status=record.status or "UNKNOWN",
            created_at=_datetime_to_str(record.created_at),
            updated_at=_datetime_to_str(record.updated_at),
        )

        return modules_pb2.GetServiceResponse(service=info)


async def serve() -> None:
    server = grpc.aio.server()
    modules_pb2_grpc.add_ModulesServiceServicer_to_server(ModulesGrpcService(), server)

    listen_addr = f"[::]:{settings.GRPC_PORT}"
    server.add_insecure_port(listen_addr)

    logger.info("Starting Modules gRPC server on %s", listen_addr)
    await server.start()

    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        logger.info("Shutting down Modules gRPC server")
        await server.stop(5)


__all__ = ["serve", "registry"]


def _datetime_to_str(value: datetime | None) -> str:
    if value is None:
        return ""
    if value.tzinfo is None:
        return value.isoformat() + "Z"
    return value.isoformat()

