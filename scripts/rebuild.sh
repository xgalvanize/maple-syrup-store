#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
cd "$PROJECT_DIR"

echo '🍁 Building and pushing new images...'

# Build images
echo '📦 Building backend...'
docker build -q -t maple-syrup-backend:latest backend

echo '📦 Building frontend...'
docker build -q -t maple-syrup-frontend:latest frontend

# Load into kind
echo '📤 Loading images into cluster...'
kind load docker-image --name atlas maple-syrup-backend:latest maple-syrup-frontend:latest

# Upgrade Helm release
echo '🚀 Upgrading Helm release...'
if helm list | grep -q maple-syrup; then
    helm upgrade maple-syrup ./helm-chart \
      -f helm-chart/values.yaml \
      -f helm-chart/secrets.yaml \
      --wait
else
    echo 'Release not found. Run ./scripts/start.sh first'
    exit 1
fi

echo '⏳ Waiting for deployments...'
kubectl rollout status deployment -l app=backend
kubectl rollout status deployment -l app=frontend

echo '✅ Rebuild complete!'
