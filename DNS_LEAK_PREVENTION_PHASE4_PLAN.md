# Phase 4: DNS Leak Prevention - Implementation Plan

**Date**: 2026-10-07
**Server**: et-gtw (Gateway Server)
**Status**: 📋 Planning
**Effort**: Low (10-15 minutes)
**Impact**: Medium (ensures DNS queries go through encrypted tunnel)

---

## Current DNS Configuration Status

### Unbound DNS Server
**File**: `/etc/unbound/unbound.conf.d/dot-forward.conf`

**Current Configuration**:
- ✅ DNS-over-TLS enabled (forward-tls-upstream: yes)
- ✅ Upstream: Cloudflare (1.1.1.1@853, 1.0.0.1@853)
- ✅ Backup: Quad9 (9.9.9.9@853, 149.112.112.112@853)
- ✅ Listening on: 127.0.0.1, 10.100.0.1, 10.128.0.10
- ✅ Access control: WireGuard subnet (10.100.0.0/24) allowed
- ✅ DNSSEC validation enabled
- ✅ QNAME minimization enabled
- ✅ Privacy features enabled (hide-identity, hide-version)

**Status**: ✅ **DNS-over-TLS ALREADY CONFIGURED**

### WireGuard Configuration
**File**: `/etc/wireguard/wg0.conf`

**Current State**:
- Server IP: 10.100.0.1
- Peer 1 (Android): 10.100.0.2
- Peer 2 (Linux Mint): 10.100.0.3
- **DNS Push**: ❌ NOT CONFIGURED

**Issue**: WireGuard clients may not be using server's DNS, potentially leaking DNS queries outside the VPN tunnel.

---

## Implementation Plan

### Step 1: Backup Current Configuration
- [ ] Backup WireGuard configuration
- [ ] Document current DNS routing

### Step 2: Add DNS Push to WireGuard Peers
- [ ] Add `DNS = 10.100.0.1` to Android peer
- [ ] Add `DNS = 10.100.0.1` to Linux Mint peer
- [ ] This tells clients to use 10.100.0.1 as their DNS server

### Step 3: Reload WireGuard Configuration
- [ ] Reload WireGuard without disconnecting peers
- [ ] Verify peers remain connected
- [ ] Check handshake times

### Step 4: Verify DNS Routing
- [ ] Test DNS resolution from server
- [ ] Verify Unbound is forwarding through DNS-over-TLS
- [ ] Check DNS queries are encrypted

### Step 5: Client-Side Verification (Optional)
- [ ] Document how clients can verify DNS routing
- [ ] Provide DNS leak test instructions

### Step 6: Service Verification
- [ ] Verify WireGuard still active
- [ ] Verify Unbound still active
- [ ] Verify other services (Nginx, Gotify, SSH, Shadowsocks) still running

### Step 7: Documentation
- [ ] Document changes made
- [ ] Update AGENTS.md
- [ ] Create rollback procedures

---

## Detailed Configuration Changes

### WireGuard Configuration Changes

**Current**: `/etc/wireguard/wg0.conf`
```ini
[Peer]
# Android Client
PublicKey = A7NoBoK8HQjV2NAWp8HCpyJUkX9vQVfOuTe8pe38JBI=
AllowedIPs = 10.100.0.2/32
PersistentKeepalive = 25

[Peer]
# Linux Mint Client
PublicKey = 5QmboH9IcWnGi6UP76WF4N2xw9286pGa+6nmo2UBqAw=
AllowedIPs = 10.100.0.3/32
PersistentKeepalive = 25
```

**After**:
```ini
[Peer]
# Android Client
PublicKey = A7NoBoK8HQjV2NAWp8HCpyJUkX9vQVfOuTe8pe38JBI=
AllowedIPs = 10.100.0.2/32
DNS = 10.100.0.1
PersistentKeepalive = 25

[Peer]
# Linux Mint Client
PublicKey = 5QmboH9IcWnGi6UP76WF4N2xw9286pGa+6nmo2UBqAw=
AllowedIPs = 10.100.0.3/32
DNS = 10.100.0.1
PersistentKeepalive = 25
```

### DNS Flow After Configuration

```
Client → WireGuard → 10.100.0.1 (Unbound) → DNS-over-TLS → Cloudflare/Quad9
```

**Benefits**:
- DNS queries encrypted via DNS-over-TLS
- DNS queries go through VPN tunnel
- No DNS leaks to ISP
- DNSSEC validation at Unbound level

---

## Resource Impact

### Disk
- **Impact**: 0KB (config file edit only)
- **Status**: ✅ Negligible

### Memory
- **Impact**: 0MB (no new services)
- **Status**: ✅ Negligible

### CPU
- **Impact**: Negligible (DNS resolution already happening)
- **Status**: ✅ Negligible

### Bandwidth
- **Impact**: Negligible (DNS queries are small)
- **Status**: ✅ Negligible

---

## Rollback Procedures

### If DNS Issues Occur

**Option 1: Remove DNS Push**
```bash
# Edit WireGuard config
sudo nano /etc/wireguard/wg0.conf
# Remove "DNS = 10.100.0.1" lines

# Reload WireGuard
sudo wg-quick down wg0
sudo wg-quick up wg0
```

**Option 2: Restore Backup**
```bash
# Restore from backup
sudo cp /etc/wireguard/wg0.conf.backup /etc/wireguard/wg0.conf

# Reload WireGuard
sudo wg-quick down wg0
sudo wg-quick up wg0
```

### If WireGuard Disconnects Peers
```bash
# Check status
sudo wg show

# Restart WireGuard
sudo systemctl restart wg-quick@wg0

# Check logs
sudo journalctl -u wg-quick@wg0 -n 50
```

---

## Service Compatibility

### WireGuard
- **Impact**: Minimal (config change only)
- **Risk**: Low (peers may briefly reconnect)
- **Mitigation**: Use `wg syncconf` for seamless reload (if available)

### Unbound
- **Impact**: None (configuration unchanged)
- **Risk**: None
- **Status**: Already configured correctly

### Other Services
- **Nginx**: No impact
- **Gotify**: No impact
- **SSH**: No impact
- **Shadowsocks**: No impact

---

## Verification Steps

### Server-Side Verification

**Test DNS Resolution**:
```bash
# Test from server
nslookup google.com 10.100.0.1

# Should return results from Unbound
```

**Verify DNS-over-TLS**:
```bash
# Check Unbound logs
sudo journalctl -u unbound -n 20

# Look for TLS connections to upstream
```

**Verify WireGuard Peers**:
```bash
# Check peer status
sudo wg show

# Peers should remain connected
# Handshake times should be recent
```

### Client-Side Verification (Optional)

**WireGuard Clients**:
After WireGuard reload, clients should automatically:
1. Use 10.100.0.1 as DNS server
2. DNS queries go through VPN tunnel
3. DNS queries encrypted via DNS-over-TLS

**Test DNS Leak**:
- Visit: https://dnsleaktest.com
- All DNS servers should show VPN IP
- No ISP DNS servers should appear

**Test DNS Resolution**:
```bash
# From client
nslookup google.com

# Should resolve correctly
```

---

## Success Criteria

- [ ] WireGuard configuration updated with DNS push
- [ ] WireGuard reloaded without disconnecting peers
- [ ] Peers remain connected (handshake < 2 minutes)
- [ ] DNS resolution works correctly
- [ ] DNS queries go through 10.100.0.1
- [ ] Unbound still forwarding via DNS-over-TLS
- [ ] All other services running normally
- [ ] Documentation complete

---

## Timeline

- **Preparation**: 2 minutes
- **Backup**: 1 minute
- **Configuration**: 2 minutes
- **Reload**: 1 minute
- **Verification**: 5 minutes
- **Documentation**: 5 minutes

**Total**: ~15 minutes

---

## Related Documentation

- **Resource Analysis**: `/home/user/AI_Agents/TRAFFIC_FINGERPRINTING_MITIGATION_RESOURCE_ANALYSIS.md`
- **Phase 1 Status**: `/home/user/AI_Agents/SSH_HARDENING_PHASE1_STATUS.md`
- **Phase 2 Status**: `/home/user/AI_Agents/SHADOWSOCKS_PHASE2_STATUS.md`
- **Client Setup**: `/home/user/AI_Agents/SHADOWSOCKS_CLIENT_SETUP_GUIDE.md`
- **System Documentation**: `/home/user/AI_Agents/AGENTS.md`

---

**Last Updated**: 2026-10-07
**Status**: 📋 Ready to proceed
