#!/bin/bash
# Optimized cron configuration - reduces monitoring frequency to save disk space
# This script backs up current crontab and installs optimized version

set -e

BACKUP_DIR="/var/backups/cron"
DATE=$(date +%Y%m%d_%H%M%S)

echo "=== Optimizing Cron Configuration ==="
echo "Timestamp: $(date)"

# Create backup directory
sudo mkdir -p ${BACKUP_DIR}

# Backup current crontab
echo "[1/3] Backing up current crontab..."
sudo crontab -l > ${BACKUP_DIR}/crontab_backup_${DATE} 2>/dev/null || true

# Install optimized crontab
echo "[2/3] Installing optimized crontab..."
sudo crontab - << 'EOF'
# Optimized monitoring schedule - reduced frequency for resource conservation

# System health check: every 15 minutes (was every 5 minutes)
*/15 * * * * /usr/local/bin/system-health-check.sh

# Disk watch: every 6 hours (was every hour)
0 */6 * * * /usr/local/bin/disk-watch.sh

# Security monitor: every 6 hours (was every hour)
0 */6 * * * /usr/local/bin/security-monitor.sh

# Log forwarding to backend: daily at 4 AM
0 4 * * * /usr/local/bin/log-forward.sh

# Aggressive cleanup: daily at 3 AM
0 3 * * * /usr/local/bin/daily-cleanup.sh

# Log rotation: hourly (handled by logrotate)
0 * * * * /usr/sbin/logrotate /etc/logrotate.conf
EOF

# Verify installation
echo "[3/3] Verifying new crontab..."
sudo crontab -l

echo "=== Cron Optimization Complete ==="
echo "Backup saved to: ${BACKUP_DIR}/crontab_backup_${DATE}"
echo "Timestamp: $(date)"
