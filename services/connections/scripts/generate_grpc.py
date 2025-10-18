#!/usr/bin/env python3
import subprocess
import sys

from pathlib import Path


def generate_grpc_files():
    root = Path(__file__).parent.parent
    proto_path = root / "proto"
    generated_path = root / "generated"
    
    if not proto_path.exists():
        print("❌ Директория proto не найдена!")
        print("   Запустите скрипт из директории services/connections")
        sys.exit(1)
    
    generated_path.mkdir(exist_ok=True)
    
    cmd = [
        "python", "-m", "grpc_tools.protoc",
        f"--python_out={generated_path}",
        f"--grpc_python_out={generated_path}",
        f"--proto_path={proto_path}",
        f"{proto_path / 'connections.proto'}"
    ]
    
    print("🔧 Генерация gRPC файлов...")
    print(f"   Команда: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ gRPC файлы успешно сгенерированы!")
        print("   Созданы файлы в services/connections/generated/:")
        print("   - connections_pb2.py")
        print("   - connections_pb2_grpc.py")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при генерации gRPC файлов:")
        print(f"   {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ grpc_tools не найден!")
        print("   Установите: pip install grpcio-tools")
        sys.exit(1)

if __name__ == "__main__":
    generate_grpc_files()
