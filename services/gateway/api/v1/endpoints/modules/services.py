from typing import List

import grpc
from fastapi import APIRouter, Depends, HTTPException

from core.config import settings
from services.dependencies import get_grpc_manager
from services.grpc_client_manager import GrpcClientManager
from shared.schemas import ModuleServiceSchema


router = APIRouter()


@router.get("", response_model=List[ModuleServiceSchema], summary="Get registered services")
async def list_services(grpc_manager: GrpcClientManager = Depends(get_grpc_manager)) -> List[ModuleServiceSchema]:
    client = await grpc_manager.get_client("modules")

    from generated.modules import modules_pb2

    response = await grpc_manager.call_grpc_with_retry(
        client,
        client.ListServices,
        modules_pb2.ListServicesRequest(),
        timeout=settings.GRPC_TIMEOUT,
    )

    services: List[ModuleServiceSchema] = []

    for item in response.services:
        services.append(
            ModuleServiceSchema(
                id=item.id,
                service_name=item.service_name,
                version=item.version,
                admin_topic=item.admin_topic,
                ttl_seconds=item.ttl_seconds,
                status=item.status,
                created_at=item.created_at or None,
                updated_at=item.updated_at or None,
            )
        )

    return services


@router.get("/{service_name}", response_model=ModuleServiceSchema, summary="Get service details")
async def get_service_details(service_name: str, grpc_manager: GrpcClientManager = Depends(get_grpc_manager)) -> ModuleServiceSchema:
    client = await grpc_manager.get_client("modules")

    from generated.modules import modules_pb2

    try:
        response = await grpc_manager.call_grpc_with_retry(
            client,
            client.GetService,
            modules_pb2.GetServiceRequest(service_name=service_name),
            timeout=settings.GRPC_TIMEOUT,
        )
    except grpc.RpcError as exc:
        if exc.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Service not found") from exc
        raise HTTPException(status_code=502, detail="Modules service error") from exc

    service = response.service

    return ModuleServiceSchema(
        id=service.id,
        service_name=service.service_name,
        version=service.version,
        admin_topic=service.admin_topic,
        ttl_seconds=service.ttl_seconds,
        status=service.status,
        created_at=service.created_at or None,
        updated_at=service.updated_at or None,
    )

