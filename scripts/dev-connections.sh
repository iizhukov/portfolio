#!/bin/bash
set -e

echo "🚀 Запуск Connections сервиса для разработки"

# Проверяем, что shared пакет установлен
python -c "import shared.env_utils" 2>/dev/null || {
    echo "❌ Shared пакет не установлен. Запустите: ./scripts/dev-setup.sh"
    exit 1
}

# Переходим в папку Connections
cd services/connections

# Проверяем .env файл
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден. Создайте его из env.example"
    exit 1
fi

# Загружаем переменные окружения
export $(cat .env | grep -v '^#' | xargs)

echo "🔧 Переменные окружения загружены"
echo "🌐 Запуск Connections на http://localhost:8001"
echo "📚 API документация: http://localhost:8001/docs"
echo ""

# Запускаем сервис
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
