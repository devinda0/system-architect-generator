.PHONY: help build up down restart logs logs-backend logs-mongodb shell-backend shell-mongodb test validate clean rebuild ps health

# Default target
help:
	@echo "System Architect Generator - Docker Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make build         - Build Docker images"
	@echo "  make up            - Start all services"
	@echo "  make down          - Stop all services"
	@echo "  make restart       - Restart all services"
	@echo "  make logs          - View logs from all services"
	@echo "  make logs-backend  - View backend logs"
	@echo "  make logs-mongodb  - View MongoDB logs"
	@echo "  make shell-backend - Open shell in backend container"
	@echo "  make shell-mongodb - Open MongoDB shell"
	@echo "  make test          - Run tests"
	@echo "  make validate      - Validate Docker setup"
	@echo "  make clean         - Stop and remove containers"
	@echo "  make rebuild       - Clean rebuild everything"
	@echo "  make ps            - Show running containers"
	@echo "  make health        - Check health status"
	@echo ""

# Build Docker images
build:
	@echo "Building Docker images..."
	docker compose build

# Start all services
up:
	@echo "Starting all services..."
	docker compose up -d
	@echo ""
	@echo "Services started! Access points:"
	@echo "  • API: http://localhost:8000"
	@echo "  • API Docs: http://localhost:8000/docs"
	@echo "  • Health: http://localhost:8000/api/health"
	@echo ""
	@echo "Run 'make validate' to verify setup"

# Stop all services
down:
	@echo "Stopping all services..."
	docker compose down

# Restart all services
restart:
	@echo "Restarting all services..."
	docker compose restart

# View logs from all services
logs:
	docker compose logs -f

# View backend logs
logs-backend:
	docker compose logs -f backend

# View MongoDB logs
logs-mongodb:
	docker compose logs -f mongodb

# Open shell in backend container
shell-backend:
	docker compose exec backend /bin/bash

# Open MongoDB shell
shell-mongodb:
	docker compose exec mongodb mongosh -u admin -p admin123 --authenticationDatabase admin

# Run tests
test:
	@echo "Running tests..."
	docker compose exec backend pytest

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	docker compose exec backend pytest --cov=app --cov-report=html
	@echo "Coverage report generated in htmlcov/"

# Validate Docker setup
validate:
	@echo "Validating Docker setup..."
	python scripts/validate_docker_setup.py

# Stop and remove containers
clean:
	@echo "Stopping and removing containers..."
	docker compose down
	@echo "Cleaned up!"

# Clean rebuild everything
rebuild:
	@echo "Performing clean rebuild..."
	docker compose down -v
	docker compose up --build -d
	@echo ""
	@echo "Rebuild complete! Run 'make validate' to verify"

# Show running containers
ps:
	docker compose ps

# Check health status
health:
	@echo "Checking health status..."
	@curl -s http://localhost:8000/api/health | python -m json.tool || echo "Backend not accessible"

# Quick start (build and run)
start: build up
	@echo ""
	@echo "Waiting for services to start..."
	@sleep 5
	@make health

# Stop and remove everything including volumes
nuke:
	@echo "⚠️  WARNING: This will remove all containers, volumes, and data!"
	@echo "Press Ctrl+C to cancel, or Enter to continue..."
	@read confirm
	docker compose down -v
	@echo "Everything removed!"
