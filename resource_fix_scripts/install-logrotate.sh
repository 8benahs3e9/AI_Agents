#!/bin/bash
# Install strict log rotation configuration
# Aggressive rotation to minimize disk usage

set -e

LOGROTATE_CONF="/etc/logrotate.d/custom-health-logs"

echo "=== Installing Strict Log Rotation ==="
echo "Timestamp: $(date)"

# Create logrotate configuration
echo "[1/2] Creating logrotate configuration..."
sudo tee ${LOGROTATE_CONF} > /dev/null << 'EOF'
# Strict log rotation for custom health monitoring logs
# Aggressive settings to minimize disk usage

/var/log/system-health.log {
    hourly
    rotate 3
    compress
    delaycompress
    missingok
    notifempty
    size 5M
    maxage 1
    create 644 root root
}

/var/log/security-monitor.log {
    hourly
    rotate 3
    compress
    delaycompress
    missingok
    notifempty
    size 2M
    maxage 1
    create 644 root root
}

/var/log/gateway-health-monitor.log {
    hourly
    rotate 3
    compress
    delaycompress
    missingok
    notifempty
    size 5M
    maxage 1
    create 644 root root
}

/var/log/disk-warning.log {
    hourly
    rotate 3
    compress
    delaycompress
    missingok
    notifempty
    size 1M
    maxage 1
    create 644 root root
}
EOF

# Force immediate rotation
echo "[2/2] Forcing immediate log rotation..."
sudo logrotate -f ${LOGROTATE_CONF}

echo "=== Log Rotation Installation Complete ==="
echo "Configuration: ${LOGROTATE_CONF}"
echo "Timestamp: $(date)"
