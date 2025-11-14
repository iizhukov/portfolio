.PHONY: help up build logs down clean status restart python-base

help:
	@echo "Portfolio Project - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


up: python-base
	docker-compose up -d

build: python-base
	docker-compose up -d --build

logs:
	docker-compose logs -f

down:
	docker-compose down

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

status:
	docker-compose ps

restart:
	docker-compose restart


python-base:
	docker build -f shared/python/Dockerfile -t portfolio-python-base .
