# VM Migration Analysis Report

**Date:** 2026-09-20  
**Source:** Google Cloud Platform (GCP)  
**Target:** To be determined  
**Project:** delta-surface-468416-f5  
**Region:** us-central1  
**Zone:** us-central1-a  

---

## Executive Summary

Current infrastructure consists of **2 VM instances** in GCP running Debian 12 (Bookworm):

1. **et-gtw** (Gateway Server) - Fully operational multi-service server
2. **skype** (Asterisk Backend) - Running but with service access issues

The system is well-documented with comprehensive configuration files in the voip-config repository. Migration complexity is **moderate** due to the multi-service nature of the gateway and network dependencies.

---

## Current Infrastructure Overview

### VM Instances

#### et-gtw (Gateway Server)
- **Instance Name:** et-gtw
- **Machine Type:** e2-micro (2 vCPU, 1GB RAM)
- **Internal IP:** 10.128.0.10
- **External IP:** 35.209.115.187
- **Status:** RUNNING
- **Disk:** 10GB persistent disk (79% used - 7.2GB/9.7GB)
- **OS:** Debian 12 Bookworm (Linux 6.1.0-51-cloud-amd64)
- **Last Start:** 2026-08-06T22:21:50.227-07:00
- **IP Forwarding:** Enabled (required for gateway functionality)
- **Tags:** et-gateway, http-server, https-server

#### skype (Asterisk Backend)
- **Instance Name:** skype
- **Machine Type:** e2-micro (2 vCPU, 1GB RAM)
- **Internal IP:** 10.128.0.6
- **External IP:** None (internal only)
- **Status:** RUNNING (service access issues documented)
- **Disk:** 10GB persistent disk
- **OS:** Debian 12 Bookworm
- **Last Start:** 2026-09-01T03:45:19.116-07:00
- **IP Forwarding:** Disabled
- **Tags:** asterisk-backend

---

## Network Configuration

### VPC Network
- **Network Name:** default
- **Subnet Mode:** CUSTOM
- **IPv4 Range:** 10.128.0.0/20
- **BGP Routing Mode:** REGIONAL
- **Stack Type:** IPV4_ONLY

### Key Firewall Rules
| Rule Name | Purpose | Ports | Priority |
|-----------|---------|-------|----------|
| allow-sip-external-to-gateway | SIP/RTP from internet | 5060,5061,10000-20000 | 1000 (DISABLED) |
| allow-wg-vpn-enhanced | WireGuard VPN | 51820/udp | 800 |
| allow-gateway-to-backend-all | Gateway to backend | 80,443,22,3306,5232,5060,5061,10000-20000 | 950 |
| allow-http-internet | HTTP from internet | 80/tcp | 700 |
| allow-https-internet | HTTPS from internet | 443/tcp | 700 |
| allow-ssh-from-iap | SSH via IAP | 22/tcp | 1000 |

### Routing
- **Default Route:** 0.0.0.0/0 → default-internet-gateway (Priority: 1000)
- **Backend Route:** 0.0.0.0/0 → et-gtw instance (Priority: 800)
- **Internal Route:** 10.128.0.0/20 → default (Priority: 0)

---

## Service Architecture

### et-gtw Services (All Operational)
Based on current system analysis:

| Service | Purpose | Status | Memory Usage |
|---------|---------|--------|--------------|
| nginx | Reverse proxy for web services | Active | ~6.5M |
| unbound | DNS resolver with DoT | Active | ~7.1M |
| wireguard (wg-quick@wg0) | VPN server (10.100.0.0/24) | Active | - |
| radicale | CalDAV/CardDAV server | Active | ~17.1M |
| gotify | Notification server | Active | ~15.7M |
| postfix | Mail transport (Gmail relay) | Active | - |
| fail2ban | Intrusion prevention | Active | ~31.8M |
| gateway-health-monitor | Health monitoring | Active | - |

### Virtual Hosts (Nginx)
- **calendar.shatsie.fun** → Radicale (127.0.0.1:5232)
- **connect.shatsie.fun** → Asterisk backend (10.128.0.6:8088)
- **gotify.shatsie.fun** → Gotify (127.0.0.1:8080)

### SSL Certificates
- calendar.shatsie.fun: Valid until 2026-09-17
- connect.shatsie.fun: Valid until 2026-09-18
- gotify.shatsie.fun: Valid until 2026-09-17

### skype Backend Services
- **Asterisk** - SIP/PBX server (documented in voip-config)
- **Internal Extensions:** 1001, 1002 (Linphone)
- **Status:** Network reachable but service access issues documented

---

## Security Configuration

### System-Level Security
- **UFW Firewall:** Active with comprehensive rules
- **Fail2ban:** Active (currently only sshd jail)
- **SSH:** Key-based authentication only
- **Root login:** Disabled on backend
- **Shielded VM:** Integrity monitoring enabled, Secure boot disabled, vTPM enabled

### GCP-Level Security
- **Service Account:** 300834760073-compute@developer.gserviceaccount.com
- **et-gtw Scopes:** Full cloud-platform access
- **skype Scopes:** Limited (storage read-only, logging, monitoring, pubsub, trace)
- **SSH Access:** Restricted to IAP at GCP level

### Security Observations
- **SIP Protection:** Active attack mitigation (~70% packet drop rate)
- **VPN Security:** WireGuard with proper key management
- **DNS Security:** DNS-over-TLS with Cloudflare and Quad9
- **Network Segmentation:** Backend has no external IP

---

## Dependencies and Integrations

### External Dependencies
- **Gmail SMTP** for Postfix relay
- **Cloudflare DNS** (1.1.1.1, 1.0.0.1) and Quad9 (9.9.9.9, 149.112.112.112)
- **SSL Certificates:** Let's Encrypt (auto-renewing via certbot)

### Internal Dependencies
- **Backend Communication:** et-gtw → skype (10.128.0.6) for Asterisk
- **DNS Resolution:** et-gtw provides DNS for VPN and internal networks
- **Network Routing:** Backend internet access via et-gtw

### Data Storage
- **Radicale:** /var/lib/radicale/collections
- **Gotify:** SQLite database at /var/lib/gotify/gotify.db
- **Configuration Files:** Backed up in migration_backups/

---

## Migration Complexity Assessment

### Complexity Level: MODERATE

#### Low Complexity Factors
- ✅ Well-documented configuration in voip-config repository
- ✅ Standard Debian 12 installation
- ✅ Configuration files backed up
- ✅ No custom kernel modifications
- ✅ No containerized services (simplifies migration)

#### Moderate Complexity Factors
- ⚠️ Multi-service gateway (7+ services on single VM)
- ⚠️ Network routing dependencies (backend → gateway)
- ⚠️ VPN configuration with client peers
- ⚠️ SSL certificate management
- ⚠️ DNS configuration with custom zones

#### High Complexity Factors
- ❌ Backend service access issues need resolution
- ❌ GCP-specific integrations (IAP, service accounts)
- ❌ Firewall rule recreation required
- ❌ Network routing reconfiguration

---

## Migration Requirements

### Target Provider Considerations

#### Essential Requirements
1. **2 VM Instances** (or equivalent capacity)
   - Gateway: 2 vCPU, 1GB RAM minimum (e2-micro equivalent)
   - Backend: 2 vCPU, 1GB RAM minimum
2. **10GB Storage** per instance minimum
3. **Static IP Addresses** for gateway (or DNS management)
4. **VPC Network** with custom subnet configuration
5. **Firewall Management** equivalent to GCP rules
6. **Debian 12** or compatible Linux distribution

#### Network Requirements
- **Internal Network:** 10.128.0.0/20 (or equivalent)
- **VPN Support:** UDP port 51820 for WireGuard
- **SIP/RTP Ports:** 5060,5061 (TCP/UDP), 10000-20000 (UDP)
- **Web Ports:** 80, 443 (HTTP/HTTPS)
- **SSH Access:** Port 22 (restrict as needed)

#### Service Requirements
- **DNS Resolution:** Custom DNS server capability
- **SSL Certificates:** Let's Encrypt or equivalent
- **Mail Relay:** SMTP relay service or Gmail integration
- **Monitoring:** Health monitoring capabilities

---

## Migration Strategy Options

### Option 1: Lift and Shift (Recommended)
**Approach:** Migrate VMs as-is with minimal reconfiguration

**Pros:**
- Minimal service disruption
- Preserves existing configuration
- Faster migration timeline
- Lower risk of configuration errors

**Cons:**
- May not optimize for target provider
- GCP-specific features may need replacement
- Potential performance differences

**Timeline:** 2-3 days

### Option 2: Re-architecture
**Approach:** Redesign architecture for target provider

**Pros:**
- Optimized for target provider
- Opportunity to address known issues
- Potential cost/performance improvements

**Cons:**
- Higher complexity and risk
- Longer migration timeline
- More testing required

**Timeline:** 1-2 weeks

### Option 3: Hybrid Approach
**Approach:** Migrate gateway first, then backend with improvements

**Pros:**
- Balanced risk and optimization
- Phased migration reduces disruption
- Can test and learn during migration

**Cons:**
- Longer overall timeline
- Temporary architecture complexity

**Timeline:** 1 week

---

## Critical Migration Points

### Pre-Migration Checklist
- [ ] Resolve backend service access issues
- [ ] Verify all SSL certificates are current
- [ ] Test backup restoration procedures
- [ ] Document current firewall rules completely
- [ ] Verify DNS configuration accuracy
- [ ] Test VPN client connectivity
- [ ] Backup all configuration files
- [ ] Document all service dependencies

### Migration Risk Factors
1. **Network Routing Complexity:** Backend depends on gateway for internet access
2. **VPN Client Configuration:** 2 active peers need reconfiguration
3. **DNS Dependencies:** Custom DNS zones and resolution
4. **SSL Certificate Transfer:** Certificate migration and renewal setup
5. **Service Account Migration:** GCP service account replacement
6. **Firewall Rule Recreation:** Complex rule set needs accurate recreation

### Rollback Plan
- Keep GCP instances running until migration verified
- Maintain DNS failover capability
- Document rollback procedures for each service
- Test rollback procedures before migration

---

## Data Migration Requirements

### Configuration Files (Already Backed Up)
- `/etc/nginx/` - Reverse proxy configuration
- `/etc/unbound/` - DNS resolver configuration
- `/etc/wireguard/` - VPN configuration
- `/etc/radicale/` - CalDAV server configuration
- `/etc/postfix/` - Mail transport configuration

### Application Data
- **Radicale:** /var/lib/radicale/collections (calendar/contact data)
- **Gotify:** /var/lib/gotify/gotify.db (notification data)
- **Asterisk:** Configuration and call recordings (if any)

### System Data
- User accounts and SSH keys
- Cron jobs and scheduled tasks
- System certificates and keys
- Log files (for debugging reference)

---

## Post-Migration Validation

### Service Validation Checklist
- [ ] All gateway services operational
- [ ] Backend services accessible
- [ ] VPN clients can connect
- [ ] DNS resolution working correctly
- [ ] Web services accessible via SSL
- [ ] Mail delivery functional
- [ ] Internal network routing operational
- [ ] Security measures active (UFW, Fail2ban)

### Performance Validation
- [ ] Network latency acceptable
- [ ] Service response times acceptable
- [ ] Resource utilization within limits
- [ ] Backup procedures functional

### Security Validation
- [ ] Firewall rules correctly implemented
- [ ] SSH access properly restricted
- [ ] SSL certificates valid and auto-renewing
- [ ] VPN encryption operational
- [ ] DNS resolution secure (DoT)

---

## Cost Considerations

### Current GCP Costs (Estimated)
- **e2-micro instances:** ~$6-8/month each
- **Storage:** ~$0.40/month per 10GB
- **Network:** Variable based on usage
- **Total Estimated:** ~$15-25/month

### Target Provider Cost Factors
- Instance pricing differences
- Storage pricing differences
- Network transfer costs
- Additional service costs (load balancers, etc.)
- Potential cost optimization opportunities

---

## Recommendations

### Immediate Actions
1. **Resolve Backend Issues:** Address skype service access problems before migration
2. **Complete Documentation:** Ensure all configuration is documented
3. **Test Backups:** Verify backup restoration procedures
4. **Choose Target Provider:** Select destination provider based on requirements

### Migration Planning
1. **Choose Migration Strategy:** Lift and shift recommended for speed
2. **Create Detailed Timeline:** Plan each migration phase
3. **Prepare Target Environment:** Set up target infrastructure
4. **Test Migration Process:** Dry run with non-production data

### Post-Migration
1. **Monitor Performance:** Close monitoring after migration
2. **Optimize Configuration:** Tune for target provider
3. **Update Documentation:** Reflect new environment
4. **Decommission GCP:** Only after full validation

---

## Next Steps

1. **Select Target Provider** based on requirements and cost analysis
2. **Resolve Backend Service Issues** to ensure clean migration
3. **Create Detailed Migration Plan** with timelines and checkpoints
4. **Set Up Target Environment** in chosen provider
5. **Execute Migration** following chosen strategy
6. **Validate and Optimize** post-migration configuration

---

**Analysis Completed:** 2026-09-20  
**Analyst:** Devin AI System  
**Status:** Ready for migration planning phase  
**Confidence Level:** High (comprehensive documentation available)