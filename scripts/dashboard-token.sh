#!/bin/bash

echo '🔑 Kubernetes Dashboard Access Token'
echo ''

TOKEN=$(kubectl -n kubernetes-dashboard create token admin-user 2>/dev/null || echo '')

if [ -z "$TOKEN" ]; then
    echo '⏳ Dashboard not ready yet. Waiting...'
    sleep 10
    TOKEN=$(kubectl -n kubernetes-dashboard create token admin-user 2>/dev/null || echo '')
fi

if [ -z "$TOKEN" ]; then
    echo '❌ Could not generate token. Dashboard may not be running.'
    echo ''
    echo 'Try running: ./scripts/status.sh'
    exit 1
fi

echo 'Copy this token and paste it into the dashboard login:'
echo ''
echo '---BEGIN TOKEN---'
echo "$TOKEN"
echo '---END TOKEN---'
echo ''
echo 'Dashboard URL: https://localhost:8443'
