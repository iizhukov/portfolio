#!/bin/bash
set -e

echo "🚀 Настройка окружения для разработки Portfolio проекта"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Проверяем, что мы в корне проекта
if [ ! -f "docker-compose.yml" ]; then
    print_error "Запустите скрипт из корня проекта!"
    exit 1
fi

# Устанавливаем shared пакет
print_status "Установка shared пакета..."
if [ -d "shared/python" ]; then
    pip install -e ./shared/python
    print_status "Shared пакет установлен"
else
    print_error "Папка shared/python не найдена!"
    exit 1
fi

# Создаем .env файлы если их нет
print_status "Проверка .env файлов..."

# Gateway .env
if [ ! -f "services/gateway/.env" ]; then
    if [ -f "services/gateway/env.example" ]; then
        cp services/gateway/env.example services/gateway/.env
        print_status "Создан services/gateway/.env из примера"
    else
        print_warning "services/gateway/env.example не найден"
    fi
fi

# Connections .env
if [ ! -f "services/connections/.env" ]; then
    if [ -f "services/connections/env.example" ]; then
        cp services/connections/env.example services/connections/.env
        print_status "Создан services/connections/.env из примера"
    else
        print_warning "services/connections/env.example не найден"
    fi
fi

# Проверяем Python зависимости
print_status "Проверка Python зависимостей..."

# Gateway dependencies
if [ -f "services/gateway/requirements.txt" ]; then
    print_status "Установка зависимостей Gateway..."
    pip install -r services/gateway/requirements.txt
fi

# Connections dependencies
if [ -f "services/connections/requirements.txt" ]; then
    print_status "Установка зависимостей Connections..."
    pip install -r services/connections/requirements.txt
fi

print_status "Настройка завершена!"
echo ""
echo "🎯 Доступные команды для разработки:"
echo "  make dev-gateway     - Запустить Gateway локально"
echo "  make dev-connections - Запустить Connections локально"
echo "  make dev-docker      - Запустить все в Docker"
echo "  make dev-infra       - Запустить только инфраструктуру"
echo ""
echo "📝 Не забудьте настроить .env файлы в services/*/"
