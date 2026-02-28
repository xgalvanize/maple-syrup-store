#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
cd "$PROJECT_DIR"

echo '🍁 Building Maple Syrup Store images...'

# Build images
echo '📦 Building backend...'
docker build -q -t maple-syrup-backend:latest backend

echo '📦 Building frontend...'
docker build -q -t maple-syrup-frontend:latest frontend

echo '📦 Building PDF service...'
docker build -q -t maple-syrup-pdf-service:latest pdf-service

# Load into kind
echo '📤 Loading images into cluster...'
kind load docker-image --name atlas maple-syrup-backend:latest maple-syrup-frontend:latest maple-syrup-pdf-service:latest

echo '✅ Build complete! Images loaded into cluster.'
echo ''
echo 'Next steps:'
echo '  - First time: ./scripts/start.sh'
echo '  - Updates:    ./scripts/restart.sh'
