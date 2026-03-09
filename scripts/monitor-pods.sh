#!/bin/bash
#
# Monitor Kubernetes pods and send alerts on failures
# Can be run as a systemd service for continuous monitoring
#
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
cd "$PROJECT_DIR"

KUBECONFIG="${KUBECONFIG:-$HOME/.kube/k3s-remote}"
NAMESPACE="${NAMESPACE:-default}"
CHECK_INTERVAL="${CHECK_INTERVAL:-60}"  # seconds
STATE_FILE="/tmp/k8s-monitor-state.json"

# Notification settings
WEBHOOK_URL="${WEBHOOK_URL:-}"  # Set to Discord/Slack webhook URL if desired
ADMIN_EMAIL="${ADMIN_EMAIL:-}"  # Email for critical alerts

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

send_notification() {
    local title="$1"
    local message="$2"
    local severity="$3"  # info, warning, critical
    
    log "$severity: $title - $message"
    
    # Send webhook if configured
    if [ -n "$WEBHOOK_URL" ]; then
        local color="3447003"  # blue
        [ "$severity" = "warning" ] && color="16776960"  # yellow
        [ "$severity" = "critical" ] && color="15158332"  # red
        
        curl -s -X POST "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d @- > /dev/null 2>&1 << EOF
{
    "embeds": [{
        "title": "🍁 $title",
        "description": "$message",
        "color": $color,
        "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%S.000Z)"
    }]
}
EOF
    fi
    
    # Send email for critical alerts
    if [ "$severity" = "critical" ] && [ -n "$ADMIN_EMAIL" ]; then
        if command -v mail &> /dev/null; then
            echo "$message" | mail -s "🚨 Maple Syrup Store Alert: $title" "$ADMIN_EMAIL"
        fi
    fi
}

check_pod_health() {
    local pod_name="$1"
    local app_label="$2"
    
    # Get pod status
    local status=$(KUBECONFIG="$KUBECONFIG" kubectl get pod "$pod_name" -n "$NAMESPACE" \
        -o jsonpath='{.status.phase}' 2>/dev/null)
    
    local ready=$(KUBECONFIG="$KUBECONFIG" kubectl get pod "$pod_name" -n "$NAMESPACE" \
        -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)
    
    local restarts=$(KUBECONFIG="$KUBECONFIG" kubectl get pod "$pod_name" -n "$NAMESPACE" \
        -o jsonpath='{.status.containerStatuses[0].restartCount}' 2>/dev/null)
    
    # Check for problems
    if [ "$status" != "Running" ] || [ "$ready" != "True" ]; then
        send_notification \
            "Pod $app_label is unhealthy" \
            "Pod: $pod_name\nStatus: $status\nReady: $ready\nRestarts: $restarts" \
            "critical"
        return 1
    fi
    
    # Check for excessive restarts (more than 5)
    if [ "$restarts" -gt 5 ]; then
        send_notification \
            "Pod $app_label restarting frequently" \
            "Pod: $pod_name\nRestart count: $restarts" \
            "warning"
    fi
    
    return 0
}

check_cluster() {
    # Check if cluster is reachable
    if ! KUBECONFIG="$KUBECONFIG" kubectl cluster-info > /dev/null 2>&1; then
        send_notification \
            "Cluster Unreachable" \
            "Cannot connect to k3s cluster at 10.0.0.140" \
            "critical"
        return 1
    fi
    
    # Get all pods we care about
    local pods=$(KUBECONFIG="$KUBECONFIG" kubectl get pods -n "$NAMESPACE" \
        -l 'app in (backend,frontend,postgres,pdf-service)' \
        -o jsonpath='{range .items[*]}{.metadata.name}:{.metadata.labels.app}{"\n"}{end}')
    
    local all_healthy=true
    
    while IFS=: read -r pod_name app_label; do
        if [ -n "$pod_name" ]; then
            if ! check_pod_health "$pod_name" "$app_label"; then
                all_healthy=false
            fi
        fi
    done <<< "$pods"
    
    # Check if any expected pods are missing
    local backend_count=$(KUBECONFIG="$KUBECONFIG" kubectl get pods -n "$NAMESPACE" \
        -l app=backend --field-selector=status.phase=Running | grep -c Running || true)
    local frontend_count=$(KUBECONFIG="$KUBECONFIG" kubectl get pods -n "$NAMESPACE" \
        -l app=frontend --field-selector=status.phase=Running | grep -c Running || true)
    
    if [ "$backend_count" -eq 0 ]; then
        send_notification \
            "No Backend Pods Running" \
            "Expected at least 1 backend pod, found 0" \
            "critical"
        all_healthy=false
    fi
    
    if [ "$frontend_count" -eq 0 ]; then
        send_notification \
            "No Frontend Pods Running" \
            "Expected at least 1 frontend pod, found 0" \
            "critical"
        all_healthy=false
    fi
    
    if $all_healthy; then
        log "✅ All pods healthy (backend: $backend_count, frontend: $frontend_count)"
    fi
}

# Main monitoring loop
if [ "${1:-}" = "--once" ]; then
    log "Running single health check..."
    check_cluster
else
    log "🍁 Starting Kubernetes Pod Monitor"
    log "   Cluster: 10.0.0.140"
    log "   Check interval: ${CHECK_INTERVAL}s"
    log "   Webhook: ${WEBHOOK_URL:-<not configured>}"
    log ""
    
    send_notification \
        "Monitor Started" \
        "Kubernetes pod monitoring is now active" \
        "info"
    
    while true; do
        check_cluster
        sleep "$CHECK_INTERVAL"
    done
fi
