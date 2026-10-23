# Phase 5: Testing & Validation - Implementation Plan

**Date**: 2026-10-07
**Server**: et-gtw (Gateway Server)
**Status**: 📋 Planning
**Effort**: Low (30-45 minutes)
**Impact**: Validation only (no configuration changes)

---

## Testing Objectives

1. Verify Shadowsocks server is accessible and functional
2. Verify DNS leak prevention is working
3. Verify WireGuard is functioning correctly
4. Verify all services are running normally
5. Measure current security posture
6. Document test results

---

## Test Plan

### Test 1: Shadowsocks Server Connectivity
**Objective**: Verify Shadowsocks server is listening and accessible

**Steps**:
1. Check Shadowsocks service status
2. Verify port 8388 is listening
3. Test local connectivity to Shadowsocks
4. Check Shadowsocks logs for errors

**Expected Results**:
- Service: Active (running)
- Port 8388: Listening (TCP and UDP)
- No errors in logs

---

### Test 2: DNS Leak Prevention
**Objective**: Verify DNS queries are encrypted and don't leak

**Steps**:
1. Test DNS resolution via Unbound (10.100.0.1)
2. Verify Unbound is using DNS-over-TLS
3. Check Unbound logs for TLS connections
4. Verify DNSSEC validation is working

**Expected Results**:
- DNS resolution: Working
- DNS-over-TLS: Active
- DNSSEC: Enabled
- No DNS leaks

---

### Test 3: WireGuard Functionality
**Objective**: Verify WireGuard is functioning correctly

**Steps**:
1. Check WireGuard interface status
2. Verify peer connections
3. Check transfer statistics
4. Verify iptables rules are correct

**Expected Results**:
- Interface: Up (wg0)
- Peers: Connected (Linux Mint)
- Transfer: Active
- iptables: Rules present

---

### Test 4: Service Health Check
**Objective**: Verify all services are running normally

**Steps**:
1. Check WireGuard service
2. Check Shadowsocks service
3. Check Unbound service
4. Check Nginx service
5. Check Gotify service
6. Check SSH service

**Expected Results**:
- All services: Active (running)
- No errors in logs
- Normal resource usage

---

### Test 5: Resource Usage
**Objective**: Verify resource usage is within limits

**Steps**:
1. Check memory usage
2. Check disk usage
3. Check CPU load
4. Check swap usage

**Expected Results**:
- Memory: < 600MB used
- Disk: < 80% used
- CPU: < 50% load
- Swap: < 100MB used

---

### Test 6: Network Connectivity
**Objective**: Verify network connectivity is correct

**Steps**:
1. Check external connectivity (ping)
2. Check DNS resolution
3. Check firewall rules
4. Check port accessibility

**Expected Results**:
- External connectivity: Working
- DNS resolution: Working
- Firewall: Rules correct
- Ports: Accessible as configured

---

## Test Execution Plan

### Order of Tests
1. Service Health Check (baseline)
2. Resource Usage (baseline)
3. Shadowsocks Connectivity
4. DNS Leak Prevention
5. WireGuard Functionality
6. Network Connectivity

### Risk Assessment
- **Risk**: None (read-only tests)
- **Service Impact**: None
- **Configuration Changes**: None
- **Rollback**: Not needed

---

## Success Criteria

- [ ] Shadowsocks service active and listening on port 8388
- [ ] DNS resolution working via 10.100.0.1
- [ ] DNS-over-TLS active (Cloudflare/Quad9)
- [ ] WireGuard interface up and peers connected
- [ ] All services running normally
- [ ] Resource usage within limits
- [ ] Network connectivity working
- [ ] No errors in logs
- [ ] Documentation complete

---

## Timeline

- **Service Health Check**: 5 minutes
- **Resource Usage**: 2 minutes
- **Shadowsocks Connectivity**: 5 minutes
- **DNS Leak Prevention**: 10 minutes
- **WireGuard Functionality**: 5 minutes
- **Network Connectivity**: 5 minutes
- **Documentation**: 10 minutes

**Total**: ~40 minutes

---

## Related Documentation

- **Phase 1 Status**: `/home/user/AI_Agents/SSH_HARDENING_PHASE1_STATUS.md`
- **Phase 2 Status**: `/home/user/AI_Agents/SHADOWSOCKS_PHASE2_STATUS.md`
- **Phase 4 Status**: `/home/user/AI_Agents/DNS_LEAK_PREVENTION_PHASE4_STATUS.md`
- **Client Setup**: `/home/user/AI_Agents/SHADOWSOCKS_CLIENT_SETUP_GUIDE.md`
- **Resource Analysis**: `/home/user/AI_Agents/TRAFFIC_FINGERPRINTING_MITIGATION_RESOURCE_ANALYSIS.md`
- **System Documentation**: `/home/user/AI_Agents/AGENTS.md`

---

**Last Updated**: 2026-10-07
**Status**: 📋 Ready to proceed
