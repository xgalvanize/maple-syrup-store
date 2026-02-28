#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
cd "$PROJECT_DIR"

echo '🍁 Starting Maple Syrup Store...'

# Check for secrets file
if [ ! -f helm-chart/secrets.yaml ]; then
    echo '⚠️  No helm-chart/secrets.yaml found!'
    echo 'Copy helm-chart/secrets.yaml.example to helm-chart/secrets.yaml'
    echo 'and update the values with your actual secrets.'
    exit 1
fi

# Check if images exist in kind cluster
echo '🔍 Checking for images...'
if ! docker image inspect maple-syrup-backend:latest >/dev/null 2>&1; then
    echo '⚠️  Images not found! Please run ./scripts/rebuild.sh first to build images.'
    exit 1
fi

# Clean up legacy manifests (pre-Helm)
echo '🧹 Cleaning legacy resources (if any)...'
kubectl delete -f k8s/ --ignore-not-found=true

# Deploy with Helm
echo '🚀 Deploying with Helm...'
helm upgrade --install maple-syrup ./helm-chart \
  -f helm-chart/values.yaml \
  -f helm-chart/secrets.yaml \
  --wait \
  --timeout 5m

# Wait for rollout
echo '⏳ Waiting for deployments...'
kubectl rollout status deployment -l app=backend -n default
kubectl rollout status deployment -l app=frontend -n default
kubectl rollout status deployment -l app=pdf-service -n default
kubectl rollout status deployment -l app=postgres -n default

# Install dashboard
echo '📊 Installing Kubernetes Dashboard...'
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Create service account
echo '🔑 Creating dashboard access token...'
kubectl apply -f - <<'EOFTOKEN'
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kubernetes-dashboard
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
EOFTOKEN

# Wait for dashboard
sleep 5
echo '⏳ Waiting for dashboard...'
kubectl rollout status deployment/kubernetes-dashboard -n kubernetes-dashboard || true

# Start port-forwards
echo '🔗 Starting port-forwards...'
(kubectl port-forward service/frontend 8081:80 > /dev/null 2>&1 &)
(kubectl port-forward service/backend 8000:8000 > /dev/null 2>&1 &)
(kubectl port-forward -n kubernetes-dashboard service/kubernetes-dashboard 8443:443 > /dev/null 2>&1 &)

echo ''
echo '✅ Maple Syrup Store is running!'
echo ''
echo '🌐 Frontend: http://localhost:8081'
echo '🔧 Admin: http://localhost:8000/admin'
echo '💾 Backend GraphQL: http://localhost:8000/graphql'
echo '📊 Dashboard: https://localhost:8443'
echo ''
echo 'Demo login: farmer / (password from setup)'
echo ''

./scripts/dashboard-token.sh
