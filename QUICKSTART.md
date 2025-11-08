# 🎯 Quick Reference - Docker Deployment

## Essential Commands

### Local Development
```bash
# Quick start (interactive)
./start.sh

# Manual start
make build && make up

# View logs
make logs

# Stop services
make down
```

### Health & Status
```bash
# Check all services
make health

# View container status
make ps

# Resource usage
make stats
```

### Database Operations
```bash
# Backup
make backup

# Restore
make restore
```

### Deployment to OCI
```bash
# Automated deployment
make deploy-oci

# Manual steps
1. docker login <region>.ocir.io
2. docker tag <image> <ocir-path>
3. docker push <ocir-path>
```

## Service URLs

| Service  | Local URL                    | Port |
|----------|------------------------------|------|
| Frontend | http://localhost             | 80   |
| Health   | http://localhost/health      | 80   |
| Backend  | http://localhost:8000 (internal) | 8000 |
| MongoDB  | mongodb://localhost:27017 (internal) | 27017 |

## Environment Variables

### Required
- `GOOGLE_API_KEY` - Your Google Gemini API key
- `MONGO_ROOT_PASSWORD` - MongoDB admin password

### Optional
- `FRONTEND_PORT` - Frontend port (default: 80)
- `DEFAULT_MODEL` - AI model (default: gemini-2.0-flash-exp)

## Container Sizes (Recommended)

| Service  | CPU    | Memory | Storage |
|----------|--------|--------|---------|
| Frontend | 1 OCPU | 2 GB   | 1 GB    |
| Backend  | 2 OCPU | 4 GB   | 2 GB    |
| MongoDB  | 2 OCPU | 4 GB   | 20 GB   |

## Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs <service-name>

# Restart service
docker-compose restart <service-name>
```

### Port Conflict
```bash
# Edit .env
FRONTEND_PORT=8080

# Restart
make restart
```

### Database Issues
```bash
# Reset MongoDB
docker-compose down -v
docker-compose up -d mongodb
docker-compose up -d backend
docker-compose up -d frontend
```

## Files Structure

```
.
├── docker-compose.yml          # Main orchestration
├── .env.example               # Environment template
├── Makefile                   # Convenient commands
├── start.sh                   # Quick start script
├── DOCKER.md                  # Docker documentation
├── DEPLOYMENT.md              # Deployment guide
├── frontend/
│   ├── Dockerfile            # Frontend image
│   └── nginx.conf            # Nginx config
├── backend/
│   └── Dockerfile            # Backend image
└── scripts/
    └── deploy-to-oci.sh      # OCI deployment script
```

## Quick Deployment Checklist

- [ ] Install Docker & Docker Compose
- [ ] Copy `.env.example` to `.env`
- [ ] Set `GOOGLE_API_KEY` in `.env`
- [ ] Set `MONGO_ROOT_PASSWORD` in `.env`
- [ ] Run `./start.sh` or `make build && make up`
- [ ] Verify at http://localhost/health
- [ ] Check logs with `make logs`

## OCI Deployment Checklist

- [ ] Run `make deploy-oci`
- [ ] Create MongoDB container instance
- [ ] Create Backend container instance
- [ ] Create Frontend container instance
- [ ] Configure VCN and security lists
- [ ] Set environment variables in OCI
- [ ] Verify connectivity
- [ ] Configure load balancer (optional)
- [ ] Set up monitoring
- [ ] Configure backups

## Support Resources

- **Full Documentation**: [DOCKER.md](./DOCKER.md)
- **Deployment Guide**: [DEPLOYMENT.md](./DEPLOYMENT.md)
- **View Logs**: `make logs`
- **Check Status**: `make ps`
- **Health Check**: `make health`

---

**Need Help?** Check the full documentation in DOCKER.md
