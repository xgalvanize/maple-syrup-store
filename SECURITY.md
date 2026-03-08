# Security Hardening Guide

This document outlines the security measures implemented in the Maple Syrup Store and best practices for maintaining security in production.

## 🔒 Security Features Implemented

### 1. Django Security Settings

#### HTTPS/SSL Configuration
- `SECURE_SSL_REDIRECT`: Redirects all HTTP requests to HTTPS (enabled in production)
- `SECURE_PROXY_SSL_HEADER`: Properly handles SSL termination behind a proxy
- `SESSION_COOKIE_SECURE`: Ensures session cookies are only sent over HTTPS (production)
- `CSRF_COOKIE_SECURE`: Ensures CSRF cookies are only sent over HTTPS (production)

#### HTTP Strict Transport Security (HSTS)
- `SECURE_HSTS_SECONDS`: Set to 1 year (31536000 seconds) in production
- `SECURE_HSTS_INCLUDE_SUBDOMAINS`: Applies HSTS to all subdomains
- `SECURE_HSTS_PRELOAD`: Allows inclusion in browser HSTS preload lists

#### Content Security and Browser Protection
- `SECURE_CONTENT_TYPE_NOSNIFF`: Prevents MIME type sniffing
- `SECURE_BROWSER_XSS_FILTER`: Enables browser XSS filtering
- `X_FRAME_OPTIONS`: Set to "DENY" to prevent clickjacking attacks

#### Session Security
- `SESSION_COOKIE_HTTPONLY`: Prevents JavaScript access to session cookies
- `SESSION_COOKIE_SAMESITE`: Set to "Lax" to prevent CSRF attacks
- `SESSION_COOKIE_AGE`: Sessions expire after 24 hours
- Sessions use secure backend storage

#### CSRF Protection
- CSRF tokens required for all state-changing operations
- `CSRF_COOKIE_HTTPONLY`: Prevents JavaScript access (where possible)
- `CSRF_COOKIE_SAMESITE`: Set to "Lax" for CSRF prevention
- `CSRF_TRUSTED_ORIGINS`: Whitelist of allowed origins

### 2. Rate Limiting

Rate limiting is implemented at multiple levels:

#### GraphQL API
- **Anonymous users**: 100 requests per minute per IP
- **Authenticated users**: 300 requests per minute per user
- Returns HTTP 429 (Too Many Requests) when limit exceeded

#### Health Check Endpoint
- 10 requests per hour per IP

#### Configuration
Rate limiting can be toggled via `RATELIMIT_ENABLE` environment variable.

### 3. Content Security Policy (CSP)

Strict CSP headers are applied to all responses:

```
default-src 'self'
script-src 'self' 'unsafe-inline'  # unsafe-inline needed for GraphiQL
style-src 'self' 'unsafe-inline'
img-src 'self' data: https:
font-src 'self' data:
connect-src 'self'
frame-ancestors 'none'
```

### 4. Additional Security Headers

Custom middleware adds:
- **Permissions-Policy**: Restricts browser features (geolocation, camera, microphone, etc.)
- **Referrer-Policy**: Set to "strict-origin-when-cross-origin" for privacy
- **X-Content-Type-Options**: Prevents MIME sniffing

### 5. CORS Configuration

Cross-Origin Resource Sharing (CORS) is configured to only allow requests from:
- Configurable via `CORS_ALLOWED_ORIGINS` environment variable
- Default: localhost:3000, localhost:8081

### 6. Kubernetes Security

#### Network Policies
Network policies enforce strict pod-to-pod communication:

- **Backend**: Can communicate with PostgreSQL and PDF service
- **Frontend**: Can only communicate with backend
- **PostgreSQL**: Only accepts connections from backend
- **PDF Service**: Only accepts connections from backend

All pods can access DNS. Backend can make outbound HTTPS for email.

#### Pod Security Contexts
All pods run with hardened security settings:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: false  # Django needs to write logs
  capabilities:
    drop:
    - ALL
  seccompProfile:
    type: RuntimeDefault
```

#### Health Checks
- **Liveness probes**: Restart unhealthy containers
- **Readiness probes**: Remove unhealthy pods from service

### 7. Password Security

Django's built-in password validation enforces:
- Minimum length requirements
- Password can't be too similar to user information
- Password can't be a commonly used password
- Password can't be entirely numeric

Passwords are hashed using PBKDF2 with SHA256.

### 8. Health Monitoring

Health check endpoints at:
- `/health/`: Comprehensive health checks (DB, cache, storage)
- `/api/health/`: Simple health check (rate limited)

### 9. Logging

Security events are logged to:
- Console (stdout/stderr)
- File: `backend/logs/security.log` (rotated at 10MB, 5 backups)

Logged events include:
- Rate limit violations
- Authentication failures
- Permission denials
- CSRF failures

## 🚀 Production Deployment Checklist

### Before Going Live

- [ ] **Generate strong SECRET_KEY**
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

- [ ] **Set DEBUG to false**
  ```yaml
  backend:
    env:
      DEBUG: "false"
  ```

- [ ] **Enable HTTPS/SSL**
  ```yaml
  backend:
    env:
      SECURE_SSL_REDIRECT: "true"
      SESSION_COOKIE_SECURE: "true"
      CSRF_COOKIE_SECURE: "true"
      SECURE_HSTS_SECONDS: "31536000"
  ```

- [ ] **Configure proper ALLOWED_HOSTS**
  ```yaml
  backend:
    env:
      ALLOWED_HOSTS: "yourdomain.com,www.yourdomain.com"
  ```

- [ ] **Configure CORS_ALLOWED_ORIGINS**
  ```yaml
  backend:
    env:
      CORS_ALLOWED_ORIGINS: "https://yourdomain.com"
  ```

- [ ] **Install SSL/TLS certificates**
  - Use cert-manager with Let's Encrypt for automatic certificates
  - Or manually configure certificates in Kubernetes

- [ ] **Review and update rate limits** if needed

- [ ] **Enable network policies**
  ```yaml
  networkPolicy:
    enabled: true
  ```

- [ ] **Enable pod security contexts**
  ```yaml
  securityContext:
    enabled: true
  ```

- [ ] **Set up monitoring and alerting**
  - Prometheus + Grafana
  - Alert on rate limit violations
  - Alert on failed authentication attempts
  - Alert on health check failures

- [ ] **Configure backup strategy**
  - Automated PostgreSQL backups
  - Test restore procedures

- [ ] **Review all secrets**
  - Use strong passwords (20+ characters)
  - Consider using external secret management (Vault, AWS Secrets Manager)
  - Rotate secrets regularly

## 🔍 Security Testing

### Run Security Tests

```bash
cd backend
pytest -v -k security
```

### Manual Security Testing

1. **Test rate limiting**:
   ```bash
   # Should return 429 after hitting limit
   for i in {1..150}; do curl http://localhost:8000/graphql/; done
   ```

2. **Test HTTPS redirect** (production):
   ```bash
   curl -I http://yourdomain.com
   # Should return 301/302 redirect to https://
   ```

3. **Verify security headers**:
   ```bash
   curl -I https://yourdomain.com
   # Should see X-Frame-Options, CSP, HSTS, etc.
   ```

4. **Test network policies**:
   ```bash
   # Try to access postgres directly (should fail)
   kubectl run test-pod --rm -it --image=postgres:16 -- psql -h postgres -U maple_user
   ```

## 🛡️ Ongoing Security Practices

### Regular Updates
- Keep Django and all dependencies updated
- Monitor security advisories for Django and Python packages
- Run `pip list --outdated` regularly

### Security Monitoring
- Review security logs daily: `backend/logs/security.log`
- Monitor rate limit violations
- Track failed authentication attempts
- Set up alerts for suspicious activity

### Incident Response
1. **If breach suspected**:
   - Immediately rotate all secrets (DB passwords, Django SECRET_KEY, JWT secrets)
   - Review logs for unauthorized access
   - Invalidate all user sessions
   - Notify affected users if data was compromised

2. **After incident**:
   - Document what happened
   - Update security measures
   - Review and test incident response plan

### Secrets Rotation
Rotate credentials regularly:
- Database passwords: Every 90 days
- Django SECRET_KEY: Every 180 days
- Email credentials: When team members leave

### Code Security
- Run security linters: `bandit -r backend/`
- Review all GraphQL resolvers for authorization checks
- Ensure all mutations require authentication where appropriate
- Validate and sanitize all user inputs

## 📚 Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [Django Security Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

## 🔧 Configuration Reference

### Environment Variables

| Variable | Default | Production | Description |
|----------|---------|------------|-------------|
| `DEBUG` | true | **false** | Django debug mode |
| `SECURE_SSL_REDIRECT` | false | **true** | Force HTTPS |
| `SESSION_COOKIE_SECURE` | false | **true** | HTTPS-only session cookies |
| `CSRF_COOKIE_SECURE` | false | **true** | HTTPS-only CSRF cookies |
| `SECURE_HSTS_SECONDS` | 0 | **31536000** | HSTS max-age |
| `RATELIMIT_ENABLE` | true | **true** | Enable rate limiting |
| `ALLOWED_HOSTS` | localhost | **yourdomain.com** | Allowed hostnames |
| `CORS_ALLOWED_ORIGINS` | localhost:3000 | **https://yourdomain.com** | CORS whitelist |

### Disabling Security Features (Development Only)

For local development, you may need to disable some features:

```yaml
# helm-chart/values.yaml (development)
backend:
  env:
    DEBUG: "true"
    SECURE_SSL_REDIRECT: "false"
    RATELIMIT_ENABLE: "false"

securityContext:
  enabled: false

networkPolicy:
  enabled: false
```

**⚠️ Never deploy to production with these settings!**

## 📞 Security Contact

For security concerns or to report vulnerabilities, contact:
- Email: security@maplesyrup.co (set your own)
- Create a private security advisory on GitHub

## 📝 Compliance Notes

This implementation provides baseline security for:
- PCI DSS: Not applicable (using email money transfer, not credit cards)
- GDPR: User data is minimized, but you should add:
  - Privacy policy
  - Cookie consent
  - Data export/deletion capabilities
  - Privacy officer contact

Consult with legal counsel for compliance requirements specific to your jurisdiction.
