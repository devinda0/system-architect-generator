# Manual Docker Build and Push Script

This script allows you to manually build and push Docker images to OCI Container Registry.

## Prerequisites

1. Docker Desktop installed and running
2. OCI CLI configured or OCI credentials ready
3. Access to OCI Container Registry

## Setup

1. Set your OCI credentials:
```bash
export OCI_USERNAME="ax1cmfkxkbut/your-username"
export OCI_AUTH_TOKEN="your-auth-token"
```

Or create a `.env.local` file:
```bash
OCI_USERNAME=ax1cmfkxkbut/your-username
OCI_AUTH_TOKEN=your-auth-token
```

2. Run the script:
```bash
chmod +x .github/scripts/manual-docker-push.sh
./.github/scripts/manual-docker-push.sh
```

## What This Script Does

1. ✅ Verifies Docker is running
2. ✅ Logs in to OCI Container Registry
3. ✅ Builds backend image from `./backend/Dockerfile`
4. ✅ Builds frontend image from `./frontend/Dockerfile`
5. ✅ Tags images with proper OCI paths
6. ✅ Pushes images to OCIR
7. ✅ Displays summary with image URLs

## Image URLs

After successful push:
- **Backend**: `ax1cmfkxkbut.ocir.io/ax1cmfkxkbut/ranga-tech/dev/app-1:latest`
- **Frontend**: `ax1cmfkxkbut.ocir.io/ax1cmfkxkbut/ranga-tech/dev/app-2:latest`

## Troubleshooting

### Docker Not Running
```bash
# Start Docker Desktop and wait for it to be ready
```

### Authentication Failed
```bash
# Verify credentials
echo $OCI_USERNAME
echo $OCI_AUTH_TOKEN

# Try manual login
docker login ax1cmfkxkbut.ocir.io -u "$OCI_USERNAME" -p "$OCI_AUTH_TOKEN"
```

### Build Failed
```bash
# Check Docker logs
docker logs

# Verify Dockerfiles exist
ls -la backend/Dockerfile
ls -la frontend/Dockerfile
```
