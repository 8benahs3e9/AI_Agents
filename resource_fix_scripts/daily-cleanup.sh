#!/bin/bash
# Automated daily cleanup script
# Runs daily at 3 AM via cron

set -e

LOG_FILE="/var/log/daily-cleanup.log"

echo "=== Daily Cleanup Started ===" | tee -a ${LOG_FILE}
echo "Timestamp: $(date)" | tee -a ${LOG_FILE}

# Clean package cache
echo "[1/6] Cleaning package cache..." | tee -a ${LOG_FILE}
apt clean 2>&1 | tee -a ${LOG_FILE}
apt autoclean 2>&1 | tee -a ${LOG_FILE}

# Remove unused packages
echo "[2/6] Removing unused packages..." | tee -a ${LOG_FILE}
apt autoremove -y 2>&1 | tee -a ${LOG_FILE}

# Clean journal logs (keep only 2 days)
echo "[3/6] Cleaning journal logs (keeping 2 days)..." | tee -a ${LOG_FILE}
journalctl --vacuum-time=2d 2>&1 | tee -a ${LOG_FILE}

# Truncate large log files
echo "[4/6] Truncating large log files (>10MB)..." | tee -a ${LOG_FILE}
find /var/log -name "*.log" -size +10M -exec truncate -s 0 {} \; 2>&1 | tee -a ${LOG_FILE}

# Remove compressed logs
echo "[5/6] Removing compressed log files..." | tee -a ${LOG_FILE}
find /var/log -name "*.gz" -delete 2>&1 | tee -a ${LOG_FILE}

# Clean temp files
echo "[6/6] Cleaning temporary files..." | tee -a ${LOG_FILE}
rm -rf /tmp/* 2>&1 | tee -a ${LOG_FILE} || true
rm -rf /var/tmp/* 2>&1 | tee -a ${LOG_FILE} || true

# Show disk usage after cleanup
echo "=== Disk Usage After Cleanup ===" | tee -a ${LOG_FILE}
df -h / | tee -a ${LOG_FILE}
echo "=== Daily Cleanup Complete ===" | tee -a ${LOG_FILE}
echo "Timestamp: $(date)" | tee -a ${LOG_FILE}
