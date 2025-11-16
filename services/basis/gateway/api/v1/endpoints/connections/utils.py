from schemas.connections.connections import ConnectionResponseSchema
from schemas.connections.health import HealthResponseSchema
from schemas.connections.image import ImageResponseSchema
from schemas.connections.status import StatusResponseSchema
from schemas.connections.working import WorkingResponseSchema


def proto_to_connection(proto) -> ConnectionResponseSchema:
    return ConnectionResponseSchema(
        id=proto.id,
        label=proto.label,
        type=proto.type,
        href=proto.href,
        value=proto.value,
    )


def proto_to_status(proto) -> StatusResponseSchema:
    return StatusResponseSchema(
        id=proto.id,
        status=proto.status,
    )


def proto_to_working(proto) -> WorkingResponseSchema:
    return WorkingResponseSchema(
        id=proto.id,
        working_on=proto.working_on,
        percentage=proto.percentage,
    )


def proto_to_image(proto) -> ImageResponseSchema:
    return ImageResponseSchema(
        id=proto.id,
        filename=proto.filename,
        content_type=proto.content_type,
        url=proto.url,
    )


def proto_to_health(proto) -> HealthResponseSchema:
    return HealthResponseSchema(
        status=proto.status,
        timestamp=proto.timestamp,
        database=proto.database,
        redpanda=proto.redpanda,
        modules_service=proto.modules_service,
    )
