import asyncio
from datetime import datetime, timedelta, timezone

import grpc
import pytest
from sqlalchemy import text

from generated.modules import modules_pb2

pytestmark = pytest.mark.asyncio


async def test_register_and_list_services(grpc_stub):
    register_response = await grpc_stub.Register(
        modules_pb2.RegisterRequest(
            service_name="gateway",
            version="1.0.0",
            admin_topic="admin.gateway",
        )
    )

    assert register_response.instance_id
    assert register_response.ttl_seconds == 30

    list_response = await grpc_stub.ListServices(modules_pb2.ListServicesRequest())
    assert len(list_response.services) == 1
    service = list_response.services[0]
    assert service.service_name == "gateway"
    assert service.status == "ONLINE"


async def test_register_validation(grpc_stub):
    with pytest.raises(grpc.aio.AioRpcError) as exc:
        await grpc_stub.Register(
            modules_pb2.RegisterRequest(
                service_name="",
                version="1.0.0",
                admin_topic="admin.topic",
            )
        )
    assert exc.value.code() == grpc.StatusCode.INVALID_ARGUMENT


async def test_heartbeat_and_get_service(grpc_stub):
    register_response = await grpc_stub.Register(
        modules_pb2.RegisterRequest(
            service_name="projects",
            version="1.0.0",
            admin_topic="admin.projects",
        )
    )
    instance_id = register_response.instance_id

    heartbeat_response = await grpc_stub.Heartbeat(
        modules_pb2.HeartbeatRequest(instance_id=instance_id)
    )
    assert heartbeat_response.ok is True

    get_response = await grpc_stub.GetService(
        modules_pb2.GetServiceRequest(service_name="projects")
    )
    assert get_response.service.service_name == "projects"
    assert get_response.service.status == "ONLINE"


async def test_heartbeat_not_found(grpc_stub):
    with pytest.raises(grpc.aio.AioRpcError) as exc:
        await grpc_stub.Heartbeat(
            modules_pb2.HeartbeatRequest(instance_id="999")
        )
    assert exc.value.code() == grpc.StatusCode.NOT_FOUND


async def test_deregister(grpc_stub):
    register_response = await grpc_stub.Register(
        modules_pb2.RegisterRequest(
            service_name="connections",
            version="1.0.0",
            admin_topic="admin.connections",
        )
    )
    instance_id = register_response.instance_id

    await grpc_stub.Deregister(
        modules_pb2.DeregisterRequest(instance_id=instance_id)
    )

    with pytest.raises(grpc.aio.AioRpcError) as exc:
        await grpc_stub.GetService(
            modules_pb2.GetServiceRequest(service_name="connections")
        )
    assert exc.value.code() == grpc.StatusCode.NOT_FOUND


async def test_get_service_not_found(grpc_stub):
    with pytest.raises(grpc.aio.AioRpcError) as exc:
        await grpc_stub.GetService(
            modules_pb2.GetServiceRequest(service_name="missing")
        )
    assert exc.value.code() == grpc.StatusCode.NOT_FOUND


async def test_list_services_marks_offline(grpc_stub, database):
    register_response = await grpc_stub.Register(
        modules_pb2.RegisterRequest(
            service_name="worker",
            version="1.0.0",
            admin_topic="admin.worker",
        )
    )
    instance_id = register_response.instance_id

    async with database.async_session() as session:
        await session.execute(
            text("UPDATE services SET updated_at = :updated WHERE id = :id"),
            {
                "updated": datetime.now(timezone.utc).replace(tzinfo=None)
                - timedelta(seconds=120),
                "id": int(instance_id),
            },
        )
        await session.commit()

    list_response = await grpc_stub.ListServices(modules_pb2.ListServicesRequest())
    service = next(
        (svc for svc in list_response.services if svc.service_name == "worker"), None
    )
    assert service is not None
    assert service.status == "OFFLINE"

