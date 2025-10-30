#!/usr/bin/env python3
from __future__ import annotations

import sys
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


@dataclass(frozen=True)
class ProtoTarget:
    proto: Path | str
    package: str

    def resolved_proto(self, proto_root: Path) -> Path:
        path = Path(self.proto)
        return path if path.is_absolute() else proto_root / path

    @property
    def module(self) -> str:
        return Path(self.proto).stem


def _ensure_package_inits(output_dir: Path, packages: Iterable[str]) -> None:
    (output_dir / "__init__.py").touch(exist_ok=True)
    for package in packages:
        pkg_dir = output_dir / package
        pkg_dir.mkdir(parents=True, exist_ok=True)
        (pkg_dir / "__init__.py").touch(exist_ok=True)


def _fix_imports(output_dir: Path, module_package_map: dict[str, str]) -> None:
    pattern = "from {package} import {module}_pb2 as {alias}"

    for grpc_file in output_dir.rglob("*_pb2_grpc.py"):
        content = grpc_file.read_text()
        updated = False

        for module, package in module_package_map.items():
            alias = f"{module}_dot_{module}__pb2"
            search = pattern.format(package=package, module=module, alias=alias)
            replacement = f"from generated.{package} import {module}_pb2 as {alias}"

            if search in content and replacement not in content:
                content = content.replace(search, replacement)
                updated = True

        if updated:
            grpc_file.write_text(content)
            print(f"✓ Fixed imports in {grpc_file}")


def generate_grpc_files(
    *,
    proto_root: Path,
    output_dir: Path,
    targets: Sequence[tuple[str | Path, str]] | Sequence[ProtoTarget],
) -> None:
    if not targets:
        raise ValueError("No proto targets provided")

    normalized: list[ProtoTarget] = [
        t if isinstance(t, ProtoTarget) else ProtoTarget(proto=t[0], package=t[1])
        for t in targets
    ]

    module_package_map = {target.module: target.package for target in normalized}
    packages = {target.package for target in normalized}

    output_dir.mkdir(parents=True, exist_ok=True)
    _ensure_package_inits(output_dir, packages)

    for target in normalized:
        proto_file = target.resolved_proto(proto_root)
        if not proto_file.exists():
            raise FileNotFoundError(f"Proto file not found: {proto_file}")

        cmd = [
            sys.executable,
            "-m",
            "grpc_tools.protoc",
            f"--proto_path={proto_root}",
            f"--python_out={output_dir}",
            f"--grpc_python_out={output_dir}",
            f"--mypy_out={output_dir}",
            str(proto_file),
        ]

        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                "Failed to generate gRPC bindings for "
                f"{proto_file}:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
            )

    _fix_imports(output_dir, module_package_map)


__all__ = ["ProtoTarget", "generate_grpc_files"]
