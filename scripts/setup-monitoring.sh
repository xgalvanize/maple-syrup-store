#!/bin/bash
#
# Setup monitoring service on local machine to watch remote k3s cluster
#
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
cd "$PROJECT_DIR"

SERVICE_FILE="$PROJECT_DIR/scripts/maple-syrup-monitor.service"
SYSTEMD_DIR="$HOME/.config/systemd/user"

echo "🍁 Setting Up Kubernetes Pod Monitoring"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Make monitor script executable
echo "📝 Making monitor script executable..."
chmod +x "$PROJECT_DIR/scripts/monitor-pods.sh"

# Create systemd user directory
mkdir -p "$SYSTEMD_DIR"

# Copy service file
echo "📋 Installing systemd service..."
cp "$SERVICE_FILE" "$SYSTEMD_DIR/maple-syrup-monitor.service"

# Reload systemd
echo "🔄 Reloading systemd daemon..."
systemctl --user daemon-reload

# Enable service
echo "✅ Enabling service..."
systemctl --user enable maple-syrup-monitor.service

echo ""
echo "✅ Monitoring setup complete!"
echo ""
echo "📊 Service Management:"
echo "   Start:   systemctl --user start maple-syrup-monitor"
echo "   Stop:    systemctl --user stop maple-syrup-monitor"
echo "   Status:  systemctl --user status maple-syrup-monitor"
echo "   Logs:    journalctl --user -u maple-syrup-monitor -f"
echo ""
echo "🔧 Configuration:"
echo "   Edit: $SYSTEMD_DIR/maple-syrup-monitor.service"
echo "   Set WEBHOOK_URL for Discord/Slack notifications"
echo "   Set ADMIN_EMAIL for critical email alerts"
echo "   Then: systemctl --user daemon-reload && systemctl --user restart maple-syrup-monitor"
echo ""
echo "⚠️  To start monitoring now, run:"
echo "   systemctl --user start maple-syrup-monitor"
