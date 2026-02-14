#!/bin/bash

echo '🍁 Maple Syrup Store Status'
echo ''

echo '� Helm Release:'
helm list | grep maple-syrup || echo '  No release found'

echo ''
echo '�📊 Deployments:'
kubectl get deployments

echo ''
echo '📦 Pods:'
kubectl get pods

echo ''
echo '🔗 Services:'
kubectl get svc

echo ''
echo 'Port forwards:'
ps aux | grep 'kubectl port-forward' | grep -v grep || echo '  None running'

echo ''
echo '🌐 Access URLs:'
echo '  Frontend:  http://localhost:8081'
echo '  Admin:     http://localhost:8000/admin'
echo '  Backend:   http://localhost:8000/graphql'
echo '  Dashboard: https://localhost:8443'
