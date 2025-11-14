#!/usr/bin/env python3
from pathlib import Path

from shared.scripts.generate_grpc import generate_grpc_files


def main() -> None:
    root = Path(__file__).parent.parent
    proto_root = root.parent.parent / "shared" / "python" / "shared" / "proto"
    output_dir = root / "generated"

    targets = [
        ("connections/connections.proto", "connections"),
        ("projects/projects.proto", "projects"),
        ("modules/modules.proto", "modules"),
        ("admin/admin.proto", "admin"),
    ]

    generate_grpc_files(proto_root=proto_root, output_dir=output_dir, targets=targets)


if __name__ == "__main__":
    main()
