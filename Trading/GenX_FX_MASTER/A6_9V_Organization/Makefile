# GenX_FX Makefile

.PHONY: help install dev api-start docker-build docker-up docker-down db-up db-migrate clean

help:
	@echo "GenX_FX Commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Start development server"
	@echo "  api-start   - Start API server"
	@echo "  docker-build- Build Docker image"
	@echo "  docker-up   - Start all services"
	@echo "  docker-down - Stop all services"
	@echo "  db-up       - Start database only"
	@echo "  db-migrate  - Run database migrations"
	@echo "  clean       - Clean up containers"

install:
	pip install -r requirements.txt

dev:
	python enhanced_trading.py

api-start:
	cd api && python main.py

docker-build:
	docker build -f Dockerfile.enhanced -t genx-enhanced .

docker-up:
	docker-compose -f docker-compose.production.yml up -d

docker-down:
	docker-compose -f docker-compose.production.yml down

db-up:
	docker-compose -f docker-compose.production.yml up -d postgres redis

db-migrate:
	python setup_database.py

clean:
	docker system prune -f
	docker volume prune -f
