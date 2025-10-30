import asyncio
import sys
from pathlib import Path

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

