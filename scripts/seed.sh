#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
cd "$PROJECT_DIR"

echo '🍁 Seeding demo data...'

POD=$(kubectl get pod -l app=backend -o jsonpath='{.items[0].metadata.name}')

if [ -z "$POD" ]; then
    echo '❌ Backend pod not found. Is the cluster running?'
    exit 1
fi

echo '📝 Clearing existing products...'
kubectl exec "$POD" -- python manage.py shell -c "from shop.models import Product; Product.objects.all().delete(); print('Deleted all products')" || true

echo '📝 Seeding demo data...'
kubectl exec "$POD" -- python manage.py seed_demo

echo '✅ Demo data seeded!'
echo ''
echo 'Demo user: demo_user / demo1234'
