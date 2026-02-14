# Helm Refactoring Complete ✅

## What Changed

The deployment system has been refactored to use **Helm** for better configuration management and secrets handling.

### Before
- Scripts directly applied raw Kubernetes manifests from `k8s/` directory
- Secrets and configuration were hardcoded in YAML files
- No separation between configuration and secrets

### After
- Scripts now use `helm install` / `helm upgrade` with Helm chart
- Secrets are managed separately in `helm-chart/secrets.yaml` (gitignored)
- Values are in `helm-chart/values.yaml` for easy configuration
- Better templating and reusability

## File Structure

```
helm-chart/
├── Chart.yaml              # Helm chart metadata
├── values.yaml             # Default configuration values
├── secrets.yaml            # SECRET CREDENTIALS (gitignored)
├── secrets.yaml.example    # Template for secrets
└── templates/
    ├── _helpers.tpl        # Helm template helpers
    ├── backend.yaml        # Backend deployment + service
    ├── frontend.yaml       # Frontend deployment + service
    └── postgres.yaml       # Database deployment + service + PVC
```

## Scripts Updated

All scripts now use Helm instead of kubectl apply:

| Script | Changes |
|--------|---------|
| `start.sh` | Now checks for secrets.yaml, uses `helm install` |
| `stop.sh` | Uses `helm uninstall` instead of kubectl delete |
| `rebuild.sh` | Uses `helm upgrade` for new images |
| `status.sh` | Added `helm list` to show release status |
| `seed.sh` | No changes (still uses kubectl exec) |
| `restart.sh` | Still uses kubectl rollout |

## Secrets Management

### Initial Setup
1. Copy example file:
   ```bash
   cp helm-chart/secrets.yaml.example helm-chart/secrets.yaml
   ```

2. Edit and set real values:
   ```bash
   nano helm-chart/secrets.yaml
   ```

3. Update these fields:
   - `backend.env.DB_PASSWORD` - PostgreSQL password
   - `backend.env.SECRET_KEY` - Django secret key
   - `postgres.env.POSTGRES_PASSWORD` - Database password
   - `django.superuser.password` - Admin password

### Git Protection
- `helm-chart/secrets.yaml` is in `.gitignore`
- Only `helm-chart/secrets.yaml.example` is committed
- Safe for committing to repositories

## Configuration Hierarchy

Values are merged in this order (last wins):
1. `helm-chart/values.yaml` (defaults)
2. `helm-chart/secrets.yaml` (overrides)

Example:
```bash
helm install maple-syrup ./helm-chart \
  -f helm-chart/values.yaml \
  -f helm-chart/secrets.yaml
```

## Updated Environment Variables

### Backend
All environment variables are now passed from Helm values:
- Regular configs in `backend.env`
- Sensitive values in `backend.secrets`

### PostgreSQL
- Regular configs in `postgres.env`
- Password in `postgres.secrets.POSTGRES_PASSWORD`

## Testing

Verify templates render correctly:
```bash
helm template maple-syrup ./helm-chart \
  -f helm-chart/values.yaml \
  -f helm-chart/secrets.yaml
```

List rendered resources:
```bash
helm template maple-syrup ./helm-chart \
  -f helm-chart/values.yaml \
  -f helm-chart/secrets.yaml | kubectl apply --dry-run=client -f -
```

## Benefits

✅ **Better Security** - Secrets separated and gitignored  
✅ **Better Reusability** - Easy to deploy to different environments  
✅ **Better Maintainability** - Single source of truth for configuration  
✅ **Production Ready** - Standard Kubernetes deployment pattern  
✅ **Easy Rollbacks** - `helm rollback maple-syrup` to previous version  
✅ **Version Control** - Release history tracked by Helm  

## Quick Start

```bash
# One-time setup
cp helm-chart/secrets.yaml.example helm-chart/secrets.yaml
# Edit helm-chart/secrets.yaml with your values

# Deploy
./scripts/start.sh

# Check status
./scripts/status.sh

# Update secrets and redeploy
helm upgrade maple-syrup ./helm-chart \
  -f helm-chart/values.yaml \
  -f helm-chart/secrets.yaml

# Rollback if needed
helm rollback maple-syrup
```

## Next Steps

- Update Dockerfile tags if pushing to registry
- Configure ingress in values.yaml for production
- Add resource limits for production workloads
- Set up automated backups for PostgreSQL
- Consider using Sealed Secrets or External Secrets for production
