# SSL Certificate Automation - Quick Start Guide

## Current Status

✅ **Good News**: Your SSL certificates are actually valid and properly configured!

**Certificate Status (as of 2026-09-20):**
- `calendar.shatsie.fun`: ✅ Valid (expires in 56 days - 2026-11-16)
- `connect.shatsie.fun`: ✅ Valid (expires in 58 days - 2026-11-17)  
- `gotify.shatsie.fun`: ✅ Valid (expires in 56 days - 2026-11-16)

The audit report mentioned certificate expiry issues, but the actual certificates are valid and have auto-renewal properly configured via certbot.

## Installation

### Quick Install (Recommended)

```bash
cd /home/user/AI_Agents/ssl_automation
sudo ./install.sh
```

### What This Does

1. **Installs monitoring scripts** to `/usr/local/bin/`
2. **Sets up systemd timers** for automated monitoring (twice daily)
3. **Configures certbot auto-renewal** (twice daily)
4. **Creates configuration** in `/etc/ssl_certificate_manager/`
5. **Sets up log rotation** for monitoring logs
6. **Installs email/webhook alerts** (configurable)

## Post-Installation Configuration

### 1. Configure Email Alerts (Optional)

Edit `/etc/ssl_certificate_manager/config.json`:

```json
{
  "email_alerts": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "your-email@gmail.com",
    "smtp_password": "your-app-specific-password",
    "recipients": ["admin@shatsie.fun"]
  }
}
```

**For Gmail users**: Generate an app-specific password at https://support.google.com/accounts/answer/185833

### 2. Test the Setup

```bash
# Test the monitoring system
sudo /usr/local/bin/ssl_monitor.sh --test

# Manual certificate check
sudo /usr/local/bin/ssl_certificate_manager.py scan

# Generate health report
sudo /usr/local/bin/ssl_certificate_manager.py report
```

### 3. Check Systemd Status

```bash
# Check monitoring timer
sudo systemctl status ssl-certificate-monitor.timer

# Check renewal timer  
sudo systemctl status certbot-renewal.timer

# View monitoring logs
sudo journalctl -u ssl-certificate-monitor -f
```

## Manual Operations

### Check Certificate Status

```bash
# Quick status check
sudo /usr/local/bin/ssl_monitor.sh

# Detailed report
sudo /usr/local/bin/ssl_certificate_manager.py report
```

### Manual Renewal

```bash
# Renew all certificates (if needed)
sudo /usr/local/bin/ssl_certificate_manager.py renew

# Force renewal of specific certificate
sudo /usr/local/bin/ssl_certificate_manager.py renew --domain calendar.shatsie.fun --force
```

### Validate Certificates

```bash
# Validate certificate chains
sudo /usr/local/bin/ssl_certificate_manager.py validate
```

## Monitoring Schedule

The automation runs on the following schedule:

- **SSL Certificate Monitor**: Twice daily (3 AM and 3 PM UTC)
- **Certbot Auto-Renewal**: Twice daily (midnight and noon UTC)
- **Randomized Delay**: Up to 30 minutes to avoid load spikes

## Alert Thresholds

- **Critical (≤ 0 days)**: Certificate expired - immediate renewal attempt
- **High (≤ 7 days)**: Expiring soon - renewal attempt + alert
- **Warning (≤ 30 days)**: Approaching expiry - scheduled renewal + alert
- **Info (> 30 days)**: Valid - no action needed

## Troubleshooting

### Check Logs

```bash
# Application logs
sudo tail -f /var/log/ssl_certificate_manager.log

# Monitor logs
sudo tail -f /var/log/ssl_certificate_monitor.log

# Systemd logs
sudo journalctl -u ssl-certificate-monitor -f
```

### Manual Certificate Check

```bash
# Check specific certificate
openssl x509 -enddate -noout -in /etc/letsencrypt/live/calendar.shatsie.fun/cert.pem

# Check all certificates
sudo certbot certificates
```

### Test Certbot Renewal

```bash
# Dry-run renewal test
sudo certbot renew --dry-run

# Manual renewal
sudo certbot renew
```

## Current Certificate Health

Based on the test run, your certificates are in excellent shape:

- **All certificates**: Valid and properly configured
- **Auto-renewal**: Enabled for all domains
- **Certificate chains**: Valid and properly signed
- **Expiry dates**: 56-58 days from now (mid-November 2026)

## Why This Automation Is Still Useful

Even though your certificates are currently valid, this automation provides:

1. **Proactive Monitoring**: Catch issues before they become problems
2. **Automated Alerts**: Get notified before certificates expire
3. **Health Reporting**: Track certificate status over time
4. **Validation**: Ensure certificate chains remain valid
5. **Documentation**: Maintain audit trail of certificate operations
6. **Peace of Mind**: Know that certificates are being monitored 24/7

## Next Steps

1. **Install the automation**: `sudo ./install.sh`
2. **Configure email alerts** (optional but recommended)
3. **Test the setup**: `sudo /usr/local/bin/ssl_monitor.sh --test`
4. **Monitor logs**: Check that everything is working correctly
5. **Set up monitoring**: Configure external monitoring if desired

## Support

For detailed documentation, see `README.md` in this directory.

For issues:
1. Check logs in `/var/log/ssl_certificate_manager.log`
2. Run with `--verbose` flag for debugging
3. Test with `--dry-run` flag first
4. Review troubleshooting section in README.md