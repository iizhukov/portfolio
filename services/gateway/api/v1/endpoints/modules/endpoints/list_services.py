from typing import List

from fastapi import APIRouter, Depends

from core.config import settings
from generated.modules import modules_pb2
from services.dependencies import get_grpc_manager
from services.grpc_client_manager import GrpcClientManager
from shared.schemas import ModuleServiceSchema

from ..utils import proto_to_service_schema


router = APIRouter()


@router.get("", response_model=List[ModuleServiceSchema], summary="Get registered services")
async def list_services(
    grpc_manager: GrpcClientManager = Depends(get_grpc_manager),
) -> List[ModuleServiceSchema]:
    client = await grpc_manager.get_client("modules")

    response = await grpc_manager.call_grpc_with_retry(
        client,
        client.ListServices,
        modules_pb2.ListServicesRequest(),
        timeout=settings.GRPC_TIMEOUT,
    )

    return [proto_to_service_schema(item) for item in response.services]
