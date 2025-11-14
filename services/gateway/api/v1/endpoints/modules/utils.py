from shared.schemas import ModuleServiceSchema


def proto_to_service_schema(proto_service) -> ModuleServiceSchema:
    return ModuleServiceSchema(
        id=proto_service.id,
        service_name=proto_service.service_name,
        version=proto_service.version,
        admin_topic=proto_service.admin_topic,
        ttl_seconds=proto_service.ttl_seconds,
        status=proto_service.status,
        created_at=proto_service.created_at or None,
        updated_at=proto_service.updated_at or None,
    )
