# Helm Deployment Guide

## Setup

### 1. Configure Secrets

Copy the example secrets file and update with your own values:

```bash
cp helm-chart/secrets.yaml.example helm-chart/secrets.yaml
```

Edit `helm-chart/secrets.yaml` and change:
- `backend.env.DB_PASSWORD` - PostgreSQL password
- `backend.env.SECRET_KEY` - Django secret key (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `postgres.env.POSTGRES_PASSWORD` - PostgreSQL root password
- `django.superuser.password` - Admin user password

**Important:** Never commit `helm-chart/secrets.yaml` to git. It's in `.gitignore`.

### 2. Deploy

```bash
./scripts/start.sh
```

This will:
- Build Docker images
- Load them into the kind cluster
- Deploy via Helm with your secrets
- Install Kubernetes Dashboard
- Start port-forwards to all services
- Display dashboard access token

### 3. Access Services

- **Frontend:** http://localhost:8081
- **Admin:** http://localhost:8000/admin (username: farmer)
- **GraphQL:** http://localhost:8000/graphql
- **Dashboard:** https://localhost:8443

## Managing Deployments

### View Status
```bash
./scripts/status.sh
```

### Rebuild Images
```bash
./scripts/rebuild.sh
```

### Seed Demo Data
```bash
./scripts/seed.sh
```

### Stop Everything
```bash
./scripts/stop.sh
```

## Helm Commands

### View Release
```bash
helm list
helm status maple-syrup
```

### Upgrade with New Secrets
```bash
helm upgrade maple-syrup ./helm-chart \
  -f helm-chart/values.yaml \
  -f helm-chart/secrets.yaml
```

### Rollback
```bash
helm rollback maple-syrup
```

### Get Values
```bash
helm get values maple-syrup
```

## Environment Variables

### Backend (Django)
- `DB_NAME` - Database name (default: maple_store)
- `DB_USER` - Database user (default: maple_user)
- `DB_PASSWORD` - Database password (in secrets.yaml)
- `DB_HOST` - Database host (default: postgres)
- `DB_PORT` - Database port (default: 5432)
- `SECRET_KEY` - Django secret key (in secrets.yaml)
- `ALLOWED_HOSTS` - Comma-separated allowed hosts
- `DEBUG` - Debug mode (in secrets.yaml, set to "false" for production)

### PostgreSQL
- `POSTGRES_DB` - Database name
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password (in secrets.yaml)

## Production Considerations

Before deploying to production:

1. **Change all secrets in `helm-chart/secrets.yaml`**
   - Generate a strong Django SECRET_KEY
   - Use strong database passwords
   - Use strong admin password

2. **Update `helm-chart/values.yaml`**
   - Increase resource limits for backend/frontend
   - Set DEBUG to "false"
   - Update ALLOWED_HOSTS to your domain
   - Configure persistent volume size for database

3. **Use a real container registry**
   - Push images to Docker Hub, ECR, GCR, etc.
   - Update image.repository in values.yaml
   - Change imagePullPolicy to "IfNotPresent" or "Always"

4. **Enable ingress**
   - Set `ingress.enabled: true` in values.yaml
   - Configure your domain
   - Use SSL certificates (cert-manager recommended)

5. **Database backups**
   - Implement PostgreSQL backup strategy
   - Consider managed database services

6. **Monitoring & Logging**
   - Add Prometheus/Grafana for monitoring
   - Configure centralized logging (ELK, Loki, etc.)
   - Set up alerting for critical issues
