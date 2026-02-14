#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
cd "$PROJECT_DIR"

echo '🛑 Stopping Maple Syrup Store...'

# Kill port-forwards
echo '🔗 Stopping port-forwards...'
pkill -f 'kubectl port-forward' || true

# Uninstall Helm release
echo '🗑️  Removing Helm release...'
helm uninstall maple-syrup --ignore-not-found || true

# Delete dashboard namespace
echo '🔧 Removing Kubernetes Dashboard...'
kubectl delete namespace kubernetes-dashboard --ignore-not-found=true

echo '✅ Stopped successfully'
