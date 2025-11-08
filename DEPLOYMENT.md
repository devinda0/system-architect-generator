# Docker Deployment Guide

This guide explains how to deploy the System Architect Generator application using Docker and Docker Compose, suitable for OCI Container Instances and other cloud platforms.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM available
- 10GB disk space
- Google Gemini API Key

## 🏗️ Architecture

The application consists of three main services:

1. **Frontend** (Nginx + React) - Port 80
2. **Backend** (FastAPI + Python) - Port 8000 (internal)
3. **MongoDB** - Port 27017 (internal)

All services communicate through a Docker network, with only the frontend exposed to the internet.

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd system-architect-generator
```

### 2. Configure Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and set your values:

```env
# MongoDB Configuration
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=your_secure_password_here
MONGO_DATABASE=system_architect_generator

# Google Gemini API Configuration
GOOGLE_API_KEY=your_google_api_key_here
DEFAULT_MODEL=gemini-2.0-flash-exp

# Frontend Port (default: 80)
FRONTEND_PORT=80
```

### 3. Build and Run

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost (or your server IP)
- **Health Check**: http://localhost/health

## 🔧 Individual Service Commands

### Build Services Separately

```bash
# Build backend
docker-compose build backend

# Build frontend
docker-compose build frontend
```

### Start/Stop Services

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes database)
docker-compose down -v

# Restart a specific service
docker-compose restart backend
docker-compose restart frontend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

## ☁️ OCI Container Instance Deployment

### Option 1: Docker Compose (OCI Container Instances with Docker Compose support)

1. **Push images to OCI Container Registry (OCIR)**:

```bash
# Login to OCIR
docker login <region-key>.ocir.io

# Tag images
docker tag system-architect-generator-backend:latest <region-key>.ocir.io/<tenancy-namespace>/<repo-name>/backend:latest
docker tag system-architect-generator-frontend:latest <region-key>.ocir.io/<tenancy-namespace>/<repo-name>/frontend:latest

# Push images
docker push <region-key>.ocir.io/<tenancy-namespace>/<repo-name>/backend:latest
docker push <region-key>.ocir.io/<tenancy-namespace>/<repo-name>/frontend:latest
```

2. **Create OCI Container Instance**:
   - Use the OCI Console or CLI
   - Provide the docker-compose.yml file
   - Set environment variables
   - Configure networking (allow port 80)

### Option 2: Individual Containers

Deploy each service as a separate container instance:

1. **MongoDB Container**
2. **Backend Container**
3. **Frontend Container**

Ensure proper networking between containers using OCI VCN.

## 🔍 Health Checks

All services include health checks:

- **Frontend**: `http://localhost/health`
- **Backend**: `http://localhost:8000/api/health` (internal)
- **MongoDB**: MongoDB ping command

## 📊 Monitoring

### Check Container Status

```bash
docker-compose ps
```

### Resource Usage

```bash
docker stats
```

### Health Status

```bash
# Frontend
curl http://localhost/health

# Backend (from inside the network)
docker exec system-architect-frontend curl http://backend:8000/api/health
```

## 🔐 Security Best Practices

1. **Change Default Passwords**: Update MongoDB credentials in `.env`
2. **API Keys**: Keep `GOOGLE_API_KEY` secure, never commit to git
3. **Network**: Only expose port 80 (frontend) to the internet
4. **Updates**: Regularly update base images
5. **Backup**: Regular MongoDB backups

## 🛠️ Troubleshooting

### Backend Can't Connect to MongoDB

```bash
# Check MongoDB is running
docker-compose ps mongodb

# Check MongoDB logs
docker-compose logs mongodb

# Restart MongoDB
docker-compose restart mongodb
```

### Frontend Can't Reach Backend

```bash
# Check backend is healthy
docker-compose exec backend curl http://localhost:8000/api/health

# Check nginx configuration
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf

# Restart frontend
docker-compose restart frontend
```

### Port Already in Use

```bash
# Change FRONTEND_PORT in .env
FRONTEND_PORT=8080

# Restart
docker-compose down
docker-compose up -d
```

### View Service Logs

```bash
# Last 100 lines
docker-compose logs --tail=100 backend

# Follow logs in real-time
docker-compose logs -f backend
```

## 🔄 Updates and Maintenance

### Update Application Code

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Backup MongoDB

```bash
# Create backup
docker-compose exec mongodb mongodump --uri="mongodb://admin:admin123@localhost:27017/system_architect_generator?authSource=admin" --out=/data/backup

# Copy backup to host
docker cp system-architect-mongodb:/data/backup ./mongodb-backup
```

### Restore MongoDB

```bash
# Copy backup to container
docker cp ./mongodb-backup system-architect-mongodb:/data/backup

# Restore
docker-compose exec mongodb mongorestore --uri="mongodb://admin:admin123@localhost:27017/system_architect_generator?authSource=admin" /data/backup
```

## 📈 Scaling

### Horizontal Scaling (Multiple Instances)

For production workloads:

```bash
# Scale backend workers
docker-compose up -d --scale backend=3
```

Note: This requires a load balancer and shared MongoDB instance.

### Vertical Scaling (More Resources)

Update Docker Compose with resource limits:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## 🧹 Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes (⚠️ deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Complete cleanup
docker system prune -a --volumes
```

## 📞 Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review health checks
- Verify environment variables
- Check network connectivity

## 🔗 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [OCI Container Instances](https://docs.oracle.com/en-us/iaas/Content/container-instances/home.htm)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Nginx Documentation](https://nginx.org/en/docs/)
