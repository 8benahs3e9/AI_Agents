# AI Agents - System Documentation

This file documents system configurations, learned information, and operational procedures for the AI_Agents project.

---

## Resource Management Configuration

### System Information
- **Server:** et-gtw (Gateway Server)
- **Platform:** GCP e2-micro instance
- **Region:** us-central1-a
- **Resources:** 2 vCPU, 1GB RAM, 10GB disk
- **Backend:** skype (10.128.0.6) - no external IP

### Resource Fixes Applied (2026-10-02)

#### Automated Scripts Location
All resource management scripts are in `/usr/local/bin/`:
- `aggressive-cleanup.sh` - Immediate disk cleanup
- `daily-cleanup.sh` - Automated daily cleanup (runs 3 AM)
- `install-logrotate.sh` - Strict log rotation configuration
- `setup-swap.sh` - 2GB swap space management
- `optimize-service-memory.sh` - Service memory limits
- `optimized-cron.sh` - Optimized monitoring schedule
- `log-forward.sh` - Log forwarding to backend (optional)
- `deploy-all.sh` - Master deployment script

#### Log Rotation Configuration
File: `/etc/logrotate.d/custom-health-logs`
- Hourly rotation
- Max 3 rotations per log
- Size limits: 5MB (system logs), 2MB (security logs)
- Max age: 1 day

#### Cron Schedule
File: System crontab
- System health check: Every 15 minutes (was 5 minutes)
- Disk watch: Every 6 hours (was hourly)
- Security monitor: Every 6 hours (was hourly)
- Log forwarding: Daily at 4 AM (if configured)
- Daily cleanup: Daily at 3 AM
- Log rotation: Hourly

#### Service Memory Limits
Applied via systemd overrides in `/etc/systemd/system/<service>.service.d/override.conf`:
- gotify: 128M
- radicale: 64M
- fail2ban: 64M
- nginx: 64M
- shadowsocks-v2ray-ws: 128M (MemoryMax in service file, added 2026-10-08)

#### Swap Configuration
- 2GB swap file at `/swapfile`
- Swappiness: 10
- Added to `/etc/fstab` for persistence

#### Backup Locations
- Cron backups: `/var/backups/cron/crontab_backup_*`
- Daily cleanup log: `/var/log/daily-cleanup.log`

---

## Verification Commands

### Check Disk Usage
```bash
df -h /
```

### Check Memory and Swap
```bash
free -h
swapon --show
```

### Check Cron Jobs
```bash
sudo crontab -l
```

### Check Log Rotation Config
```bash
cat /etc/logrotate.d/custom-health-logs
```

### Check Service Status
```bash
systemctl status gotify radicale fail2ban nginx
```

### Check Service Memory Limits
```bash
systemctl show gotify --property=MemoryLimit
systemctl show radicale --property=MemoryLimit
```

---

## Troubleshooting

### Disk Space Issues
Run immediate cleanup:
```bash
sudo /usr/local/bin/aggressive-cleanup.sh
```

### Log Forwarding Issues
Edit configuration:
```bash
sudo nano /usr/local/bin/log-forward.sh
# Set BACKEND_USER to correct username
```

### Service Won't Start After Memory Limits
Edit override:
```bash
sudo systemctl edit gotify
# Increase MemoryLimit value
sudo systemctl restart gotify
```

### Restore Original Cron
```bash
sudo crontab /var/backups/cron/crontab_backup_<timestamp>
```

---

## Rollback Procedures

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

## Key Metrics (Post-Fix - 2026-10-02)
- Disk: 78% (7.1GB/9.7GB) - 2.1GB free
- Memory: 57% (557MB/969MB) + 2GB swap
- Swap usage: 4MB (healthy)

---

## Related Documentation
- `/home/user/AI_Agents/resource_fix_scripts/DEPLOYMENT_GUIDE.md` - Detailed deployment guide
- `/home/user/AI_Agents/resource_fix_scripts/README.md` - Quick start guide
- `/home/user/AI_Agents/RESOURCE_MONITORING_ANALYSIS_2026-09-20.md` - Original analysis
- `/home/user/AI_Agents/VM_SECURITY_RESOURCE_AUDIT_2026-09-20.md` - Security audit
- `/home/user/AI_Agents/TRAFFIC_FINGERPRINTING_MITIGATION_RESOURCE_ANALYSIS.md` - Traffic fingerprinting mitigation resource analysis (2026-10-06)
- `/home/user/AI_Agents/SSH_HARDENING_PHASE1_STATUS.md` - SSH hardening Phase 1 status and IAP tunnel instructions (2026-10-06)
- `/home/user/AI_Agents/SHADOWSOCKS_V2RAY_INTEGRATION_2026-10-08.md` - Shadowsocks V2Ray + Nginx integration documentation (2026-10-08)
- `/home/user/AI_Agents/SHADOWSOCKS_CORRECTION_2026-10-08.md` - Correction of previous incorrect analysis (2026-10-08)
- `/home/user/AI_Agents/DNS_LEAK_PREVENTION_PHASE4_STATUS.md` - DNS leak prevention Phase 4 status (2026-10-07)

### Historical Documentation (Archived)
- `/home/user/AI_Agents/SHADOWSOCKS_PHASE2_PLAN.md` - Original Shadowsocks plan (superseded by V2Ray integration)
- `/home/user/AI_Agents/SHADOWSOCKS_PHASE2_STATUS.md` - Original Shadowsocks status (superseded by V2Ray integration)
- `/home/user/AI_Agents/SHADOWSOCKS_CLIENT_SETUP_GUIDE.md` - Original client setup guide (superseded by V2Ray integration)
- `/home/user/AI_Agents/DNS_LEAK_PREVENTION_PHASE4_PLAN.md` - DNS leak prevention plan (implementation complete)
- `/home/user/AI_Agents/TESTING_VALIDATION_PHASE5_PLAN.md` - Testing plan (testing complete)
- `/home/user/AI_Agents/TESTING_VALIDATION_PHASE5_STATUS.md` - Testing status (superseded by V2Ray integration)
- `/home/user/AI_Agents/CLIENT_CONFIGURATION_ANALYSIS_2026-10-07.md` - Client analysis (based on incorrect assumptions)

---

## GCP IAP Tunneling for SSH Testing

### Testing SSH on Non-Standard Ports via IAP

When changing SSH ports (e.g., from 22 to 2222), use IAP tunneling to test before removing the old port:

#### 1. Update GCP Firewall Rule
```bash
# Add new port to existing IAP rule
gcloud compute firewall-rules update allow-ssh-from-iap \
  --project=delta-surface-468416-f5 \
  --allow tcp:22,tcp:2222
```

#### 2. Set Up IAP Forwarding Tunnel
```bash
gcloud compute start-iap-tunnel et-gtw 2222 \
  --project=delta-surface-468416-f5 \
  --zone=us-central1-a \
  --local-host-port=localhost:2222
```

#### 3. Test SSH Connection
```bash
ssh -p 2222 user@localhost
```

#### 4. Remove Old Port (After Successful Test)
```bash
# Edit /etc/ssh/sshd_config: remove "Port 22"
sudo ufw delete allow 22/tcp
sudo systemctl restart sshd
```

### IAP Source Range
- **Range**: 35.235.240.0/20
- **Purpose**: Identity-Aware Proxy (IAP) for secure SSH access

### Current SSH Configuration (2026-10-06)
- **SSH Port**: 2222 (port 22 removed) ✅
- **Compression**: Disabled ✅
- **Authentication**: Key-only ✅
- **Access**: Via IAP tunnel or direct connection on port 2222
- **Documentation**: `/home/user/AI_Agents/SSH_HARDENING_PHASE1_STATUS.md`

---

## Shadowsocks Configuration (2026-10-08)

### Shadowsocks V2Ray + Nginx Integration

**Service**: shadowsocks-v2ray-ws.service (NOT shadowsocks-libev.service)
- **Status**: Active ✅ (running since 2026-10-07 12:03:54 UTC)
- **Port**: 10000 (localhost only)
- **Bind**: 127.0.0.1 (not directly accessible externally)
- **Plugin**: ss-v2ray-plugin (WebSocket mode)
- **Path**: /assets/telemetry/ws-7f3a91c2
- **TLS**: Terminated by Nginx on port 443
- **Memory**: 25.2M (max 128M)
- **Documentation**: `/home/user/AI_Agents/SHADOWSOCKS_V2RAY_INTEGRATION_2026-10-08.md`

### Architecture
```
Client → Nginx (TLS on 443) → WebSocket Path → V2Ray Plugin → Shadowsocks (127.0.0.1:10000) → Internet
```

### Shadowsocks Config File
**File**: `/etc/shadowsocks-libev/config.json`
- **Password**: `I/GiLCVJWbDuSyPEqatn3YMwe6e5S4w+k1FDTfdHZsk=`
- **Method**: aes-256-gcm
- **DNS**: 10.100.0.1 (WireGuard gateway with DNS-over-TLS)

### Client Configuration
Configure Shadowsocks clients with:
- **Server**: connect.shatsie.fun
- **Port**: 443 (HTTPS)
- **Path**: /assets/telemetry/ws-7f3a91c2
- **Protocol**: WSS (WebSocket Secure)
- **Password**: `I/GiLCVJWbDuSyPEqatn3YMwe6e5S4w+k1FDTfdHZsk=`
- **Method**: aes-256-gcm

### Service Management
```bash
# Start/Stop/Restart
sudo systemctl start shadowsocks-v2ray-ws.service
sudo systemctl stop shadowsocks-v2ray-ws.service
sudo systemctl restart shadowsocks-v2ray-ws.service

# Check status
sudo systemctl status shadowsocks-v2ray-ws.service
```

### Security Advantages
- ✅ Multi-layer obfuscation (TLS + WebSocket + Shadowsocks)
- ✅ Appears as HTTPS WebSocket traffic
- ✅ Localhost binding (not directly accessible)
- ✅ Nginx reverse proxy protection
- ✅ Path-based access control
- **Fingerprinting Resistance**: ~20-30% (significant improvement from simple Shadowsocks)

---

## DNS Configuration (2026-10-07)

### DNS-over-TLS
- **Service**: Unbound DNS resolver
- **Status**: Active ✅
- **Configuration**: DNS-over-TLS with Cloudflare (1.1.1.1@853) and Quad9 (9.9.9.9@853)
- **DNSSEC**: Enabled ✅
- **Privacy**: QNAME minimization, hide identity, hide version ✅
- **Documentation**: `/home/user/AI_Agents/DNS_LEAK_PREVENTION_PHASE4_STATUS.md`

### DNS Flow
```
Client → Shadowsocks (encrypted) → 10.100.0.1 (Unbound) → DNS-over-TLS (encrypted) → Cloudflare/Quad9
```

### DNS Leak Prevention
- ✅ DNS queries encrypted through Shadowsocks tunnel
- ✅ DNS queries encrypted via DNS-over-TLS to upstream
- ✅ DNS queries go through VPN tunnel
- ✅ No DNS leaks to ISP
- ✅ DNSSEC validation enabled

---

## Traffic Fingerprinting Mitigation Summary (2026-10-06 to 2026-10-08)

### Completed Phases

**Phase 1: SSH Hardening** (2026-10-06)
- SSH moved from port 22 to port 2222
- SSH compression disabled
- Zero service disruption
- Documentation: `/home/user/AI_Agents/SSH_HARDENING_PHASE1_STATUS.md`

**Phase 2: Shadowsocks Implementation** (2026-10-06)
- shadowsocks-libev installed and configured
- Original simple Shadowsocks setup (port 8388)
- Zero service disruption
- Documentation: `/home/user/user/AI_Agents/SHADOWSOCKS_PHASE2_STATUS.md` (historical)

**Phase 2b: V2Ray + Nginx Integration** (2026-10-07)
- Upgraded to shadowsocks-v2ray-ws.service
- Added V2Ray WebSocket plugin
- Nginx reverse proxy for TLS termination
- Changed to localhost binding (127.0.0.1:10000)
- Documentation: `/home/user/AI_Agents/SHADOWSOCKS_V2RAY_INTEGRATION_2026-10-08.md`

**Phase 4: DNS Leak Prevention** (2026-10-07)
- DNS-over-TLS verified active (Cloudflare + Quad9)
- DNSSEC validation enabled
- Privacy features enabled
- Documentation: `/home/user/AI_Agents/DNS_LEAK_PREVENTION_PHASE4_STATUS.md`

### Security Improvements

**Fingerprinting Resistance**:
- Before: ~95% accuracy (plain WireGuard + SSH on port 22)
- After (with V2Ray + WebSocket): ~20-30% accuracy (if clients use V2Ray configuration)
- **Actual Improvement**: SIGNIFICANT (multi-layer obfuscation: TLS + WebSocket + Shadowsocks)
- **Note**: Clients must be reconfigured to use connect.shatsie.fun with WSS path

**DNS Security**:
- Double encryption (Shadowsocks + DNS-over-TLS)
- DNSSEC validation
- Privacy features (QNAME minimization, hide identity)
- No DNS leaks

### Current Configuration

- **SSH**: Port 2222, compression disabled ✅
- **Shadowsocks V2Ray**: Port 10000 (localhost), V2Ray WebSocket plugin, Nginx TLS proxy ✅
- **WireGuard**: Port 51820, active ✅
- **DNS**: DNS-over-TLS with Cloudflare/Quad9 ✅
- **Nginx**: Reverse proxy for Shadowsocks WSS ✅
- **All Services**: Running normally ✅

### Client Status

- **Android**: Status unknown (needs reconfiguration for V2Ray WSS)
- **Linux Mint**: Using WireGuard (active connection, handshake 6 seconds ago)
- **Note**: Clients must be reconfigured to use connect.shatsie.fun with WSS path /assets/telemetry/ws-7f3a91c2
- **Documentation**: `/home/user/AI_Agents/SHADOWSOCKS_V2RAY_INTEGRATION_2026-10-08.md`
- **Recommendation**: Reconfigure clients to use V2Ray WebSocket configuration

### Optional Future Enhancements

- **Phase 3**: Traffic Padding (50-200% bandwidth overhead, reduces accuracy to ~20%)
- **Phase 6**: Multi-Hop Architecture (additional VPS, $5-10/month)
- **Phase 7**: Dynamic Configuration (port rotation)

---

**Last Updated:** 2026-10-08
**Next Review:** 2026-10-15 (1 week)
**Action Required**: Reconfigure clients to use V2Ray WebSocket configuration (connect.shatsie.fun with WSS path /assets/telemetry/ws-7f3a91c2)
