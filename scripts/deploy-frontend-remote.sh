#!/bin/bash
#
# Deploy frontend updates to remote k3s cluster at 10.0.0.140
# This is a FAST deployment - syncs built assets directly to running pod
# No image rebuild, no Helm upgrade, changes lost on pod restart
#
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
cd "$PROJECT_DIR"

KUBECONFIG="${KUBECONFIG:-$HOME/.kube/k3s-remote}"
NAMESPACE="${NAMESPACE:-default}"

if [ ! -f "$KUBECONFIG" ]; then
    echo "❌ Kubeconfig not found at: $KUBECONFIG"
    echo "   Set KUBECONFIG environment variable or place config at ~/.kube/k3s-remote"
    exit 1
fi

echo "🍁 Deploying Frontend to Remote Cluster (Quick Sync)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Build frontend
echo "📦 Building React frontend..."
cd "$PROJECT_DIR/frontend"
npm run build > /dev/null 2>&1
cd "$PROJECT_DIR"

# Get frontend pod
echo "🔍 Finding frontend pod..."
FRONTEND_POD=$(KUBECONFIG="$KUBECONFIG" kubectl get pods -n "$NAMESPACE" \
    -l app=frontend \
    -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$FRONTEND_POD" ]; then
    echo "❌ No frontend pod found in namespace $NAMESPACE"
    exit 1
fi

echo "   Pod: $FRONTEND_POD"

# Sync assets
echo "📤 Syncing assets to pod..."
KUBECONFIG="$KUBECONFIG" kubectl cp \
    "$PROJECT_DIR/frontend/build/." \
    "$NAMESPACE/$FRONTEND_POD:/usr/share/nginx/html" \
    --no-preserve

# Verify deployment
echo "✅ Verifying deployment..."
BUNDLE_HASH=$(curl -sS http://10.0.0.140:30081 | grep -o 'main\.[a-z0-9]*\.js' | head -1)

if [ -z "$BUNDLE_HASH" ]; then
    echo "⚠️  Could not verify bundle deployment"
else
    echo "   Bundle: $BUNDLE_HASH"
fi

echo ""
echo "✅ Frontend deployed successfully!"
echo ""
echo "⚠️  NOTE: This deployment is ephemeral (lost on pod restart)"
echo "   For persistent changes, use: ./scripts/rebuild-remote.sh"
echo ""
echo "📱 Test at: http://10.0.0.140:30081"
