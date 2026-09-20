# SSL Certificate Automation Documentation

Automated SSL certificate monitoring, renewal, and rotation system for Let's Encrypt certificates.

## Overview

This automation system provides comprehensive SSL certificate management including:
- **Automated Monitoring**: Continuous certificate expiry monitoring
- **Intelligent Renewal**: Automatic renewal before expiration
- **Health Reporting**: Detailed certificate status reports
- **Alert Notifications**: Email and webhook alerts for certificate events
- **Systemd Integration**: Native systemd timer-based scheduling
- **Validation**: Certificate chain and validity verification

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  SSL Certificate Automation                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │  Monitor Script  │─────▶│  Python Manager  │            │
│  │  ssl_monitor.sh  │      │  ssl_cert_mgr.py │            │
│  └──────────────────┘      └──────────────────┘            │
│           │                          │                      │
│           │                          │                      │
│           ▼                          ▼                      │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │  Systemd Timer  │      │  Certbot Renewal │            │
│  │  (twice daily)   │      │  (twice daily)   │            │
│  └──────────────────┘      └──────────────────┘            │
│                                   │                          │
│                                   ▼                          │
│                          ┌──────────────────┐               │
│                          │  Nginx Reload    │               │
│                          │  (post-renewal)  │               │
│                          └──────────────────┘               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Python Certificate Manager (`ssl_certificate_manager.py`)
- Core certificate management logic
- Certificate scanning and validation
- Automated renewal operations
- Health report generation
- Email and webhook notifications

### 2. Monitor Script (`ssl_monitor.sh`)
- Bash wrapper for monitoring operations
- Manual certificate checks
- Dependency validation
- Cron job setup
- Dry-run testing capabilities

### 3. Systemd Services
- `ssl-certificate-monitor.service`: Monitoring service
- `ssl-certificate-monitor.timer`: Twice-daily monitoring schedule
- `certbot-renewal.service`: Certbot renewal service
- `certbot-renewal.timer`: Twice-daily renewal schedule

### 4. Configuration (`config.json`)
- Domain list configuration
- Email alert settings
- Renewal thresholds
- Monitoring parameters

## Installation

### Prerequisites
- Debian 12 (Bookworm) or compatible Linux distribution
- Python 3.8+
- certbot installed
- nginx web server
- root or sudo access

### Quick Install

```bash
# Navigate to the ssl_automation directory
cd /home/user/AI_Agents/ssl_automation

# Run the installation script
sudo ./install.sh
```

### Manual Installation

```bash
# 1. Install dependencies
sudo apt update
sudo apt install -y python3 python3-requests certbot nginx openssl

# 2. Create configuration directory
sudo mkdir -p /etc/ssl_certificate_manager

# 3. Copy configuration file
sudo cp config.json /etc/ssl_certificate_manager/

# 4. Install scripts
sudo cp ssl_certificate_manager.py /usr/local/bin/
sudo cp ssl_monitor.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/ssl_certificate_manager.py
sudo chmod +x /usr/local/bin/ssl_monitor.sh

# 5. Install systemd services
sudo cp ssl-certificate-monitor.service /etc/systemd/system/
sudo cp ssl-certificate-monitor.timer /etc/systemd/system/
sudo cp certbot-renewal.service /etc/systemd/system/
sudo cp certbot-renewal.timer /etc/systemd/system/

# 6. Reload systemd and enable timers
sudo systemctl daemon-reload
sudo systemctl enable ssl-certificate-monitor.timer
sudo systemctl start ssl-certificate-monitor.timer
sudo systemctl enable certbot-renewal.timer
sudo systemctl start certbot-renewal.timer

# 7. Setup log rotation
sudo cp logrotate.conf /etc/logrotate.d/ssl-certificate-manager
```

## Configuration

### Configuration File (`/etc/ssl_certificate_manager/config.json`)

```json
{
  "domains": [
    "calendar.shatsie.fun",
    "connect.shatsie.fun",
    "gotify.shatsie.fun"
  ],
  "cert_path": "/etc/letsencrypt/live",
  "renewal_threshold_days": 30,
  "email_alerts": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "your-email@gmail.com",
    "smtp_password": "your-app-specific-password",
    "recipients": ["admin@shatsie.fun"]
  },
  "webhook_url": null,
  "dry_run": false,
  "log_level": "INFO",
  "health_report_path": "/var/log/ssl_certificate_health_report.json",
  "monitoring": {
    "enabled": true,
    "check_interval_hours": 6,
    "alert_threshold_days": 7
  }
}
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `domains` | array | - | List of domains to monitor |
| `cert_path` | string | `/etc/letsencrypt/live` | Path to Let's Encrypt certificates |
| `renewal_threshold_days` | integer | 30 | Days before expiry to trigger renewal |
| `email_alerts.enabled` | boolean | true | Enable email notifications |
| `email_alerts.smtp_server` | string | `smtp.gmail.com` | SMTP server for alerts |
| `email_alerts.smtp_port` | integer | 587 | SMTP port |
| `email_alerts.smtp_username` | string | - | SMTP username |
| `email_alerts.smtp_password` | string | - | SMTP password (app-specific) |
| `email_alerts.recipients` | array | - | Email recipients for alerts |
| `webhook_url` | string | null | Webhook URL for notifications |
| `dry_run` | boolean | false | Enable dry-run mode |
| `monitoring.check_interval_hours` | integer | 6 | Monitoring check frequency |

## Usage

### Manual Certificate Monitoring

```bash
# Scan all certificates
sudo /usr/local/bin/ssl_monitor.sh

# Run in dry-run mode
sudo /usr/local/bin/ssl_monitor.sh --dry-run

# Check specific domain
sudo /usr/local/bin/ssl_certificate_manager.py scan --domain calendar.shatsie.fun

# Generate health report
sudo /usr/local/bin/ssl_certificate_manager.py report

# Validate certificate chain
sudo /usr/local/bin/ssl_certificate_manager.py validate
```

### Manual Certificate Renewal

```bash
# Renew all expiring certificates
sudo /usr/local/bin/ssl_certificate_manager.py renew

# Force renewal of specific certificate
sudo /usr/local/bin/ssl_certificate_manager.py renew --domain calendar.shatsie.fun --force

# Renew in dry-run mode
sudo /usr/local/bin/ssl_certificate_manager.py renew --dry-run
```

### Using the Monitor Script

```bash
# Run full monitoring cycle
sudo /usr/local/bin/ssl_monitor.sh

# Test the setup
sudo /usr/local/bin/ssl_monitor.sh --test

# Setup cron jobs (alternative to systemd)
sudo /usr/local/bin/ssl_monitor.sh --setup-cron
```

### Systemd Management

```bash
# Check status of monitoring timer
sudo systemctl status ssl-certificate-monitor.timer

# Check status of renewal timer
sudo systemctl status certbot-renewal.timer

# View monitoring logs
sudo journalctl -u ssl-certificate-monitor -f

# View renewal logs
sudo journalctl -u certbot-renewal -f

# Manually trigger monitoring
sudo systemctl start ssl-certificate-monitor.service

# Manually trigger renewal
sudo systemctl start certbot-renewal.service
```

## Monitoring and Alerts

### Monitoring Schedule

- **SSL Certificate Monitor**: Runs twice daily (3 AM and 3 PM)
- **Certbot Renewal**: Runs twice daily (midnight and noon)
- **Randomized Delay**: Up to 30 minutes to avoid load spikes

### Alert Thresholds

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Certificate Expired | 0 days | CRITICAL alert + immediate renewal attempt |
| Expiring Soon | ≤ 7 days | HIGH alert + renewal attempt |
| Approaching Expiry | ≤ 30 days | WARNING alert + scheduled renewal |
| Valid | > 30 days | INFO log only |

### Email Alerts

Email alerts are sent for:
- Certificate renewal success/failure
- Certificate expiry warnings
- Certificate validation failures
- System errors

### Webhook Integration

Configure webhook URL in `config.json` to receive JSON notifications:

```json
{
  "webhook_url": "https://your-webhook-endpoint.com/ssl-alerts"
}
```

Webhook payload format:
```json
{
  "event_type": "certificate_renewed",
  "timestamp": "2026-09-20T15:30:00Z",
  "data": {
    "domain": "calendar.shatsie.fun",
    "new_expiry": "2026-12-20T15:30:00Z",
    "status": "success"
  }
}
```

## Health Reports

### Generating Reports

```bash
# Generate and display report
sudo /usr/local/bin/ssl_certificate_manager.py report

# Report is automatically saved to
/var/log/ssl_certificate_health_report.json
```

### Report Format

```json
{
  "timestamp": "2026-09-20T15:30:00Z",
  "total_certificates": 3,
  "valid": 1,
  "expiring_soon": 2,
  "expired": 0,
  "certificates": [
    {
      "domain": "calendar.shatsie.fun",
      "path": "/etc/letsencrypt/live/calendar.shatsie.fun/cert.pem",
      "expiry_date": "2026-12-20T15:30:00Z",
      "days_until_expiry": 91,
      "issuer": "CN=R3,...",
      "status": "valid",
      "auto_renewal": true
    }
  ],
  "auto_renewal_enabled": 3
}
```

## Troubleshooting

### Common Issues

#### 1. Certificate Not Found
**Problem**: `Certificate file not found for domain`

**Solution**:
```bash
# Check if certificate exists
ls -la /etc/letsencrypt/live/

# Request new certificate if missing
sudo certbot certonly --nginx -d your-domain.com
```

#### 2. Renewal Fails
**Problem**: `Certificate renewal failed`

**Solution**:
```bash
# Check certbot logs
sudo cat /var/log/letsencrypt/letsencrypt.log

# Try manual renewal with debug output
sudo certbot renew --verbose --dry-run

# Check nginx configuration
sudo nginx -t
```

#### 3. Email Alerts Not Working
**Problem**: Email alerts not being sent

**Solution**:
```bash
# Check SMTP credentials in config.json
# For Gmail, use app-specific password: https://support.google.com/accounts/answer/185833

# Test SMTP connection manually
python3 -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587).starttls()"

# Check logs for email errors
sudo tail -f /var/log/ssl_certificate_manager.log
```

#### 4. Systemd Timer Not Running
**Problem**: Timer not active or not triggering

**Solution**:
```bash
# Check timer status
sudo systemctl status ssl-certificate-monitor.timer

# Enable timer if not enabled
sudo systemctl enable ssl-certificate-monitor.timer

# Start timer if not running
sudo systemctl start ssl-certificate-monitor.timer

# Check next scheduled run
sudo systemctl list-timers ssl-certificate-monitor
```

#### 5. Permission Errors
**Problem**: Permission denied accessing certificate files

**Solution**:
```bash
# Ensure scripts run as root
sudo /usr/local/bin/ssl_monitor.sh

# Check file permissions
sudo ls -la /etc/letsencrypt/live/
sudo chmod 755 /etc/letsencrypt/live/
```

### Debug Mode

Enable debug logging by editing configuration:
```json
{
  "log_level": "DEBUG",
  "dry_run": true
}
```

Or use command-line debug:
```bash
sudo /usr/local/bin/ssl_monitor.sh --verbose
```

### Log Locations

- **Application Logs**: `/var/log/ssl_certificate_manager.log`
- **Monitor Logs**: `/var/log/ssl_certificate_monitor.log`
- **Systemd Logs**: `journalctl -u ssl-certificate-monitor`
- **Certbot Logs**: `/var/log/letsencrypt/letsencrypt.log`
- **Health Reports**: `/var/log/ssl_certificate_health_report.json`

## Maintenance

### Regular Maintenance Tasks

#### Weekly
- Review health reports
- Check alert logs
- Verify certificate status

#### Monthly
- Test renewal process in dry-run mode
- Review and update configuration
- Check disk space for logs

#### Quarterly
- Review and rotate SMTP credentials
- Update monitoring thresholds
- Test backup/restore procedures

### Backup and Restore

#### Backup Configuration
```bash
# Backup configuration
sudo tar -czf ssl-cert-backup-$(date +%Y%m%d).tar.gz \
  /etc/ssl_certificate_manager/ \
  /usr/local/bin/ssl_certificate_manager.py \
  /usr/local/bin/ssl_monitor.sh \
  /etc/systemd/system/ssl-certificate-*.service \
  /etc/systemd/system/ssl-certificate-*.timer
```

#### Restore Configuration
```bash
# Restore from backup
sudo tar -xzf ssl-cert-backup-20260920.tar.gz -C /

# Reload systemd
sudo systemctl daemon-reload

# Restart services
sudo systemctl restart ssl-certificate-monitor.timer
sudo systemctl restart certbot-renewal.timer
```

### Updates and Upgrades

#### Update Scripts
```bash
# Navigate to ssl_automation directory
cd /home/user/AI_Agents/ssl_automation

# Pull latest changes
git pull

# Reinstall
sudo ./install.sh
```

#### Update Dependencies
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Update Python packages
sudo pip3 install --upgrade requests
```

## Security Considerations

### Credential Management
- Store SMTP passwords in `config.json` with appropriate file permissions (600)
- Use app-specific passwords for Gmail
- Consider using environment variables for sensitive data
- Regularly rotate SMTP credentials

### File Permissions
```bash
# Restrict configuration file access
sudo chmod 600 /etc/ssl_certificate_manager/config.json
sudo chown root:root /etc/ssl_certificate_manager/config.json

# Restrict script execution
sudo chmod 755 /usr/local/bin/ssl_certificate_manager.py
sudo chmod 755 /usr/local/bin/ssl_monitor.sh
```

### Network Security
- Ensure firewall allows outbound HTTPS (port 443) for Let's Encrypt
- Restrict access to monitoring logs
- Use secure SMTP (TLS) for email alerts

## Integration with Existing Systems

### Nginx Integration
The system automatically reloads nginx after successful certificate renewal via the `--post-hook` in certbot.

### Monitoring Systems
Health reports can be integrated with external monitoring systems:
- Prometheus: Export metrics from health report JSON
- Grafana: Visualize certificate expiry timelines
- Nagios: Parse health report for alert conditions

### CI/CD Integration
Include certificate validation in deployment pipelines:
```bash
# Pre-deployment certificate check
sudo /usr/local/bin/ssl_certificate_manager.py validate
if [ $? -ne 0 ]; then
  echo "Certificate validation failed - aborting deployment"
  exit 1
fi
```

## Performance Considerations

### Resource Usage
- **Memory**: ~50MB per Python process
- **Disk**: ~10MB for logs (with rotation)
- **Network**: Minimal (HTTPS requests to Let's Encrypt)
- **CPU**: Negligible (sporadic checks)

### Optimization Tips
- Adjust monitoring frequency based on requirements
- Use dry-run mode for testing
- Implement log rotation to manage disk space
- Cache certificate information to reduce openssl calls

## Uninstallation

### Complete Removal
```bash
# Run uninstall script
cd /home/user/AI_Agents/ssl_automation
sudo ./install.sh --uninstall
```

### Manual Removal
```bash
# Stop and disable services
sudo systemctl stop ssl-certificate-monitor.timer
sudo systemctl disable ssl-certificate-monitor.timer
sudo systemctl stop certbot-renewal.timer
sudo systemctl disable certbot-renewal.timer

# Remove service files
sudo rm /etc/systemd/system/ssl-certificate-monitor.*
sudo rm /etc/systemd/system/certbot-renewal.*

# Reload systemd
sudo systemctl daemon-reload

# Remove scripts
sudo rm /usr/local/bin/ssl_certificate_manager.py
sudo rm /usr/local/bin/ssl_monitor.sh

# Remove configuration (optional)
sudo rm -rf /etc/ssl_certificate_manager

# Remove log rotation
sudo rm /etc/logrotate.d/ssl-certificate-manager
```

## Support and Contributing

### Getting Help
- Check logs: `/var/log/ssl_certificate_manager.log`
- Review troubleshooting section above
- Test with dry-run mode first
- Check certbot documentation: https://letsencrypt.org/docs/

### Customization
The system is designed to be easily customizable:
- Add custom alert mechanisms via webhook
- Extend Python manager for additional functionality
- Modify monitoring schedules in systemd timers
- Add custom validation logic

## License

This SSL certificate automation system is provided as-is for managing Let's Encrypt certificates on your infrastructure.

## Version History

- **v1.0** (2026-09-20): Initial release
  - Automated certificate monitoring
  - Systemd timer integration
  - Email and webhook alerts
  - Health reporting
  - Comprehensive documentation