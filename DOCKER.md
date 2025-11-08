# 🐳 Docker Setup for System Architect Generator

Complete Docker configuration for deploying the System Architect Generator application to production environments, including OCI Container Instances.

## 📦 What's Included

### Docker Files

- **Frontend**
  - `frontend/Dockerfile` - Multi-stage build with Nginx
  - `frontend/nginx.conf` - Production Nginx configuration
  - `frontend/.dockerignore` - Optimized build context

- **Backend**
  - `backend/Dockerfile` - Optimized Python/FastAPI image
  - `backend/.dockerignore` - Optimized build context

- **Orchestration**
  - `docker-compose.yml` - Full stack orchestration
  - `.env.example` - Environment configuration template

### Scripts & Documentation

- `scripts/deploy-to-oci.sh` - Automated OCI deployment script
- `DEPLOYMENT.md` - Comprehensive deployment guide
- `Makefile` - Convenient Docker commands

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Check Docker installation
docker --version
docker-compose --version

# Minimum versions:
# - Docker: 20.10+
# - Docker Compose: 2.0+
```

### 2. Configuration

```bash
# Create environment file
cp .env.example .env

# Edit configuration
nano .env
```

Set these values:
```env
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=your_secure_password
MONGO_DATABASE=system_architect_generator
GOOGLE_API_KEY=your_google_api_key_here
DEFAULT_MODEL=gemini-2.0-flash-exp
FRONTEND_PORT=80
```

### 3. Build & Run

```bash
# Using Makefile (recommended)
make build
make up

# Or using docker-compose directly
docker-compose build
docker-compose up -d
```

### 4. Verify Deployment

```bash
# Check status
make ps

# Check health
make health

# View logs
make logs
```

Access the application:
- Frontend: http://localhost
- Health Check: http://localhost/health

## 🎯 Makefile Commands

```bash
make help          # Show all available commands
make build         # Build all images
make up            # Start all services
make down          # Stop all services
make restart       # Restart all services
make logs          # View all logs
make logs-backend  # View backend logs only
make logs-frontend # View frontend logs only
make health        # Check service health
make clean         # Remove everything (with confirmation)
make backup        # Backup MongoDB
make restore       # Restore MongoDB from backup
make deploy-oci    # Deploy to OCI
```

## ☁️ OCI Deployment

### Automated Deployment

```bash
# Run the deployment script
make deploy-oci

# Or directly
./scripts/deploy-to-oci.sh
```

The script will:
1. ✅ Build Docker images
2. ✅ Tag images for OCIR
3. ✅ Login to Oracle Container Registry
4. ✅ Push images to OCIR
5. ✅ Generate deployment information

### Manual OCI Setup

1. **Push Images to OCIR**

```bash
# Login
docker login <region>.ocir.io

# Tag
docker tag system-architect-generator-backend:latest <region>.ocir.io/<namespace>/<repo>/backend:latest
docker tag system-architect-generator-frontend:latest <region>.ocir.io/<namespace>/<repo>/frontend:latest

# Push
docker push <region>.ocir.io/<namespace>/<repo>/backend:latest
docker push <region>.ocir.io/<namespace>/<repo>/frontend:latest
```

2. **Create Container Instances**

Create three container instances in this order:

**MongoDB Container:**
- Image: `mongo:7.0`
- Memory: 4GB
- CPU: 2 OCPU
- Environment Variables:
  ```
  MONGO_INITDB_ROOT_USERNAME=admin
  MONGO_INITDB_ROOT_PASSWORD=<password>
  MONGO_INITDB_DATABASE=system_architect_generator
  ```
- Storage: Mount volume for `/data/db`

**Backend Container:**
- Image: `<region>.ocir.io/<namespace>/<repo>/backend:latest`
- Memory: 4GB
- CPU: 2 OCPU
- Environment Variables:
  ```
  MONGODB_URL=mongodb://admin:<password>@<mongodb-ip>:27017/system_architect_generator?authSource=admin
  GOOGLE_API_KEY=<your-key>
  DEFAULT_MODEL=gemini-2.0-flash-exp
  ```

**Frontend Container:**
- Image: `<region>.ocir.io/<namespace>/<repo>/frontend:latest`
- Memory: 2GB
- CPU: 1 OCPU
- Port: 80 (expose to internet)
- Depends on: Backend container

3. **Configure Networking**

- Create VCN with public and private subnets
- Frontend: Public subnet (allow 80/443)
- Backend & MongoDB: Private subnet
- Configure security lists appropriately

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Internet / Load Balancer        │
└─────────────────┬───────────────────────┘
                  │ Port 80/443
                  ▼
┌─────────────────────────────────────────┐
│         Frontend (Nginx + React)        │
│         - Serves static files           │
│         - Proxies API to backend        │
└─────────────────┬───────────────────────┘
                  │ /api → :8000
                  ▼
┌─────────────────────────────────────────┐
│        Backend (FastAPI + Python)       │
│        - AI Architecture Engine         │
│        - REST API endpoints             │
└─────────────────┬───────────────────────┘
                  │ :27017
                  ▼
┌─────────────────────────────────────────┐
│          MongoDB Database               │
│          - Persistent storage           │
│          - Projects & Knowledge Base    │
└─────────────────────────────────────────┘
```

## 🔍 Service Details

### Frontend Container

- **Base Image**: nginx:alpine
- **Port**: 80
- **Features**:
  - Multi-stage build (Node → Nginx)
  - Gzip compression
  - Static asset caching
  - API proxy to backend
  - SPA routing support
  - Security headers
- **Health Check**: `/health`

### Backend Container

- **Base Image**: python:3.11-slim
- **Port**: 8000
- **Features**:
  - Optimized Python dependencies
  - Multi-worker Uvicorn
  - Non-root user execution
  - Health check endpoint
- **Health Check**: `/api/health`

### MongoDB Container

- **Base Image**: mongo:7.0
- **Port**: 27017 (internal)
- **Features**:
  - Persistent data volumes
  - Init script support
  - Authentication enabled
- **Health Check**: MongoDB ping

## 🔒 Security

### Production Best Practices

1. **Environment Variables**
   - Never commit `.env` to git
   - Use strong passwords
   - Rotate credentials regularly

2. **Network Security**
   - Only expose port 80 publicly
   - Use private network for internal services
   - Configure firewall rules

3. **Container Security**
   - Run as non-root user
   - Minimal base images
   - Regular security updates

4. **Data Protection**
   - Enable MongoDB authentication
   - Regular backups
   - Encrypt sensitive data

## 📊 Monitoring & Logging

### View Logs

```bash
# All services
make logs

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb

# Last N lines
docker-compose logs --tail=100 backend
```

### Health Checks

```bash
# All services
make health

# Individual checks
curl http://localhost/health
curl http://localhost/api/health
```

### Resource Usage

```bash
# Container stats
make stats

# Detailed view
docker stats
```

## 🔧 Maintenance

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
make down
make build
make up
```

### Backup Database

```bash
# Create backup
make backup

# Backups stored in ./backups/
ls -lh ./backups/
```

### Restore Database

```bash
# Restore from backup
make restore

# Enter filename when prompted
```

### Scale Services

```bash
# Scale backend workers
docker-compose up -d --scale backend=3
```

## 🐛 Troubleshooting

### Check Service Status

```bash
docker-compose ps
make health
```

### Common Issues

**Port Already in Use**
```bash
# Change port in .env
FRONTEND_PORT=8080

# Restart
make restart
```

**Backend Can't Connect to MongoDB**
```bash
# Check MongoDB
docker-compose logs mongodb

# Restart services in order
docker-compose restart mongodb
docker-compose restart backend
```

**Frontend Can't Reach Backend**
```bash
# Check backend health
docker-compose exec backend curl http://localhost:8000/api/health

# Check nginx config
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
```

### View Detailed Logs

```bash
# Backend errors
docker-compose logs --tail=100 backend | grep ERROR

# Frontend access logs
docker-compose logs --tail=100 frontend
```

## 🧹 Cleanup

### Remove Services

```bash
# Stop services
make down

# Remove everything (with prompt)
make clean

# Force removal (no prompt)
docker-compose down -v --rmi all
```

### Remove Images

```bash
# Local images only
docker-compose down --rmi local

# All images
docker-compose down --rmi all
```

## 📚 Additional Resources

- [Deployment Guide](./DEPLOYMENT.md) - Comprehensive deployment documentation
- [Docker Documentation](https://docs.docker.com/)
- [OCI Container Instances](https://docs.oracle.com/iaas/Content/container-instances/home.htm)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

## 💡 Tips

1. **Development vs Production**
   - Use `docker-compose` for local development
   - Use individual containers or orchestration for production

2. **Performance Tuning**
   - Adjust worker count in backend Dockerfile
   - Configure MongoDB connection pool size
   - Enable CDN for static assets in production

3. **Cost Optimization**
   - Use smaller instance sizes where appropriate
   - Auto-scaling for backend services
   - Consider managed MongoDB service

## 🆘 Support

For issues or questions:
1. Check logs: `make logs`
2. Review health: `make health`
3. Consult [DEPLOYMENT.md](./DEPLOYMENT.md)
4. Check container status: `make ps`

---

**Happy Deploying! 🚀**
