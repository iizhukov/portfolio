#!/usr/bin/env python3
import subprocess
import sys

from pathlib import Path


def generate_grpc_files():
    root = Path(__file__).parent.parent
    
    proto_locations = [
        root / "proto",
        root.parent.parent / "shared" / "python" / "shared" / "proto",
        Path("/shared/python/shared/proto"),
    ]
    
    proto_path = None
    for location in proto_locations:
        if location.exists() and (location / "connections.proto").exists():
            proto_path = location
            break
    
    if not proto_path:
        print("\033[91mError\033[0m: proto directory not found!")
        print("   Tried locations:")

        for location in proto_locations:
            print(f"   - {location}")

        print("   Make sure proto file exists in one of these locations")
        sys.exit(1)
    
    generated_path = root / "generated"
    
    generated_path.mkdir(exist_ok=True)
    
    cmd = [
        "python", "-m", "grpc_tools.protoc",
        f"--python_out={generated_path}",
        f"--grpc_python_out={generated_path}",
        f"--proto_path={proto_path}",
        f"{proto_path / 'connections.proto'}"
    ]
    
    print("Generating gRPC files...")
    print(f"   Proto source: {proto_path}")
    print(f"   Generated to: {generated_path}")
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("GRPC files generated \033[92msuccessfully\033[0m!")
        print("   Files created in services/connections/generated/:")
        print("   - connections_pb2.py")
        print("   - connections_pb2_grpc.py")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\033[91mError\033[0m generating gRPC files:")
        print(f"   {e.stderr}")
        return False
    except FileNotFoundError:
        print("\033[91mError\033[0m: grpc_tools not found!")
        print("   Install: pip install grpcio-tools")
        return False


def main():
    print("=" * 60)
    print("gRPC File Generation")
    print("=" * 60)
    print()
    
    if not generate_grpc_files():
        print("\n\033[91mFailed\033[0m to generate gRPC files")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Generation \033[92mcompleted\033[0m!")
    print("=" * 60)


if __name__ == "__main__":
    main()
