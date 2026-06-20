#!/bin/bash
# ============================================================
# simple-web-cicd - Cloud Server Deployment Script
# ============================================================
# Usage:
#   ./deploy.sh ghcr.io/username/simple-web-cicd:latest
#
# This script pulls the latest Docker image and (re)starts
# the application container on the cloud server.
# ============================================================

set -euo pipefail

IMAGE="${1:-ghcr.io/your-username/simple-web-cicd:latest}"
CONTAINER_NAME="simple-web-cicd"
HOST_PORT="5000"

echo "=========================================="
echo "  simple-web-cicd Deployment"
echo "=========================================="
echo "[1/5] Pulling image: $IMAGE"
docker pull "$IMAGE"

echo "[2/5] Stopping old container (if running)"
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

echo "[3/5] Starting new container"
docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  -p "$HOST_PORT":5000 \
  "$IMAGE"

echo "[4/5] Waiting for service to start..."
sleep 5

echo "[5/5] Running health check"
if curl -f "http://localhost:$HOST_PORT/health" > /dev/null 2>&1; then
  echo "✅ Health check passed!"
  echo "Container $CONTAINER_NAME is running on port $HOST_PORT"
  docker ps --filter name="$CONTAINER_NAME"
  exit 0
else
  echo "❌ Health check FAILED!"
  echo "Showing container logs for diagnosis:"
  docker logs "$CONTAINER_NAME" --tail 30
  exit 1
fi
