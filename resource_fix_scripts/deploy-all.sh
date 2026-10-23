#!/bin/bash
# Master deployment script - runs all resource fixes in order
# Run this on et-gtw server after copying scripts to /usr/local/bin

set -e

echo "========================================"
echo "Resource Exhaustion Fix - Full Deployment"
echo "========================================"
echo "Timestamp: $(date)"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: This script must be run as root (use sudo)"
    exit 1
fi

# Check if scripts are in /usr/local/bin
if [ ! -f /usr/local/bin/aggressive-cleanup.sh ]; then
    echo "ERROR: Scripts not found in /usr/local/bin/"
    echo "Please copy scripts first:"
    echo "  sudo cp *.sh /usr/local/bin/"
    echo "  sudo chmod +x /usr/local/bin/*.sh"
    exit 1
fi

echo "Step 1: Aggressive Cleanup (IMMEDIATE)"
echo "--------------------------------------"
/usr/local/bin/aggressive-cleanup.sh
echo ""

echo "Step 2: Install Strict Log Rotation"
echo "-----------------------------------"
/usr/local/bin/install-logrotate.sh
echo ""

echo "Step 3: Setup Swap Space"
echo "------------------------"
/usr/local/bin/setup-swap.sh
echo ""

echo "Step 4: Optimize Service Memory"
echo "-------------------------------"
/usr/local/bin/optimize-service-memory.sh
echo ""

echo "Step 5: Install Optimized Cron Schedule"
echo "---------------------------------------"
/usr/local/bin/optimized-cron.sh
echo ""

echo "Step 6: Log Forwarding (Manual Setup Required)"
echo "----------------------------------------------"
echo "NOTE: Log forwarding requires manual configuration:"
echo "1. Edit /usr/local/bin/log-forward.sh"
echo "2. Set BACKEND_USER to correct username"
echo "3. Ensure SSH key auth to backend (10.128.0.6)"
echo "4. Run manually: sudo /usr/local/bin/log-forward.sh"
echo ""

echo "========================================"
echo "Deployment Complete!"
echo "========================================"
echo ""
echo "Current Status:"
echo "---------------"
echo "Disk usage:"
df -h /
echo ""
echo "Memory & Swap:"
free -h
echo ""
echo "Active Cron Jobs:"
crontab -l
echo ""
echo "========================================"
echo "Next Steps:"
echo "========================================"
echo "1. Review the output above"
echo "2. Configure log forwarding (if using backend)"
echo "3. Monitor disk usage over next few days"
echo "4. Check /var/log/daily-cleanup.log for cleanup results"
echo ""
echo "Timestamp: $(date)"
