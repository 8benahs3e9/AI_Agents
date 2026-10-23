# Resource Exhaustion Fix Scripts

All scripts created to resolve resource exhaustion on et-gtw server without disk resizing.

## Scripts

1. **aggressive-cleanup.sh** - Immediate disk cleanup (500MB-1GB savings)
2. **log-forward.sh** - Forward logs to backend server (200MB-500MB ongoing savings)
3. **optimized-cron.sh** - Reduce monitoring frequency (70% fewer log entries)
4. **install-logrotate.sh** - Strict log rotation (prevents log bloat)
5. **daily-cleanup.sh** - Automated daily cleanup (100MB-300MB daily savings)
6. **setup-swap.sh** - Add 2GB swap space (prevents OOM errors)
7. **optimize-service-memory.sh** - Service memory limits (prevents runaway memory)
8. **deploy-all.sh** - Master deployment script (runs all fixes in order)

## Quick Start

### On et-gtw server:

```bash
# 1. Copy scripts to system location
sudo cp *.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/*.sh

# 2. Run master deployment script
sudo /usr/local/bin/deploy-all.sh

# 3. (Optional) Configure log forwarding
sudo nano /usr/local/bin/log-forward.sh
# Edit BACKEND_USER="user" to correct username
sudo /usr/local/bin/log-forward.sh
```

## Expected Results

- **Disk:** 79% → 60-65% (after cleanup + ongoing maintenance)
- **Memory:** ~85% → ~70% (with swap + service limits)
- **Logs:** Controlled rotation, max 3 x 5MB per log file

## Documentation

See `DEPLOYMENT_GUIDE.md` for detailed deployment instructions, troubleshooting, and rollback procedures.
