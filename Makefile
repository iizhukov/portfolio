.PHONY: help dev dev-build dev-logs dev-down clean test lint format

help:
	@echo "Portfolio Project - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


dev:
	docker-compose up -d

dev-build:
	docker-compose up -d --build

dev-logs:
	docker-compose logs -f

dev-down:
	docker-compose down


infra:
	docker-compose -f infrastructure/docker-compose.yml up -d

infra-build:
	docker-compose -f infrastructure/docker-compose.yml up -d --build

infra-logs:
	docker-compose -f infrastructure/docker-compose.yml logs -f

infra-down:
	docker-compose -f infrastructure/docker-compose.yml down

apps:
	docker-compose -f apps/docker-compose.yml up -d

apps-build:
	docker-compose -f apps/docker-compose.yml up -d --build

apps-logs:
	docker-compose -f apps/docker-compose.yml logs -f

apps-down:
	docker-compose -f apps/docker-compose.yml down

services:
	docker-compose -f services/docker-compose.yml up -d

services-build:
	docker-compose -f services/docker-compose.yml up -d --build

services-logs:
	docker-compose -f services/docker-compose.yml logs -f

services-down:
	docker-compose -f services/docker-compose.yml down


health:
	@echo "Checking service health..."
	@curl -f http://localhost/ || echo "❌ Web client health check failed"
	@curl -f http://localhost:8000/ || echo "❌ API Gateway health check failed"
	@curl -f http://localhost:8001/health || echo "❌ Connections service health check failed"
	@echo "✅ Health checks completed"

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

clean-all:
	docker-compose down -v --remove-orphans
	docker system prune -af


setup:
	@echo "Setting up development environment..."
	$(MAKE) dev-build
	@echo "Waiting for services to start..."
	sleep 30
	$(MAKE) health
	@echo "Setup complete! Visit http://localhost to see the application."

env-example:
	@echo "Creating example environment files..."
	@cp services/connections/env.example services/connections/.env
	@echo "Please update the .env files with your actual values"


status:
	docker-compose ps

status-infra:
	docker-compose -f infrastructure/docker-compose.yml ps

status-apps:
	docker-compose -f apps/docker-compose.yml ps

status-services:
	docker-compose -f services/docker-compose.yml ps


restart:
	docker-compose restart

restart-infra:
	docker-compose -f infrastructure/docker-compose.yml restart

restart-apps:
	docker-compose -f apps/docker-compose.yml restart

restart-services:
	docker-compose -f services/docker-compose.yml restart

