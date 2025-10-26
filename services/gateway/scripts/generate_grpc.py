#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path


def fix_imports_in_generated_files(generated_dir: Path):
    grpc_file = generated_dir / "connections_pb2_grpc.py"
    
    if grpc_file.exists():
        print("\nFixing imports in connections_pb2_grpc.py...")
        
        content = grpc_file.read_text()
        
        content = content.replace(
            "import connections_pb2 as connections__pb2",
            "from generated import connections_pb2 as connections__pb2"
        )
        
        grpc_file.write_text(content)
        print("\033[92m✓\033[0m Imports fixed successfully")


def generate_grpc_files():
    script_dir = Path(__file__).parent
    service_dir = script_dir.parent
    
    proto_locations = [
        service_dir / "proto",
        service_dir.parent.parent / "shared" / "python" / "shared" / "proto",
        Path("/shared/python/shared/proto"),
    ]
    
    proto_dir = None
    for location in proto_locations:
        if location.exists() and (location / "connections.proto").exists():
            proto_dir = location
            break
    
    if not proto_dir:
        print("\033[91mError\033[0m: No proto directory found!")
        print("   Tried locations:")

        for location in proto_locations:
            print(f"   - {location}")

        return False
    
    generated_dir = service_dir / "generated"
    generated_dir.mkdir(exist_ok=True)

    proto_files = list(proto_dir.glob("*.proto"))
    
    if not proto_files:
        print(f"\033[91mError\033[0m: No proto files found in {proto_dir}")
        return False
    
    print(f"Proto source: {proto_dir}")
    print(f"Generated to: {generated_dir}")
    print(f"Found {len(proto_files)} proto files:")
    for proto_file in proto_files:
        print(f"  - {proto_file.name}")
    
    for proto_file in proto_files:
        print(f"\n\033[94mInfo:\033[0m Generating Python files for {proto_file.name}...")
        
        try:
            cmd = [
                sys.executable, "-m", "grpc_tools.protoc",
                f"--proto_path={proto_dir}",
                f"--python_out={generated_dir}",
                f"--grpc_python_out={generated_dir}",
                f"--mypy_out={generated_dir}",
                str(proto_file)
            ]

            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"\033[92mSuccessfully\033[0m generated files for {proto_file.name}")
                

            else:
                print(f"\033[91mError\033[0m: generating files for {proto_file.name}:")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"\033[91mError\033[0m: Exception while generating files for {proto_file.name}: {e}")
            return False
    
    generated_files = list(generated_dir.glob("*.py"))
    print(f"\nGenerated {len(generated_files)} Python files:")
    for file in generated_files:
        print(f"  - {file.name}")
    
    fix_imports_in_generated_files(generated_dir)
    
    return True


def main():
    print("Starting gRPC file generation...")
    
    success = generate_grpc_files()
    
    if success:
        print("\ngRPC file generation completed \033[92mSuccessfully\033[0m!")
        sys.exit(0)
    else:
        print("\n\033[91mError\033[0m: gRPC file generation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
