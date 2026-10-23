# Shadowsocks Misidentification Analysis

**Date**: 2026-10-08
**Purpose**: Analyze why Shadowsocks was initially misidentified as a manual process

---

## The Error

### Initial Incorrect Conclusion
I incorrectly concluded that Shadowsocks was:
1. Disabled/inactive
2. Running as a manual process (not systemd-managed)
3. Stopped on Oct 08 05:14 UTC

### Actual Reality
Shadowsocks IS:
1. Active and running
2. Managed by systemd service `shadowsocks-v2ray-ws.service`
3. Started on 2026-10-07 12:03:54 UTC (23+ hours ago)

---

## Root Cause Analysis

### Why the Error Occurred

#### Step 1: Wrong Service Name Assumption
**What I Did**:
```bash
systemctl status shadowsocks-libev
```

**What I Expected**:
- This to be the Shadowsocks service

**What Actually Happened**:
- `shadowsocks-libev.service` was the OLD service name from Phase 2
- The actual service is `shadowsocks-v2ray-ws.service`
- I never checked for other Shadowsocks-related services

**Error**: Assumed the service name from Phase 2 documentation was still current

---

#### Step 2: Port Check on Wrong Port
**What I Did**:
```bash
sudo ss -tunp | grep 8388
```

**What I Expected**:
- To see Shadowsocks connections on port 888

**What Actually Happened**:
- Port 8388 is from the OLD configuration
- The NEW configuration uses port 10000 (localhost only)
- No connections on port 8388

**Error**: Checked for the old port, not the new port

---

#### Step 3: Process Check Revealed Different Configuration
**What I Did**:
```bash
ps aux | grep ss-server
```

**What I Found**:
```
/usr/bin/ss-server -c /etc/shadowsocks-libev/config.json -s 127.0.0.1 -p 10000 --plugin ss-v2ray-plugin --plugin-opts server;mode=websocket;path=/assets/telemetry/ws-7f3a91c2
```

**What I Concluded**:
- This is a manual process (because it wasn't the service I expected)
- Started outside systemd

**What I Should Have Concluded**:
- This is a different service with different command-line arguments
- Need to find which systemd service manages this process
- Check `systemctl list-units --all | grep shadowsocks`

**Error**: Assumed manual process because it didn't match my expected service

---

#### Step 4: Failed to Check for All Shadowsocks Services
**What I Should Have Done**:
```bash
systemctl list-units --all | grep shadowsocks
```

**What This Would Have Shown**:
```
shadowsocks-v2ray-ws.service loaded active running
```

**What I Actually Did**:
- Never ran this command
- Assumed only `shadowsocks-libev.service` existed

**Error**: Failed to discover the actual service name

---

## Why This Happened

### Documentation Lag
- Phase 2 documentation referenced `shadowsocks-libev.service`
- User upgraded to `shadowsocks-v2ray-ws.service` without updating documentation
- I relied on outdated documentation

### Confirmation Bias
- When I saw `shadowsocks-libev.service` was disabled, I confirmed my initial assumption
- I didn't seek evidence that could contradict my conclusion
- I saw authentication errors and assumed they meant the service failed

### Narrow Search Scope
- I only checked for what I expected (port 8388, service name from docs)
- I didn't check for alternatives (other ports, other service names)
- I didn't verify with `systemctl list-units --all`

### Process vs Service Confusion
- When I saw the process running, I assumed it was manual
- I didn't check which service manages the process
- I didn't verify the process PID against systemd services

---

## Lessons Learned

### 1. Always Verify Service Names
**Before**: Assume service name from documentation is current
**After**: Always run `systemctl list-units --all | grep <keyword>` to find actual service names

### 2. Check for Alternative Configurations
**Before**: Check only the documented port/service
**After**: Check for all ports and all related services

### 3. Corroborate Process Information
**Before**: Assume running process = manual
**After**: Check `systemctl status <pid>` or `systemctl status <service>` to verify which service manages the process

### 4. Don't Assume Documentation is Current
**Before**: Trust documentation as up-to-date
**After**: Treat documentation as potentially outdated, verify current state

### 5. Use Multiple Verification Methods
**Before**: Single method (systemctl status)
**After**: Multiple methods (systemctl, ps, ss, netstat)

---

## Correct Verification Process

### What I Should Have Done

```bash
# Step 1: Check for all Shadowsocks-related services
systemctl list-units --all | grep shadowsocks

# Step 2: Check status of each service found
systemctl status shadowsocks-v2ray-ws.service

# Step 3: Check what's listening on all ports
sudo ss -tunp

# Step 4: Verify process belongs to service
ps aux | grep ss-server
# Note PID, then check:
systemctl status <pid>

# Step 5: Check nginx configuration for proxy rules
nginx -T | grep -A 10 -B 5 shadowsocks
```

---

## Timeline of Error

1. **12:03:54 UTC (Oct 07)**: shadowsocks-v2ray-ws.service started
2. **05:04:19 UTC (Oct 08)**: Authentication errors on 87.151.163.150
3. **05:14:29 UTC (Oct 08)**: shadowsocks-libev.service stopped (old service)
4. **11:30 UTC (Oct 08)**: I began analysis
5. **11:30-11:35**: I checked wrong service name
6. **11:35-11:40**: I checked wrong port (8388)
7. **11:40-11:45**: I found process, assumed manual
8. **11:45-12:00**: Created incorrect analysis documents
9. **11:40-11:45**: User corrected me
10. **11:45-12:00**: I discovered actual service name

---

## Impact

### Documentation Created (Incorrect)
- CONFIGURATION_CHANGE_ANALYSIS_2026-10-08.md (incorrect)
- DOCUMENTATION_CONSOLIDATION_2026-10-08.md (based on incorrect analysis)
- NEXT_STEPS_PLAN_2026-10-08.md (based on incorrect analysis)

### Documentation Created (Correct)
- SHADOWSOCKS_CORRECTION_2026-10-08.md (correction of error)
- SHADOWSOCKS_V2RAY_INTEGRATION_2026-10-08.md (actual configuration)
- AGENTS.md (updated with correct configuration)

### Client Impact
- No client impact (server continued running correctly)
- No service disruption
- Security posture was actually BETTER than I reported

---

## System Design Analysis

### Why User Changed Configuration

### From Simple Shadowsocks to V2Ray + Nginx

**Possible Reasons**:
1. **Better Obfuscation**: V2Ray + WebSocket is harder to fingerprint
2. **TLS Termination**: Nginx handles TLS, certificates, and HTTP/HTTPS
3. **Path-Based Access**: Additional filtering capability
4. **Localhost Binding**: Not directly accessible externally
5. **Integration**: Leverages existing Nginx infrastructure

### Authentication Errors on Oct 08

**Logs Showed**:
```
failed to handshake with 87.151.163.150: authentication error
```

**Likely Cause**:
- Client was trying to connect using OLD configuration (port 8388, no V2Ray)
- Server had already migrated to V2Ray + WebSocket
- Client credentials didn't match new configuration
- This caused the OLD service (shadowsocks-libev.service) to be stopped

**Correct Action**:
- Stop old service
- Keep new service running
- Reconfigure clients to use new configuration

---

## Service Management Best Practices

### For This System

**Current State**:
- OLD service: `shadowsocks-libev.service` (disabled/stopped)
- NEW service: `shadowsocks-v2ray-ws.service` (active/running)
- Config file: `/etc/shadowsocks-libev/config.json` (still references old port)

**Recommendation**:
1. Remove old service file: `/etc/systemd/system/shadowsocks-libev.service` (doesn't exist - was never a systemd file)
2. Archive old documentation
3. Update config file to match actual usage (port 10000, localhost)
4. Document service migration

### For Future Changes

**When Upgrading Services**:
1. Create new service file with different name (e.g., shadowsocks-v2ray-ws.service)
2. Keep old service until new one is verified
3. Update documentation immediately
4. Remove old service after migration complete
5. Remove old systemd files

**When Investigating Services**:
1. Always use `systemctl list-units --all | grep <keyword>`
2. Check all ports, not just documented ones
3. Verify process belongs to which service
4. Use multiple verification methods
5. Don't assume documentation is current

---

## Conclusion

### The Error Was Due To:
1. **Outdated documentation** - Service name changed but docs not updated
2. **Narrow search scope** - Only checked for expected service/port
3. **Confirmation bias** - Confirmed assumptions instead of seeking disconfirming evidence
4. **Lack of verification** - Didn't check for alternative services or processes

### The System Is Actually:
- **Better secured** than the original design
- **More sophisticated** (V2Ray + Nginx integration)
- **Actively running** (not manual process)
- **Correctly managed** by systemd

### Documentation Is Now:
- **Corrected** to reflect actual V2Ray + Nginx configuration
- **Updated** with proper service name and configuration
- **Consolidated** with historical docs marked as superseded

---

**Last Updated**: 2026-10-08
**Status**: ✅ Analysis Complete
**Lesson**: Always verify with multiple methods, don't assume documentation is current
