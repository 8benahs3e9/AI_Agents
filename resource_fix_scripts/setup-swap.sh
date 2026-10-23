#!/bin/bash
# Setup 2GB swap space to improve memory management
# This adds virtual memory to prevent OOM situations

set -e

SWAP_FILE="/swapfile"
SWAP_SIZE="2G"

echo "=== Setting Up Swap Space ==="
echo "Timestamp: $(date)"

# Check if swap already exists
if [ -f ${SWAP_FILE} ]; then
    echo "WARNING: Swap file already exists at ${SWAP_FILE}"
    echo "Removing existing swap file..."
    sudo swapoff ${SWAP_FILE} 2>/dev/null || true
    sudo rm -f ${SWAP_FILE}
fi

# Create swap file
echo "[1/5] Creating ${SWAP_SIZE} swap file..."
sudo fallocate -l ${SWAP_SIZE} ${SWAP_FILE}

# Set proper permissions
echo "[2/5] Setting permissions..."
sudo chmod 600 ${SWAP_FILE}

# Format as swap
echo "[3/5] Formatting as swap..."
sudo mkswap ${SWAP_FILE}

# Enable swap
echo "[4/5] Enabling swap..."
sudo swapon ${SWAP_FILE}

# Add to fstab for persistence
echo "[5/5] Adding to fstab for persistence..."
if ! grep -q "${SWAP_FILE}" /etc/fstab; then
    echo "${SWAP_FILE} none swap sw 0 0" | sudo tee -a /etc/fstab
else
    echo "Swap already in fstab"
fi

# Verify swap is active
echo "=== Swap Setup Complete ==="
echo "Swap status:"
swapon --show
echo "Memory status:"
free -h
echo "Timestamp: $(date)"

# Optimize swappiness (reduce swapping when enough RAM available)
echo "Optimizing swappiness..."
echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf
sudo sysctl vm.swappiness=10
