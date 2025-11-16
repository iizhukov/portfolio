from schemas.projects.projects import ProjectResponseSchema


def proto_project_to_schema(proto_project) -> ProjectResponseSchema:
    children = [
        proto_project_to_schema(child)
        for child in getattr(proto_project, "children", [])
    ]

    return ProjectResponseSchema(
        id=proto_project.id,
        name=proto_project.name,
        type=proto_project.type,
        file_type=proto_project.file_type if proto_project.HasField("file_type") else None,
        parent_id=proto_project.parent_id if proto_project.HasField("parent_id") else None,
        url=proto_project.url if proto_project.HasField("url") else None,
        children=children,
        created_at=proto_project.created_at if proto_project.created_at else None,
        updated_at=proto_project.updated_at if proto_project.updated_at else None,
    )


