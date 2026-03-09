# Deployment & Monitoring Automation

This guide covers automated deployment and monitoring for the Maple Syrup Store.

## Quick Reference

```bash
# Deploy frontend updates (fast, ephemeral)
./scripts/deploy-frontend-remote.sh

# Full rebuild with persistent changes
./scripts/rebuild-remote.sh

# Watch frontend and auto-deploy on changes
./scripts/watch-frontend.sh

# Check pod health once
./scripts/monitor-pods.sh --once

# Setup continuous monitoring
./scripts/setup-monitoring.sh
systemctl --user start maple-syrup-monitor
```

---

## Frontend Deployment

### Quick Deployment (Recommended for Development)

**What it does:**
- Builds React frontend locally
- Syncs assets directly to running pod
- **Fast** (~10 seconds)
- **Ephemeral** (changes lost on pod restart)

**Usage:**
```bash
./scripts/deploy-frontend-remote.sh
```

**When to use:**
- Development/testing CSS, JavaScript, or React component changes
- Quick iterations without image rebuilds
- No changes to Dockerfile or dependencies

**Example Output:**
```
🍁 Deploying Frontend to Remote Cluster (Quick Sync)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Building React frontend...
🔍 Finding frontend pod...
   Pod: maple-syrup-frontend-fbff44c75-hj7lt
📤 Syncing assets to pod...
✅ Verifying deployment...
   Bundle: main.372ba56e.js

✅ Frontend deployed successfully!
```

---

### Full Rebuild (Production Deployments)

**What it does:**
- Builds Docker images from scratch
- Transfers images to remote host
- Upgrades Helm release
- Recreates pods with new images
- **Slower** (~5 minutes)
- **Persistent** (survives pod restarts)

**Usage:**
```bash
./scripts/rebuild-remote.sh
```

**When to use:**
- Production deployments
- Changes to Dockerfile or nginx config
- npm dependency updates
- Creating a new release

**Prerequisites:**
- SSH access to remote host (`borg@10.0.0.140`)
- Docker installed locally
- Helm installed

**Example Output:**
```
🍁 Rebuilding Maple Syrup Store on Remote Cluster
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Building Docker images...
   Building backend...
   Building frontend...
   Building PDF service...
📤 Transferring images to remote host...
🚀 Upgrading Helm release...
⏳ Waiting for pod rollout...
✅ Remote rebuild complete!
```

---

### Live Development Mode

**What it does:**
- Watches `frontend/src/` for file changes
- Auto-deploys on save (debounced 2 seconds)
- Shows deployment status in terminal

**Usage:**
```bash
./scripts/watch-frontend.sh
```

**Prerequisites:**
- Install `inotify-tools`: `sudo pacman -S inotify-tools`

**Example Output:**
```
🍁 Watching Frontend for Changes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Directory: /home/borg/.../frontend/src
   Press Ctrl+C to stop

📝 Change detected: /home/.../Navbar.js
🚀 Deploying...
✅ Deployed at 14:23:45
👀 Watching for changes...
```

---

## Pod Monitoring & Alerting

### One-Time Health Check

Check current pod status without starting continuous monitoring:

```bash
./scripts/monitor-pods.sh --once
```

**Output:**
```
[2026-03-08 21:47:35] Running single health check...
[2026-03-08 21:47:36] ✅ All pods healthy (backend: 1, frontend: 1)
```

---

### Continuous Monitoring with Systemd

**Setup monitoring as a background service:**

```bash
# 1. Install and enable the service
./scripts/setup-monitoring.sh

# 2. Start monitoring
systemctl --user start maple-syrup-monitor

# 3. Check status
systemctl --user status maple-syrup-monitor

# 4. View live logs
journalctl --user -u maple-syrup-monitor -f
```

**What it monitors:**
- ✅ Cluster connectivity
- ✅ Pod status (Running/Ready)
- ✅ Restart counts (alerts if >5)
- ✅ Expected pod counts (backend, frontend)
- ✅ Container health

**Check interval:** 60 seconds (configurable)

---

### Alert Configuration

Monitoring supports multiple notification channels:

#### 1. Discord/Slack Webhooks

Edit the systemd service file:
```bash
nano ~/.config/systemd/user/maple-syrup-monitor.service
```

Add webhook URL:
```ini
Environment="WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN"
```

Reload and restart:
```bash
systemctl --user daemon-reload
systemctl --user restart maple-syrup-monitor
```

#### 2. Email Alerts (Critical Only)

Add admin email:
```ini
Environment="ADMIN_EMAIL=your-email@example.com"
```

**Requires:** `mailutils` or similar mail client installed

#### 3. Custom Notification Handlers

Edit `scripts/monitor-pods.sh` and modify the `send_notification()` function to add your own handlers (PagerDuty, Twilio, etc.).

---

### Alert Severity Levels

| Level | Color | Trigger | Example |
|-------|-------|---------|---------|
| **info** | 🔵 Blue | Monitor start/stop | "Monitor Started" |
| **warning** | 🟡 Yellow | Non-critical issues | Pod restarted 6 times |
| **critical** | 🔴 Red | Service down | Pod not running, cluster unreachable |

---

## Environment Variables

All scripts support these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `KUBECONFIG` | `~/.kube/k3s-remote` | Path to k3s kubeconfig |
| `NAMESPACE` | `default` | Kubernetes namespace |
| `REMOTE_HOST` | `10.0.0.140` | Remote cluster IP |
| `CHECK_INTERVAL` | `60` | Monitoring interval (seconds) |
| `WEBHOOK_URL` | _(empty)_ | Discord/Slack webhook |
| `ADMIN_EMAIL` | _(empty)_ | Email for critical alerts |

**Example usage:**
```bash
KUBECONFIG=/path/to/config ./scripts/monitor-pods.sh --once
CHECK_INTERVAL=30 ./scripts/monitor-pods.sh
```

---

## Troubleshooting

### Deployment Fails: "No frontend pod found"

**Cause:** Frontend pod is not running or has wrong label.

**Fix:**
```bash
# Check pods
KUBECONFIG=~/.kube/k3s-remote kubectl get pods -n default -l app=frontend

# If missing, redeploy Helm chart
./scripts/rebuild-remote.sh
```

### Monitor Reports "Cluster Unreachable"

**Cause:** Cannot connect to remote k3s cluster.

**Fix:**
```bash
# Test connectivity
KUBECONFIG=~/.kube/k3s-remote kubectl cluster-info

# Check SSH access
ssh borg@10.0.0.140 "sudo k3s kubectl get nodes"

# Verify kubeconfig
cat ~/.kube/k3s-remote | grep server
```

### Watch Script: "inotifywait not found"

**Cause:** `inotify-tools` not installed.

**Fix:**
```bash
sudo pacman -S inotify-tools
```

### Systemd Service Won't Start

**Check logs:**
```bash
journalctl --user -u maple-syrup-monitor -n 50
```

**Common issues:**
- Wrong file paths in service file
- Missing KUBECONFIG
- Permission denied (ensure script is executable)

**Fix:**
```bash
# Verify paths
cat ~/.config/systemd/user/maple-syrup-monitor.service

# Reload and try again
systemctl --user daemon-reload
systemctl --user restart maple-syrup-monitor
```

---

## Best Practices

### For Development
1. Use `./scripts/deploy-frontend-remote.sh` for quick CSS/JS changes
2. Enable `watch-frontend.sh` for live reload during active development
3. Test locally with `npm start` before deploying

### For Production
1. Always use `./scripts/rebuild-remote.sh` for production changes
2. Test in a staging environment first (if available)
3. Keep Helm version tags or git commits for rollback capability

### For Monitoring
1. Configure Discord/Slack webhooks for team visibility
2. Set `CHECK_INTERVAL` based on criticality (30-60s recommended)
3. Enable email alerts for critical issues
4. Review logs regularly: `journalctl --user -u maple-syrup-monitor --since "1 day ago"`

---

## Reference: Script Summary

| Script | Speed | Persistence | Use Case |
|--------|-------|-------------|----------|
| `deploy-frontend-remote.sh` | ⚡ Fast | ❌ Ephemeral | Dev iterations |
| `rebuild-remote.sh` | 🐢 Slow | ✅ Persistent | Production releases |
| `watch-frontend.sh` | ⚡ Auto | ❌ Ephemeral | Live development |
| `monitor-pods.sh --once` | ⚡ Instant | N/A | Manual health check |
| `monitor-pods.sh` (service) | 🔁 Continuous | N/A | 24/7 monitoring |

---

## Next Steps

1. ✅ Test quick deployment: `./scripts/deploy-frontend-remote.sh`
2. ✅ Setup monitoring: `./scripts/setup-monitoring.sh`
3. ✅ Start monitoring service: `systemctl --user start maple-syrup-monitor`
4. 🔧 Configure webhook URL for notifications
5. 📊 Monitor logs: `journalctl --user -u maple-syrup-monitor -f`
