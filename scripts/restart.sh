#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
cd "$PROJECT_DIR"

echo '🍁 Restarting Maple Syrup Store...'

# Kill existing port-forwards
pkill -f 'kubectl port-forward' || true

# Restart deployments
echo '🔄 Restarting deployments...'
kubectl rollout restart deployment -l app=backend
kubectl rollout restart deployment -l app=frontend
kubectl rollout restart deployment -l app=pdf-service

echo '⏳ Waiting for deployments...'
kubectl rollout status deployment -l app=backend
kubectl rollout status deployment -l app=frontend
kubectl rollout status deployment -l app=pdf-service

# Start port-forwards
echo '🔗 Starting port-forwards...'
(kubectl port-forward service/frontend 8081:80 > /dev/null 2>&1 &)
(kubectl port-forward service/backend 8000:8000 > /dev/null 2>&1 &)
(kubectl port-forward -n kubernetes-dashboard service/kubernetes-dashboard 8443:443 > /dev/null 2>&1 &)

echo ''
echo '✅ Restarted successfully!'
echo ''
echo '🌐 Frontend: http://localhost:8081'
echo '🔧 Admin: http://localhost:8000/admin'
echo '📊 Dashboard: https://localhost:8443'
echo ''
