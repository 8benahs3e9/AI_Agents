#!/bin/bash
# Log forwarding script - sends logs to backend server (skype)
# Requires SSH key authentication to backend

set -e

BACKEND_HOST="10.128.0.6"
BACKEND_USER="user"  # Change this to actual backend username
BACKEND_LOG_DIR="/var/log/archive"
DATE=$(date +%Y%m%d)
TEMP_DIR="/tmp"

echo "=== Log Forwarding Started ==="
echo "Timestamp: $(date)"

# Create archive directory on backend if it doesn't exist
echo "[1/4] Creating archive directory on backend..."
ssh ${BACKEND_USER}@${BACKEND_HOST} "sudo mkdir -p ${BACKEND_LOG_DIR}"

# Compress logs
echo "[2/4] Compressing logs..."
tar -czf ${TEMP_DIR}/logs-${DATE}.tar.gz \
    /var/log/system-health.log \
    /var/log/security-monitor.log \
    /var/log/gateway-health-monitor.log \
    /var/log/disk-warning.log 2>/dev/null || true

# Send to backend
echo "[3/4] Sending logs to backend..."
scp ${TEMP_DIR}/logs-${DATE}.tar.gz ${BACKEND_USER}@${BACKEND_HOST}:${TEMP_DIR}/
ssh ${BACKEND_USER}@${BACKEND_HOST} "sudo mv ${TEMP_DIR}/logs-${DATE}.tar.gz ${BACKEND_LOG_DIR}/"

# Clear local logs after successful transfer
echo "[4/4] Clearing local logs..."
truncate -s 0 /var/log/system-health.log 2>/dev/null || true
truncate -s 0 /var/log/security-monitor.log 2>/dev/null || true
truncate -s 0 /var/log/gateway-health-monitor.log 2>/dev/null || true
truncate -s 0 /var/log/disk-warning.log 2>/dev/null || true

# Cleanup temp file
rm -f ${TEMP_DIR}/logs-${DATE}.tar.gz

echo "=== Log Forwarding Complete ==="
echo "Timestamp: $(date)"
