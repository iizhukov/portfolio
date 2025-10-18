#!/usr/bin/env python3
import subprocess
import sys
import os

from pathlib import Path


def run_command(cmd, description):
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, check=True, shell=True, capture_output=True, text=True)
        print(f"✅ {description} завершено")

        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при {description.lower()}:")
        print(f"   {e.stderr}")

        return False


def setup_connections_service():
    print("🚀 Настройка Connections Service")
    print("=" * 50)

    root = Path(__file__).parent.parent
    proto_path = root / "proto/connections.proto"
    if not proto_path.exists():
        print("❌ Файл proto/connections.proto не найден!")
        print("   Запустите скрипт из директории services/connections/scripts/")
        sys.exit(1)
    
    generate_grpc_path = root / "scripts/generate_grpc.py"
    if not run_command(f"python {generate_grpc_path}", "Генерация gRPC файлов"):
        return False
    
    init_db_path = root / "scripts/init_db.py"
    if not run_command(f"python {init_db_path}", "Инициализация базы данных"):
        return False
    
    print("\n✅ Настройка Connections Service завершена!")
    print("\n📋 Следующие шаги:")
    print("   1. Настройте .env файл из env.example")
    print("   2. Запустите сервис: make dev-connections")
    print("   3. Проверьте API: http://localhost:8001/docs")
    print("   4. Проверьте gRPC: порт 50051")


if __name__ == "__main__":
    setup_connections_service()
