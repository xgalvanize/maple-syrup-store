#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
cd "$PROJECT_DIR"

echo '🍁 Rebuilding Maple Syrup Store...'

# Build and load images
./scripts/build.sh

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
kubectl rollout status deployment -l app=pdf-service

echo '✅ Rebuild complete!'
