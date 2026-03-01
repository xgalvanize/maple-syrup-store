#!/bin/bash
set -e

# Simple daily backup script
kubectl exec deployment/maple-syrup-postgres -- \
  pg_dump -U maple_user maple_store | \
  gzip > backup-$(date +%Y%m%d).sql.gz