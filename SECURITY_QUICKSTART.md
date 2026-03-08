# Security Quick Start

This guide helps you quickly enable security features for production deployment.

## 🚀 Quick Setup (5 minutes)

### 1. Install Security Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `django-ratelimit` - API rate limiting
- `django-csp` - Content Security Policy headers
- `django-health-check` - Health check endpoints

### 2. Update Secrets File

Copy and update the secrets template:

```bash
cp helm-chart/secrets.yaml.example helm-chart/secrets.yaml
```

Edit `helm-chart/secrets.yaml` and update:

```yaml
backend:
  secrets:
    SECRET_KEY: "GENERATE_NEW_SECRET_KEY_HERE"
    DB_PASSWORD: "strong_database_password_here"
    EMAIL_HOST_USER: "your-email@gmail.com"
    EMAIL_HOST_PASSWORD: "your-app-password"
  
  env:
    # For production with HTTPS
    SECURE_SSL_REDIRECT: "true"
    SESSION_COOKIE_SECURE: "true"
    CSRF_COOKIE_SECURE: "true"
    SECURE_HSTS_SECONDS: "31536000"
```

**Generate a new SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Configure Domain

Update `helm-chart/values.yaml`:

```yaml
backend:
  env:
    ALLOWED_HOSTS: "yourdomain.com,www.yourdomain.com"
    CORS_ALLOWED_ORIGINS: "https://yourdomain.com"
    DEBUG: "false"
```

### 4. Enable Security Features

In `helm-chart/values.yaml`:

```yaml
securityContext:
  enabled: true

networkPolicy:
  enabled: true
```

### 5. Deploy

```bash
./scripts/start.sh
```

## ✅ Verify Security

### Check Security Headers

```bash
curl -I https://yourdomain.com
```

Look for:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Strict-Transport-Security`
- `Content-Security-Policy`
- `Permissions-Policy`

### Test Rate Limiting

```bash
# Should return 429 after 100 requests
for i in {1..150}; do 
  curl -X POST https://yourdomain.com/graphql/ \
    -H "Content-Type: application/json" \
    -d '{"query": "{ __typename }"}' 
done
```

### Check Health Endpoints

```bash
curl https://yourdomain.com/api/health/
# Should return: {"status": "healthy"}

curl https://yourdomain.com/health/
# Should return health check details
```

### Verify Network Policies

```bash
kubectl get networkpolicies
# Should show policies for backend, frontend, postgres, pdf-service
```

### Test HTTPS Redirect

```bash
curl -I http://yourdomain.com
# Should return 301/302 redirect to https://
```

## 🔐 Production Checklist

Before launching:

- [ ] DEBUG set to "false"
- [ ] Strong SECRET_KEY generated
- [ ] HTTPS enabled with valid SSL certificate
- [ ] ALLOWED_HOSTS configured correctly
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] Network policies enabled
- [ ] Pod security contexts enabled
- [ ] Health checks working
- [ ] Monitoring and alerting set up
- [ ] Backup strategy in place
- [ ] Security logs being collected

## 🆘 Troubleshooting

### Rate limiting not working
- Check `RATELIMIT_ENABLE` is "true"
- Verify cache backend is configured
- Check logs: `kubectl logs -l app=backend`

### HTTPS redirect loop
- Ensure `SECURE_PROXY_SSL_HEADER` is set correctly
- Check load balancer SSL termination
- Verify `X-Forwarded-Proto` header

### Network policy blocking traffic
- Check pod labels match policy selectors
- Verify DNS access is allowed
- Test without network policies first, then enable

### Health checks failing
- Check database connectivity
- Verify all migrations are applied
- Check logs for specific errors

## 📚 Full Documentation

See [SECURITY.md](SECURITY.md) for complete security documentation.

## 🔄 Regular Maintenance

### Monthly
- [ ] Review security logs
- [ ] Check for package updates: `pip list --outdated`
- [ ] Review rate limit metrics
- [ ] Test backup/restore

### Quarterly
- [ ] Rotate database passwords
- [ ] Update Django SECRET_KEY
- [ ] Review and update CORS origins
- [ ] Security audit

### Immediately
- [ ] When team members leave, rotate all shared credentials
- [ ] On security advisory, update affected packages
- [ ] If breach suspected, follow incident response plan
