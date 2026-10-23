#!/bin/bash
# Aggressive cleanup script for et-gtw server
# Run this immediately to free disk space

set -e

echo "=== Starting Aggressive Cleanup ==="
echo "Timestamp: $(date)"

# Clean package cache
echo "[1/7] Cleaning package cache..."
sudo apt clean
sudo apt autoclean

# Remove unused packages
echo "[2/7] Removing unused packages..."
sudo apt autoremove -y

# Remove old kernels (keep current + 1 previous)
echo "[3/7] Removing old kernels..."
sudo apt autoremove --purge -y

# Clean journal logs (keep only 3 days)
echo "[4/7] Cleaning journal logs (keeping 3 days)..."
sudo journalctl --vacuum-time=3d

# Clean compressed logs
echo "[5/7] Removing compressed log files..."
sudo rm -rf /var/log/*.gz /var/log/*/*.gz 2>/dev/null || true

# Clean temp files
echo "[6/7] Cleaning temporary files..."
sudo rm -rf /tmp/* 2>/dev/null || true
sudo rm -rf /var/tmp/* 2>/dev/null || true

# Clean user temp
echo "[7/7] Cleaning user temp files..."
rm -rf ~/.cache/* 2>/dev/null || true

echo "=== Cleanup Complete ==="
echo "Disk usage after cleanup:"
df -h /
echo "Timestamp: $(date)"
