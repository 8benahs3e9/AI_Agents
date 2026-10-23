# Phase 2: WireGuard Obfuscation with Shadowsocks - Implementation Plan

**Date**: 2026-10-06
**Server**: et-gtw (Gateway Server)
**Status**: 📋 Planning
**Effort**: Medium (1-2 hours)
**Impact**: High (protocol obfuscation)

---

## Resource Status Check (Pre-Installation)

### Current Resources
- **Memory**: 465MB available (48% free) ✅
- **Disk**: 2.1GB free (22% free) ✅
- **CPU Load**: Low (~0.10) ✅

### Expected Resource Impact
- **Disk**: ~400KB (shadowsocks-libev package + dependencies)
- **Memory**: ~25MB (shadowsocks-libev service runtime)
- **CPU**: ~2-5% (encryption/decryption overhead)

### Resource Assessment
- ✅ **Sufficient memory**: 465MB available → ~440MB after installation (45% free)
- ✅ **Sufficient disk**: 2.1GB available → ~2.1GB after installation (negligible change)
- ✅ **Sufficient CPU**: Low load → minimal impact

---

## Implementation Plan

### Step 1: Pre-Installation Checks
- [x] Verify memory availability (465MB free)
- [x] Verify disk space (2.1GB free)
- [x] Verify current services running (WireGuard, Nginx, Gotify, Unbound)
- [ ] Check package details and dependencies

### Step 2: Package Installation
- [ ] Update package lists
- [ ] Install shadowsocks-libev package
- [ ] Verify installation success
- [ ] Check package size and dependencies

### Step 3: Configuration
- [ ] Create Shadowsocks configuration directory
- [ ] Generate strong password
- [ ] Create Shadowsocks config file
- [ ] Set appropriate file permissions

### Step 4: Service Configuration
- [ ] Apply memory limit to shadowsocks-libev service (64MB limit)
- [ ] Create systemd override
- [ ] Verify service configuration

### Step 5: Firewall Configuration
- [ ] Add UFW rule for Shadowsocks port 8388 (TCP)
- [ ] Add UFW rule for Shadowsocks port 8388 (UDP)
- [ ] Reload UFW firewall
- [ ] Verify firewall rules

### Step 6: Service Start
- [ ] Enable shadowsocks-libev service
- [ ] Start shadowsocks-libev service
- [ ] Verify service status
- [ ] Check service logs

### Step 7: Verification
- [ ] Verify Shadowsocks listening on port 8388
- [ ] Verify all other services still running
- [ ] Check memory usage
- [ ] Check disk usage

### Step 8: Documentation
- [ ] Document configuration
- [ ] Document client setup instructions
- [ ] Update AGENTS.md
- [ ] Create rollback procedures

---

## Configuration Details

### Shadowsocks Configuration
**File**: `/etc/shadowsocks-libev/config.json`

**Settings**:
- Server: 0.0.0.0 (listen on all interfaces)
- Port: 8388 (default Shadowsocks port)
- Password: [GENERATED STRONG PASSWORD]
- Method: aes-256-gcm (strong encryption)
- Timeout: 60 seconds
- Mode: tcp_and_udp
- Fast Open: enabled (performance optimization)

### Memory Limit
**File**: `/etc/systemd/system/shadowsocks-libev.service.d/override.conf`

**Limit**: 64MB (consistent with other services)

### Firewall Rules
- Port 8388/tcp: ALLOW IN
- Port 8388/udp: ALLOW IN

---

## Security Considerations

### Password Security
- Generate strong random password (32+ characters)
- Store securely (config file with restricted permissions)
- Share with clients via secure channel

### Encryption Method
- aes-256-gcm: Strong, widely supported
- Alternative: chacha20-poly1305 (better performance on mobile)

### Network Exposure
- Shadowsocks will be accessible from any IP
- Consider limiting to specific IPs if possible
- Keep password secure

---

## Rollback Procedures

### If Installation Fails
```bash
# Remove package
sudo apt remove shadowsocks-libev

# Remove UFW rules
sudo ufw delete allow 8388/tcp
sudo ufw delete allow 8388/udp
sudo ufw reload
```

### If Service Won't Start
```bash
# Check logs
sudo journalctl -u shadowsocks-libev -n 50

# Check config syntax
sudo shadowsocks-libev -c /etc/shadowsocks-libev/config.json -t

# Remove memory limit if causing issues
sudo systemctl revert shadowsocks-libev
sudo systemctl daemon-reload
```

### If Services Are Disrupted
```bash
# Check all services
sudo systemctl status wg-quick@wg0 nginx gotify unbound sshd

# Restart affected services
sudo systemctl restart <service-name>

# Remove Shadowsocks
sudo systemctl stop shadowsocks-libev
sudo systemctl disable shadowsocks-libev
sudo apt remove shadowsocks-libev
```

---

## Service Compatibility

### WireGuard
- **Impact**: None (different port, different protocol)
- **Verification**: `wg show` to confirm peers still connected

### Nginx
- **Impact**: None (different port)
- **Verification**: `systemctl status nginx`

### Gotify
- **Impact**: None (different port)
- **Verification**: `systemctl status gotify`

### Unbound
- **Impact**: None (different port)
- **Verification**: `systemctl status unbound`

### SSH
- **Impact**: None (different port)
- **Verification**: `systemctl status sshd`

---

## Post-Installation Client Setup

### Client Configuration
Clients will need to:
1. Install Shadowsocks client
2. Configure with server IP, port 8388, password, encryption method
3. Set system proxy to use Shadowsocks
4. Test connection

### WireGuard-over-Shadowsocks (Advanced)
Optionally route WireGuard through Shadowsocks:
- Configure Shadowsocks client on WireGuard peers
- Route WireGuard traffic through Shadowsocks tunnel
- Or use Shadowsocks as primary VPN instead of WireGuard

---

## Success Criteria

- [ ] Shadowsocks package installed successfully
- [ ] Shadowsocks service running on port 8388
- [ ] Memory usage within expected limits (~25MB)
- [ ] All other services (WireGuard, Nginx, Gotify, Unbound, SSH) running normally
- [ ] UFW firewall rules correct
- [ ] No errors in service logs
- [ ] Documentation complete

---

## Estimated Timeline

- **Preparation**: 5 minutes
- **Installation**: 10 minutes
- **Configuration**: 15 minutes
- **Firewall**: 5 minutes
- **Verification**: 10 minutes
- **Documentation**: 15 minutes

**Total**: ~60 minutes

---

## Related Documentation

- **Resource Analysis**: `/home/user/AI_Agents/TRAFFIC_FINGERPRINTING_MITIGATION_RESOURCE_ANALYSIS.md`
- **Phase 1 Status**: `/home/user/AI_Agents/SSH_HARDENING_PHASE1_STATUS.md`
- **System Documentation**: `/home/user/AI_Agents/AGENTS.md`

---

**Last Updated**: 2026-10-06
**Status**: 📋 Ready to proceed
