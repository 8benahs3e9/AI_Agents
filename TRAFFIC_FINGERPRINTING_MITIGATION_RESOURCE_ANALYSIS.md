# Traffic Fingerprinting Mitigation - Resource Analysis

**Server**: et-gtw (Gateway Server)
**Platform**: GCP e2-micro instance
**Resources**: 2 vCPU, 1GB RAM, 10GB disk
**Region**: us-central1-a
**Analysis Date**: 2026-10-06

---

## Current Resource Status

### Memory
- **Total**: 969MB
- **Used**: 481MB (49.6%)
- **Available**: 488MB (50.4%)
- **Swap**: 2GB (79MB used, 1.9GB free)
- **Status**: ✅ Healthy

### Disk
- **Total**: 9.7GB
- **Used**: 7.1GB (78%)
- **Free**: 2.1GB (22%)
- **Inodes**: 18% used (112,786/647,168)
- **Status**: ⚠️ Tight (need to monitor)

### CPU
- **Load Average**: 0.10, 0.07, 0.02 (very low)
- **Current Usage**: ~6.7% system, 46.7% idle
- **Status**: ✅ Healthy

### Services (Memory Limits Applied)
- gotify: 128MB limit
- radicale: 64MB limit
- fail2ban: 64MB limit
- nginx: 64MB limit
- unbound: ~11MB (no limit, but low usage)

### Disk Usage Breakdown
- `/var/log`: 49MB
- `/var/cache/apt/archives`: 16KB (clean)
- Journal logs: 25MB (2-day retention)
- Inodes: 18% used

### Currently Installed Tools
- ✅ WireGuard (already installed)
- ✅ tcpdump (already installed)
- ✅ tc (traffic control, already installed)
- ❌ nmap (not installed)
- ❌ shadowsocks-libev (not installed)
- ❌ wireshark (not installed)

---

## Phase-by-Phase Resource Analysis

### Phase 1: SSH Hardening

**Effort**: Low | **Impact**: Medium | **Risk**: Low

#### Resource Requirements
- **Disk**: ~0KB (config file edits only)
- **Memory**: 0MB (no new services)
- **CPU**: Negligible (config reload only)
- **Installation**: None (editing existing files)

#### Resource Impact
- **Disk**: No change
- **Memory**: No change
- **CPU**: No change (after initial restart)

#### Compatibility Check
- ✅ SSH service already running
- ✅ UFW firewall already configured
- ✅ Configuration file exists: `/etc/ssh/sshd_config`
- ✅ No new packages to install

#### Resource Analysis Result
**Status**: ✅ **SAFE TO IMPLEMENT**

**Rationale**:
- Zero resource overhead
- No new services or packages
- Only configuration changes
- Fits comfortably within current resource limits

**Recommendation**: Proceed immediately

---

### Phase 2: WireGuard Obfuscation (Shadowsocks)

**Effort**: Medium | **Impact**: High | **Risk**: Medium

#### Resource Requirements
- **Disk**: ~200KB (shadowsocks-libev package: 176KB)
- **Memory**: ~20-30MB (shadowsocks-libev service runtime)
- **CPU**: ~2-5% (encryption/decryption overhead)
- **Installation**: shadowsocks-libev package

#### Package Details
- **Package**: shadowsocks-libev
- **Size**: 176KB (download)
- **Dependencies**: libshadowsocks-libev2 (~200KB)
- **Total Disk Impact**: ~400KB (including dependencies)

#### Memory Impact Analysis
- **Current Available**: 488MB
- **Shadowsocks Overhead**: ~25MB
- **After Installation**: ~463MB available
- **Status**: ✅ Sufficient (48% free)

#### CPU Impact Analysis
- **Current Load**: 0.10 (very low)
- **Expected Increase**: +0.05-0.10
- **After Implementation**: ~0.15-0.20
- **Status**: ✅ Acceptable

#### Disk Impact Analysis
- **Current Free**: 2.1GB
- **Package Size**: ~400KB
- **After Installation**: ~2.1GB (negligible change)
- **Status**: ✅ Sufficient

#### Compatibility Check
- ✅ Port 8388 available (not in use)
- ✅ UFW firewall can be updated
- ✅ No conflicting services
- ✅ WireGuard already installed (can be layered)

#### Resource Analysis Result
**Status**: ✅ **SAFE TO IMPLEMENT**

**Rationale**:
- Memory overhead is manageable (25MB out of 488MB available)
- CPU overhead is minimal on low-load system
- Disk impact is negligible (<1MB)
- Fits within current resource limits with comfortable margin

**Recommendation**: Proceed after Phase 1

**Note**: May need to apply memory limit to shadowsocks-libev service similar to other services (e.g., 64MB limit)

---

### Phase 3: Traffic Padding Implementation

**Effort**: Medium-High | **Impact**: High | **Risk**: Low

#### Resource Requirements
- **Disk**: ~1KB (script file)
- **Memory**: ~5-10MB (tc kernel module overhead)
- **CPU**: ~5-10% (packet processing overhead)
- **Bandwidth**: 50-200% increase (dummy traffic)
- **Installation**: None (tc already installed)

#### Memory Impact Analysis
- **Current Available**: 488MB
- **tc Overhead**: ~8MB
- **After Implementation**: ~480MB available
- **Status**: ✅ Sufficient (49% free)

#### CPU Impact Analysis
- **Current Load**: 0.10
- **Expected Increase**: +0.10-0.20
- **After Implementation**: ~0.20-0.30
- **Status**: ✅ Acceptable (still low)

#### Bandwidth Impact Analysis
- **Current Traffic**: 4.2GB received, 19.9GB sent (WireGuard)
- **Padding Overhead**: 50-200%
- **Expected After**: 6.3-12.6GB received, 29.9-59.7GB sent
- **Status**: ⚠️ **SIGNIFICANT BANDWIDTH COST**

**Critical Warning**: This will substantially increase bandwidth usage and potential GCP egress costs.

#### Disk Impact Analysis
- **Current Free**: 2.1GB
- **Script Size**: ~1KB
- **After Implementation**: ~2.1GB (no change)
- **Status**: ✅ Sufficient

#### Compatibility Check
- ✅ tc already installed at `/usr/sbin/tc`
- ✅ iproute2 already installed
- ✅ Kernel supports traffic control
- ✅ No conflicts with existing services

#### Resource Analysis Result
**Status**: ⚠️ **PROCEED WITH CAUTION**

**Rationale**:
- Memory and CPU impact is acceptable
- **Major concern**: Bandwidth overhead (50-200% increase)
- **Cost implication**: Increased GCP egress charges
- **Trade-off**: Security vs cost

**Recommendation**:
1. **Optional for low-budget setup**: Skip if bandwidth costs are concern
2. **Implement if security is priority**: Accept cost increase
3. **Alternative**: Use adaptive padding with lower overhead (30-50%)

**Mitigation**: Start with lower padding rate (50% overhead) and monitor costs

---

### Phase 4: DNS Leak Prevention

**Effort**: Low | **Impact**: Medium | **Risk**: Low

#### Resource Requirements
- **Disk**: ~0KB (config file edits only)
- **Memory**: 0MB (Unbound already running)
- **CPU**: Negligible (config change only)
- **Installation**: None (Unbound already installed)

#### Current DNS Configuration Analysis
**File**: `/etc/unbound/unbound.conf.d/dot-forward.conf`

**Current State**:
- ✅ DNS-over-TLS already configured (Cloudflare + Quad9)
- ✅ DNSSEC validation enabled
- ✅ Privacy features enabled (hide-identity, hide-version)
- ✅ QNAME minimization enabled
- ✅ Caching configured (64MB msg-cache, 128MB rrset-cache)
- ✅ Listening on WireGuard interface (10.100.0.1)
- ✅ Access control for WireGuard subnet (10.100.0.0/24)

#### Resource Impact
- **Disk**: No change
- **Memory**: No change (Unbound already using ~11MB)
- **CPU**: No change
- **Bandwidth**: Negligible (DNS traffic is small)

#### Compatibility Check
- ✅ Unbound already configured for DNS-over-TLS
- ✅ WireGuard already configured to route DNS
- ✅ Only need to add DNS push to WireGuard config
- ✅ No new services or packages

#### Resource Analysis Result
**Status**: ✅ **ALREADY IMPLEMENTED**

**Rationale**:
- DNS-over-TLS is already configured
- DNSSEC validation is enabled
- Privacy features are in place
- Only minor config change needed (add DNS push to WireGuard)

**Recommendation**: Complete as quick config update (no resource impact)

---

### Phase 5: Testing & Validation

**Effort**: Low | **Impact**: Validation | **Risk**: None

#### Resource Requirements
- **Disk**: ~2MB (nmap package: 1.9MB)
- **Memory**: ~50-100MB (during testing only)
- **CPU**: ~10-20% (during testing only)
- **Installation**: nmap package

#### Package Details
- **Package**: nmap
- **Size**: 1.9MB (download)
- **Total Disk Impact**: ~2MB

#### Memory Impact Analysis
- **Current Available**: 488MB
- **nmap Runtime**: ~80MB (during scans only)
- **Peak Usage**: ~400MB available during scan
- **Status**: ✅ Sufficient (41% free during peak)

#### CPU Impact Analysis
- **Current Load**: 0.10
- **During Scan**: +0.15-0.25
- **Peak Load**: ~0.25-0.35
- **Status**: ✅ Acceptable (temporary, short duration)

#### Disk Impact Analysis
- **Current Free**: 2.1GB
- **Package Size**: ~2MB
- **After Installation**: ~2.1GB (negligible change)
- **Status**: ✅ Sufficient

#### Compatibility Check
- ✅ tcpdump already installed
- ✅ tc already installed
- ✅ No conflicts with existing services
- ✅ Testing is temporary (no permanent resource impact)

#### Resource Analysis Result
**Status**: ✅ **SAFE TO IMPLEMENT**

**Rationale**:
- Temporary resource usage only
- nmap package is small (2MB)
- Memory and CPU impact is short-lived
- No permanent resource overhead
- Essential for validation

**Recommendation**: Proceed after Phase 2-4 implementation

**Note**: Testing should be done during low-traffic periods to minimize impact

---

### Phase 6: Multi-Hop Architecture (Optional)

**Effort**: High | **Impact**: Very High | **Risk**: Medium

#### Resource Requirements
- **Disk**: N/A (separate VPS)
- **Memory**: N/A (separate VPS)
- **CPU**: N/A (separate VPS)
- **Cost**: $5-10/month for additional VPS

#### Current Server Impact
- **Disk**: No change (all work on new VPS)
- **Memory**: No change (all work on new VPS)
- **CPU**: No change (all work on new VPS)
- **Bandwidth**: Slight increase (additional hop latency)

#### Resource Analysis Result
**Status**: ⚠️ **REQUIRES ADDITIONAL INFRASTRUCTURE**

**Rationale**:
- Current server (et-gtw) has no resource impact
- Requires provisioning second VPS
- Additional monthly cost ($5-10)
- Additional management overhead
- Additional attack surface (two servers to secure)

**Recommendation**:
- **Skip if budget is concern**: Current mitigations provide good protection
- **Implement if maximum security needed**: Against sophisticated adversaries
- **Consider**: Only after completing Phases 1-5

**Cost-Benefit Analysis**:
- **Cost**: $5-10/month
- **Benefit**: Significant increase in correlation resistance
- **Verdict**: Optional for most threat models

---

### Phase 7: Dynamic Configuration (Optional)

**Effort**: High | **Impact**: Medium-High | **Risk**: Medium

#### Resource Requirements
- **Disk**: ~1KB (script file)
- **Memory**: ~1-2MB (script execution only)
- **CPU**: Negligible (weekly cron job)
- **Installation**: None (using existing tools)

#### Memory Impact Analysis
- **Current Available**: 488MB
- **Script Overhead**: ~2MB (during execution only)
- **Status**: ✅ Negligible

#### CPU Impact Analysis
- **Current Load**: 0.10
- **During Execution**: +0.01-0.02 (weekly, for seconds)
- **Status**: ✅ Negligible

#### Disk Impact Analysis
- **Current Free**: 2.1GB
- **Script Size**: ~1KB
- **Status**: ✅ Negligible

#### Compatibility Check
- ✅ Cron already configured
- ✅ Gotify already running (for notifications)
- ✅ UFW already configured
- ✅ No new services or packages

#### Resource Analysis Result
**Status**: ✅ **SAFE TO IMPLEMENT**

**Rationale**:
- Minimal resource overhead
- One-time script execution weekly
- Uses existing infrastructure (cron, gotify)
- No permanent resource impact
- Low complexity

**Recommendation**:
- **Implement after Phase 2**: To rotate Shadowsocks ports
- **Optional**: Security benefit is moderate
- **Consider**: If threat model includes long-term correlation

**Note**: Requires client-side update mechanism (manual or automated)

---

## Summary Resource Impact

### Cumulative Resource Impact (Phases 1-5)

| Resource | Before | After Phases 1-5 | Change | Status |
|----------|--------|------------------|--------|--------|
| **Memory** | 488MB free | ~400MB free | -88MB | ✅ Sufficient |
| **Disk** | 2.1GB free | ~2.1GB free | -2MB | ✅ Sufficient |
| **CPU Load** | 0.10 | ~0.20-0.30 | +0.10-0.20 | ✅ Acceptable |
| **Bandwidth** | Baseline | +50-200% (if Phase 3) | Significant | ⚠️ Cost concern |

### Phase-by-Phase Resource Table

| Phase | Disk | Memory | CPU | Bandwidth | Cost | Status |
|-------|------|--------|-----|-----------|------|--------|
| 1. SSH Hardening | 0KB | 0MB | 0% | 0% | $0 | ✅ Safe |
| 2. Shadowsocks | 400KB | 25MB | 2-5% | 10-20% | $0 | ✅ Safe |
| 3. Traffic Padding | 1KB | 8MB | 5-10% | 50-200% | $$ | ⚠️ Caution |
| 4. DNS Prevention | 0KB | 0MB | 0% | 0% | $0 | ✅ Done |
| 5. Testing | 2MB | 80MB (temp) | 10-20% (temp) | 0% | $0 | ✅ Safe |
| 6. Multi-Hop | N/A | N/A | N/A | +10% latency | $5-10/mo | ⚠️ New VPS |
| 7. Dynamic Config | 1KB | 2MB (temp) | 1% (temp) | 0% | $0 | ✅ Safe |

---

## Recommendations

### Immediate Implementation (Safe & Low-Cost)
1. **Phase 1**: SSH Hardening (15 min, zero resource impact)
2. **Phase 2**: Shadowsocks Obfuscation (1-2 hours, minimal resource impact)
3. **Phase 4**: DNS Leak Prevention (30 min, already mostly done)
4. **Phase 5**: Testing & Validation (1 hour, temporary resource impact)

**Total Resource Impact**:
- Memory: -25MB (5% of available)
- Disk: -400KB (negligible)
- CPU: +2-5% (acceptable)
- Bandwidth: +10-20% (minimal cost)

### Conditional Implementation (Cost-Benefit Decision)
5. **Phase 3**: Traffic Padding (1-2 hours, 50-200% bandwidth increase)
   - **Recommendation**: Implement only if:
     - Threat model includes sophisticated adversaries
     - Budget allows for increased bandwidth costs
     - Security is higher priority than cost

### Optional Implementation (Advanced Security)
6. **Phase 6**: Multi-Hop Architecture (4-6 hours, $5-10/month)
   - **Recommendation**: Implement only if:
     - Threat model includes nation-state adversaries
     - Maximum anonymity is required
     - Budget allows for additional VPS

7. **Phase 7**: Dynamic Configuration (3-4 hours, minimal resource impact)
   - **Recommendation**: Implement after Phase 2 for additional security
   - Optional: Long-term correlation resistance

---

## Resource Constraints & Warnings

### Critical Constraints
1. **Disk Space**: 78% used (2.1GB free)
   - ✅ Sufficient for Phases 1-5
   - ⚠️ Monitor if adding large packages
   - ✅ Daily cleanup script already in place

2. **Memory**: 49% used (488MB free)
   - ✅ Sufficient for all phases
   - ✅ Swap available (2GB, 79MB used)
   - ⚠️ Monitor if adding memory-intensive services

3. **CPU**: Very low load (0.10)
   - ✅ Plenty of headroom
   - ✅ Can handle additional processing
   - ✅ No immediate concerns

### Bandwidth Cost Warning
- **Phase 3 (Traffic Padding)**: 50-200% bandwidth increase
- **Current Usage**: 4.2GB received, 19.9GB sent (24.1GB total)
- **After Phase 3**: 36-72GB total (at 50-200% overhead)
- **GCP Egress Cost**: ~$0.12/GB (us-central1)
- **Estimated Cost Increase**: $1.44-$5.76/month

**Recommendation**: Monitor bandwidth costs closely after implementing Phase 3

---

## Implementation Priority (Resource-Based)

### Priority 1: No Resource Impact (Do First)
- Phase 1: SSH Hardening
- Phase 4: DNS Leak Prevention (config update only)

### Priority 2: Minimal Resource Impact (Do Second)
- Phase 2: Shadowsocks Obfuscation
- Phase 5: Testing & Validation

### Priority 3: Significant Resource Impact (Do with Caution)
- Phase 3: Traffic Padding (monitor costs)

### Priority 4: Additional Infrastructure (Optional)
- Phase 6: Multi-Hop Architecture (new VPS required)
- Phase 7: Dynamic Configuration (optional enhancement)

---

## Risk Assessment

### Low Risk (Recommended for Implementation)
- Phase 1: SSH Hardening (zero resource impact)
- Phase 4: DNS Leak Prevention (already configured)
- Phase 5: Testing & Validation (temporary impact)
- Phase 7: Dynamic Configuration (minimal impact)

### Medium Risk (Monitor After Implementation)
- Phase 2: Shadowsocks Obfuscation (25MB memory, acceptable)
- Phase 3: Traffic Padding (bandwidth cost increase)

### High Risk (Requires Careful Planning)
- Phase 6: Multi-Hop Architecture (additional cost and complexity)

---

## Conclusion

### Resource Capacity Assessment
**Current server resources are sufficient for Phases 1-5 implementation** with comfortable margins:
- Memory: 488MB available → ~400MB after implementation (41% free)
- Disk: 2.1GB available → ~2.1GB after implementation (21% free)
- CPU: 0.10 load → ~0.20-0.30 after implementation (still low)

### Recommended Implementation Path
1. **Week 1**: Phases 1, 2, 4 (SSH, Shadowsocks, DNS)
2. **Week 2**: Phase 5 (Testing & Validation)
3. **Week 3**: Phase 3 (Traffic Padding) - if budget allows
4. **Optional**: Phases 6-7 (Multi-Hop, Dynamic Config) - based on threat model

### Final Verdict
**✅ The et-gtw server has sufficient resources to implement the core traffic fingerprinting mitigations (Phases 1-5).**

**⚠️ Phase 3 (Traffic Padding) should be implemented with cost monitoring due to bandwidth overhead.**

**ℹ️ Phases 6-7 are optional and should be evaluated based on threat model and budget.**

---

**Document Version**: 1.0
**Last Updated**: 2026-10-06
**Next Review**: After Phase 2 implementation
