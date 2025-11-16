import grpc
from fastapi import APIRouter, Depends, HTTPException

from core.config import settings
from generated.modules import modules_pb2
from services.dependencies import get_grpc_manager
from services.grpc_client_manager import GrpcClientManager
from shared.schemas import ModuleServiceSchema

from ..utils import proto_to_service_schema


router = APIRouter()


@router.get("/{service_name}", response_model=ModuleServiceSchema, summary="Get service details")
async def get_service_details(
    service_name: str,
    grpc_manager: GrpcClientManager = Depends(get_grpc_manager),
) -> ModuleServiceSchema:
    client = await grpc_manager.get_client("modules")

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

    return proto_to_service_schema(response.service)
