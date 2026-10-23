#!/bin/bash
# Optimize service memory limits using systemd overrides
# Adds memory limits to prevent runaway memory consumption

set -e

echo "=== Optimizing Service Memory Limits ==="
echo "Timestamp: $(date)"

# Function to add memory limit to a service
add_memory_limit() {
    local service=$1
    local memory_limit=$2

    echo "Adding memory limit to ${service}..."
    sudo systemctl edit ${service} --force --full << EOF
[Service]
MemoryLimit=${memory_limit}
MemoryMax=${memory_limit}
EOF

    echo "Applied ${memory_limit} limit to ${service}"
}

# Apply memory limits to key services
echo "[1/4] Optimizing gotify service..."
add_memory_limit "gotify" "128M"

echo "[2/4] Optimizing radicale service..."
add_memory_limit "radicale" "64M"

echo "[3/4] Optimizing fail2ban service..."
add_memory_limit "fail2ban" "64M"

echo "[4/4] Optimizing nginx service..."
add_memory_limit "nginx" "64M"

# Reload systemd and restart services
echo "Reloading systemd..."
sudo systemctl daemon-reload

echo "Restarting services with new limits..."
sudo systemctl restart gotify 2>/dev/null || echo "gotify restart failed (may not be running)"
sudo systemctl restart radicale 2>/dev/null || echo "radicale restart failed (may not be running)"
sudo systemctl restart fail2ban 2>/dev/null || echo "fail2ban restart failed (may not be running)"
sudo systemctl restart nginx 2>/dev/null || echo "nginx restart failed (may not be running)"

echo "=== Service Memory Optimization Complete ==="
echo "Timestamp: $(date)"
echo ""
echo "Service status:"
systemctl status gotify radicale fail2ban nginx --no-pager || true
