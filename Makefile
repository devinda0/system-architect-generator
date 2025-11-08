.PHONY: help build up down restart logs clean deploy-oci

# Default target
help:
	@echo "Available commands:"
	@echo "  make build        - Build all Docker images"
	@echo "  make up           - Start all services"
	@echo "  make down         - Stop all services"
	@echo "  make restart      - Restart all services"
	@echo "  make logs         - View logs from all services"
	@echo "  make logs-backend - View backend logs"
	@echo "  make logs-frontend- View frontend logs"
	@echo "  make clean        - Stop and remove all containers, networks, and volumes"
	@echo "  make test         - Run tests"
	@echo "  make deploy-oci   - Deploy to OCI Container Registry"
	@echo "  make health       - Check health of all services"

# Build all images
build:
	@echo "Building Docker images..."
	docker-compose build

# Start all services
up:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "Services started. Access the application at http://localhost"

# Stop all services
down:
	@echo "Stopping all services..."
	docker-compose down

# Restart all services
restart:
	@echo "Restarting all services..."
	docker-compose restart

# View logs
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-mongodb:
	docker-compose logs -f mongodb

# Check health of services
health:
	@echo "Checking service health..."
	@echo "\n=== Frontend Health ==="
	@curl -s http://localhost/health || echo "Frontend not responding"
	@echo "\n\n=== Backend Health (via frontend proxy) ==="
	@curl -s http://localhost/api/health || echo "Backend not responding"
	@echo "\n\n=== Container Status ==="
	@docker-compose ps

# Clean up everything
clean:
	@echo "WARNING: This will remove all containers, networks, and volumes!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v --rmi local; \
		echo "Cleanup complete"; \
	else \
		echo "Cleanup cancelled"; \
	fi

# Run backend tests
test:
	@echo "Running backend tests..."
	docker-compose exec backend pytest

# Deploy to OCI
deploy-oci:
	@echo "Starting OCI deployment..."
	./scripts/deploy-to-oci.sh

# Build and start
run: build up

# View specific service
ps:
	docker-compose ps

# Pull latest images
pull:
	docker-compose pull

# Show resource usage
stats:
	docker stats --no-stream

# Backup MongoDB
backup:
	@echo "Creating MongoDB backup..."
	@mkdir -p ./backups
	docker-compose exec -T mongodb mongodump --uri="mongodb://admin:admin123@localhost:27017/system_architect_generator?authSource=admin" --archive > ./backups/mongodb-backup-$$(date +%Y%m%d-%H%M%S).archive
	@echo "Backup created in ./backups/"

# Restore MongoDB
restore:
	@echo "Available backups:"
	@ls -lh ./backups/
	@read -p "Enter backup filename to restore: " backup; \
	docker-compose exec -T mongodb mongorestore --uri="mongodb://admin:admin123@localhost:27017/system_architect_generator?authSource=admin" --archive < ./backups/$$backup
	@echo "Restore complete"
