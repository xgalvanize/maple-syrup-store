#!/bin/bash
#
# Full rebuild and deployment to remote k3s cluster at 10.0.0.140
# Builds Docker images, pushes to remote, upgrades Helm release
# Changes persist across pod restarts
#
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
cd "$PROJECT_DIR"

KUBECONFIG="${KUBECONFIG:-$HOME/.kube/k3s-remote}"
REMOTE_HOST="${REMOTE_HOST:-10.0.0.140}"
NAMESPACE="${NAMESPACE:-default}"

if [ ! -f "$KUBECONFIG" ]; then
    echo "❌ Kubeconfig not found at: $KUBECONFIG"
    exit 1
fi

echo "🍁 Rebuilding Maple Syrup Store on Remote Cluster"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Build images
echo "📦 Building Docker images..."

echo "   Building backend..."
docker build -q -t maple-syrup-backend:latest "$PROJECT_DIR/backend"

echo "   Building frontend..."
docker build -q -t maple-syrup-frontend:latest "$PROJECT_DIR/frontend"

echo "   Building PDF service..."
docker build -q -t maple-syrup-pdf-service:latest "$PROJECT_DIR/pdf-service"

# Save and transfer images to remote host
echo ""
echo "📤 Transferring images to remote host..."

IMAGE_TAR="/tmp/maple-syrup-images-$(date +%s).tar"
echo "   Saving images to: $IMAGE_TAR"
docker save \
    maple-syrup-backend:latest \
    maple-syrup-frontend:latest \
    maple-syrup-pdf-service:latest \
    -o "$IMAGE_TAR"

echo "   Transferring to $REMOTE_HOST..."
scp -q "$IMAGE_TAR" "borg@$REMOTE_HOST:/tmp/"

echo "   Loading images into remote k3s..."
ssh "borg@$REMOTE_HOST" "sudo k3s ctr images import /tmp/$(basename $IMAGE_TAR) && rm /tmp/$(basename $IMAGE_TAR)"

rm "$IMAGE_TAR"

# Upgrade Helm release
echo ""
echo "🚀 Upgrading Helm release..."
KUBECONFIG="$KUBECONFIG" helm upgrade maple-syrup "$PROJECT_DIR/helm-chart" \
    -f "$PROJECT_DIR/helm-chart/values.yaml" \
    -f "$PROJECT_DIR/helm-chart/values.remote-unified.yaml" \
    -f "$PROJECT_DIR/helm-chart/secrets.yaml" \
    --wait \
    --timeout 5m

# Wait for rollout
echo ""
echo "⏳ Waiting for pod rollout..."
KUBECONFIG="$KUBECONFIG" kubectl rollout status deployment/maple-syrup-backend -n "$NAMESPACE" --timeout=3m
KUBECONFIG="$KUBECONFIG" kubectl rollout status deployment/maple-syrup-frontend -n "$NAMESPACE" --timeout=3m

echo ""
echo "✅ Remote rebuild complete!"
echo ""
echo "📊 Pod Status:"
KUBECONFIG="$KUBECONFIG" kubectl get pods -n "$NAMESPACE" -l 'app in (backend,frontend,pdf-service)'

echo ""
echo "📱 Frontend: http://$REMOTE_HOST:30081"
