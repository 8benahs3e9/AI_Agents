# Resource Exhaustion Fix - Deployment Guide

**Date:** 2026-10-02
**Target:** et-gtw gateway server (GCP e2-micro instance)
**Purpose:** Resolve disk and memory exhaustion without resizing

---

## Overview

This deployment includes 7 scripts to fix resource exhaustion issues on your et-gtw server. All solutions avoid disk resizing and focus on cleanup, optimization, and offloading.

## Scripts Created

1. **aggressive-cleanup.sh** - Immediate disk cleanup
2. **log-forward.sh** - Forward logs to backend server
3. **optimized-cron.sh** - Reduce monitoring frequency
4. **install-logrotate.sh** - Strict log rotation
5. **daily-cleanup.sh** - Automated daily cleanup
6. **setup-swap.sh** - Add 2GB swap space
7. **optimize-service-memory.sh** - Service memory limits

---

## Deployment Steps

### Step 1: Transfer Scripts to et-gtw

From your local machine:

```bash
# Copy all scripts to et-gtw
scp resource_fix_scripts/*.sh user@et-gtw:/tmp/

# SSH into et-gtw
ssh user@et-gtw
```

### Step 2: Make Scripts Executable

```bash
cd /tmp
chmod +x *.sh
```

### Step 3: Install Scripts to System Locations

```bash
# Copy scripts to /usr/local/bin
sudo cp aggressive-cleanup.sh /usr/local/bin/
sudo cp log-forward.sh /usr/local/bin/
sudo cp daily-cleanup.sh /usr/local/bin/
sudo cp setup-swap.sh /usr/local/bin/
sudo cp optimize-service-memory.sh /usr/local/bin/
sudo cp optimized-cron.sh /usr/local/bin/
sudo cp install-logrotate.sh /usr/local/bin/

# Ensure all are executable
sudo chmod +x /usr/local/bin/*.sh
```

### Step 4: Run Immediate Fixes (Critical)

Run these in order:

```bash
# 1. Aggressive cleanup (IMMEDIATE - frees disk space)
sudo /usr/local/bin/aggressive-cleanup.sh

# 2. Install strict log rotation (IMMEDIATE - controls log growth)
sudo /usr/local/bin/install-logrotate.sh

# 3. Setup swap space (IMMEDIATE - improves memory)
sudo /usr/local/bin/setup-swap.sh

# 4. Optimize service memory (IMMEDIATE - prevents runaway memory)
sudo /usr/local/bin/optimize-service-memory.sh
```

### Step 5: Configure Log Forwarding (Optional)

**IMPORTANT:** Before running this, you must:

1. Edit `/usr/local/bin/log-forward.sh` and set the correct backend username:
   ```bash
   sudo nano /usr/local/bin/log-forward.sh
   # Change: BACKEND_USER="user" to actual backend username
   ```

2. Ensure SSH key authentication is set up between et-gtw and backend (10.128.0.6)

Then run:
```bash
# Test log forwarding manually first
sudo /usr/local/bin/log-forward.sh

# If successful, it will be added to cron in next step
```

### Step 6: Install Optimized Cron Schedule

```bash
# This replaces current crontab with optimized schedule
sudo /usr/local/bin/optimized-cron.sh
```

### Step 7: Verify Everything

```bash
# Check disk usage
df -h /

# Check memory and swap
free -h

# Check new crontab
sudo crontab -l

# Check logrotate config
cat /etc/logrotate.d/custom-health-logs

# Check service status
systemctl status gotify radicale fail2ban nginx
```

---

## What Each Script Does

### 1. aggressive-cleanup.sh
- Cleans package cache
- Removes unused packages
- Removes old kernels
- Cleans journal logs (keeps 3 days)
- Removes compressed logs
- Cleans temp files
- **Expected disk savings:** 500MB - 1GB

### 2. log-forward.sh
- Compresses logs and sends to backend server (10.128.0.6)
- Clears local logs after successful transfer
- Requires SSH key auth to backend
- **Expected disk savings:** 200MB - 500MB (ongoing)

### 3. optimized-cron.sh
- Changes health checks from every 5 min to every 15 min
- Changes disk/security checks from hourly to every 6 hours
- Adds daily log forwarding (4 AM)
- Adds daily cleanup (3 AM)
- **Expected reduction:** 70% fewer log entries

### 4. install-logrotate.sh
- Hourly log rotation (instead of daily)
- Keeps only 3 rotations
- Size limits: 5MB for system logs, 2MB for security logs
- Max age: 1 day
- **Expected disk savings:** Prevents log bloat

### 5. daily-cleanup.sh
- Runs daily at 3 AM via cron
- Cleans package cache
- Removes unused packages
- Cleans journal logs (keeps 2 days)
- Truncates large log files (>10MB)
- Removes compressed logs
- **Expected disk savings:** 100MB - 300MB daily

### 6. setup-swap.sh
- Creates 2GB swap file
- Adds to fstab for persistence
- Optimizes swappiness to 10
- **Expected benefit:** Prevents OOM errors, adds 2GB virtual memory

### 7. optimize-service-memory.sh
- Adds memory limits via systemd:
  - gotify: 128MB
  - radicale: 64MB
  - fail2ban: 64MB
  - nginx: 64MB
- **Expected benefit:** Prevents runaway memory consumption

---

## Configuration Requirements

### For Log Forwarding

Edit `/usr/local/bin/log-forward.sh`:
```bash
BACKEND_USER="your_actual_username"  # Change this
```

Ensure SSH key authentication:
```bash
# From et-gtw, test SSH to backend
ssh user@10.128.0.6 "echo 'SSH works'"
```

### For Backend Log Storage

On backend server (skype):
```bash
# Create log archive directory
sudo mkdir -p /var/log/archive
sudo chown user:user /var/log/archive
```

---

## Monitoring After Deployment

### Check Disk Usage
```bash
df -h /
# Should show significant improvement after aggressive cleanup
```

### Check Memory
```bash
free -h
# Should show 2GB swap available
```

### Check Logs
```bash
# Verify logs are rotating
ls -lh /var/log/*.log*

# Check log sizes
du -sh /var/log/*.log
```

### Check Cron Jobs
```bash
sudo crontab -l
# Should show optimized schedule
```

---

## Rollback (If Needed)

### Restore Original Crontab
```bash
# Backup is saved in /var/backups/cron/
sudo crontab /var/backups/cron/crontab_backup_<timestamp>
```

### Remove Swap
```bash
sudo swapoff /swapfile
sudo rm /swapfile
sudo sed -i '/swapfile/d' /etc/fstab
```

### Remove Service Memory Limits
```bash
sudo systemctl revert gotify
sudo systemctl revert radicale
sudo systemctl revert fail2ban
sudo systemctl revert nginx
sudo systemctl daemon-reload
sudo systemctl restart gotify radicale fail2ban nginx
```

### Remove Log Rotation Config
```bash
sudo rm /etc/logrotate.d/custom-health-logs
```

---

## Expected Results

### Before (from audit)
- Disk: 79% (7.2GB/9.7GB)
- Memory: ~85% usage
- Log entries: 179K+ in system-health.log

### After (expected)
- Disk: 60-65% (after cleanup + ongoing maintenance)
- Memory: ~70% (with swap + service limits)
- Log entries: Controlled rotation, max 3 x 5MB

---

## Troubleshooting

### Log Forwarding Fails
- Check SSH connectivity: `ssh user@10.128.0.6`
- Verify backend directory exists: `ssh user@10.128.0.6 "ls -la /var/log/archive"`
- Check log-forward.sh script for correct username

### Swap Not Showing
- Check: `swapon --show`
- If empty, check if file exists: `ls -lh /swapfile`
- Verify fstab entry: `cat /etc/fstab`

### Services Won't Start After Memory Limits
- Limits may be too low for your workload
- Edit systemd override: `sudo systemctl edit gotify`
- Increase MemoryLimit value
- Restart service: `sudo systemctl restart gotify`

### Cron Jobs Not Running
- Check cron service: `systemctl status cron`
- Check cron logs: `grep CRON /var/log/syslog`
- Verify script permissions: `ls -la /usr/local/bin/*.sh`

---

## Maintenance

### Weekly
- Check disk usage: `df -h /`
- Check memory: `free -h`
- Review logs: `ls -lh /var/log/*.log*`

### Monthly
- Review log rotation effectiveness
- Check if swap is being used: `cat /proc/swaps`
- Verify cron jobs are running correctly
- Review backend log storage capacity

---

## Support

If issues arise:
1. Check script logs in `/var/log/daily-cleanup.log`
2. Review system logs: `journalctl -xe`
3. Verify each script ran successfully
4. Use rollback procedures if needed

---

**Deployment completed:** [Date after deployment]
**Next review:** 1 week after deployment
