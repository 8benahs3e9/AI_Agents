# VM Migration Checklist

**Project:** delta-surface-468416-f5 Migration  
**Source:** Google Cloud Platform (us-central1-a)  
**Target:** TBD  
**Created:** 2026-09-20  

---

## Phase 1: Pre-Migration Preparation

### Environment Assessment
- [ ] Review migration analysis document
- [ ] Select target cloud provider
- [ ] Choose migration strategy (Lift and Shift recommended)
- [ ] Define migration timeline and milestones
- [ ] Identify migration team and responsibilities

### Current State Validation
- [ ] Verify et-gtw gateway services operational
- [ ] Resolve skype backend service access issues
- [ ] Test VPN client connectivity (2 peers)
- [ ] Verify SSL certificate validity and renewal
- [ ] Test DNS resolution (internal and external)
- [ ] Validate network routing (gateway ↔ backend)
- [ ] Check disk space and resource utilization
- [ ] Verify all configuration files documented

### Backup Preparation
- [ ] Verify gateway_configs.tar.gz backup integrity
- [ ] Backup application data (Radicale, Gotify, Asterisk)
- [ ] Backup SSL certificates and keys
- [ ] Backup SSH keys and authorized_keys
- [ ] Document backup locations and restoration procedures
- [ ] Test backup restoration on non-production system

### Target Environment Setup
- [ ] Create account with target provider
- [ ] Set up billing and cost controls
- [ ] Configure network (VPC, subnets, routing)
- [ ] Set up firewall rules equivalent to GCP
- [ ] Configure DNS (if using provider DNS)
- [ ] Prepare SSH keys and access controls

---

## Phase 2: Infrastructure Migration

### Network Configuration
- [ ] Create VPC network (10.128.0.0/20 or equivalent)
- [ ] Configure subnet with appropriate CIDR range
- [ ] Set up routing tables (default route, backend route)
- [ ] Configure firewall rules:
  - [ ] HTTP/HTTPS (80, 443) from internet
  - [ ] WireGuard VPN (51820/udp)
  - [ ] SSH (22) restricted access
  - [ ] SIP/RTP (5060,5061,10000-20000) if needed
  - [ ] Internal network communication
- [ ] Configure static IP for gateway (or DNS setup)
- [ ] Test network connectivity

### Instance Creation
- [ ] Create gateway VM (2 vCPU, 1GB RAM, 10GB disk)
- [ ] Create backend VM (2 vCPU, 1GB RAM, 10GB disk)
- [ ] Install Debian 12 (or compatible OS)
- [ ] Configure SSH access
- [ ] Set up hostnames (et-gtw, skype)
- [ ] Configure internal IP addresses
- [ ] Configure external IP for gateway
- [ ] Verify instance connectivity

---

## Phase 3: Gateway Migration (et-gtw)

### OS Configuration
- [ ] Update system packages
- [ ] Configure system settings (timezone, locale)
- [ ] Create user accounts (matching current setup)
- [ ] Configure SSH keys and access
- [ ] Set up firewall (UFW) with current rules
- [ ] Configure time synchronization

### Service Installation
- [ ] Install and configure Nginx
- [ ] Install and configure Unbound DNS
- [ ] Install and configure WireGuard
- [ ] Install and configure Radicale
- [ ] Install and configure Gotify
- [ ] Install and configure Postfix
- [ ] Install and configure Fail2ban
- [ ] Install health monitoring scripts

### Configuration Restoration
- [ ] Restore Nginx configuration from backup
- [ ] Restore Unbound configuration from backup
- [ ] Restore WireGuard configuration from backup
- [ ] Restore Radicale configuration from backup
- [ ] Restore Postfix configuration from backup
- [ ] Restore SSL certificates and keys
- [ ] Update configuration with new IP addresses if needed

### Application Data Migration
- [ ] Migrate Radicale collections (/var/lib/radicale/collections)
- [ ] Migrate Gotify database (/var/lib/gotify/gotify.db)
- [ ] Migrate any other application data
- [ ] Verify data integrity
- [ ] Test application functionality

### SSL Certificate Setup
- [ ] Install Let's Encrypt certbot
- [ ] Configure DNS for certificate validation
- [ ] Request SSL certificates for domains:
  - [ ] calendar.shatsie.fun
  - [ ] connect.shatsie.fun
  - [ ] gotify.shatsie.fun
- [ ] Configure auto-renewal
- [ ] Test SSL certificate validity

### Service Testing
- [ ] Test Nginx reverse proxy functionality
- [ ] Test DNS resolution (internal and external)
- [ ] Test WireGuard VPN connectivity
- [ ] Test Radicale CalDAV/CardDAV access
- [ ] Test Gotify notification system
- [ ] Test Postfix mail delivery
- [ ] Test Fail2ban functionality
- [ ] Test health monitoring

---

## Phase 4: Backend Migration (skype)

### OS Configuration
- [ ] Update system packages
- [ ] Configure system settings
- [ ] Create user accounts
- [ ] Configure SSH access
- [ ] Set up firewall rules
- [ ] Configure network routing via gateway

### Asterisk Installation
- [ ] Install Asterisk and dependencies
- [ ] Restore Asterisk configuration from voip-config
- [ ] Configure PJSIP endpoints
- [ ] Configure internal extensions (1001, 1002)
- [ ] Configure any SIP trunks if needed
- [ ] Set up RTP ports and security

### Application Data Migration
- [ ] Migrate Asterisk configuration files
- [ ] Migrate any voicemail or call recordings
- [ ] Migrate any other Asterisk data
- [ ] Verify data integrity

### Network Configuration
- [ ] Configure internal IP (10.128.0.6 or equivalent)
- [ ] Set up routing via gateway for internet access
- [ ] Configure firewall rules for SIP/RTP
- [ ] Test connectivity to gateway
- [ ] Test internet access via gateway

### Service Testing
- [ ] Test Asterisk service status
- [ ] Test SIP registration for extensions
- [ ] Test internal calling between extensions
- [ ] Test any external SIP trunks
- [ ] Test audio/rtp functionality
- [ ] Verify fail2ban for Asterisk

---

## Phase 5: Integration Testing

### Network Integration
- [ ] Test gateway ↔ backend communication
- [ ] Test backend internet access via gateway
- [ ] Test VPN client access to internal network
- [ ] Test DNS resolution for all services
- [ ] Test firewall rules effectiveness

### Service Integration
- [ ] Test web services via Nginx reverse proxy
- [ ] Test Asterisk backend access via connect.shatsie.fun
- [ ] Test calendar service via calendar.shatsie.fun
- [ ] Test notification service via gotify.shatsie.fun
- [ ] Test mail delivery via Postfix

### Security Validation
- [ ] Verify SSH access restrictions
- [ ] Test firewall rule effectiveness
- [ ] Verify SSL certificate validity
- [ ] Test VPN encryption
- [ ] Test DNS-over-TLS functionality
- [ ] Verify Fail2ban operational

### Performance Testing
- [ ] Test service response times
- [ ] Monitor resource utilization
- [ ] Test network latency
- [ ] Verify backup/restore procedures
- [ ] Test monitoring and alerting

---

## Phase 6: DNS and External Services

### DNS Configuration
- [ ] Update DNS records for gateway IP
- [ ] Update DNS records for services:
  - [ ] calendar.shatsie.fun
  - [ ] connect.shatsie.fun
  - [ ] gotify.shatsie.fun
- [ ] Configure DNS TTL for smooth transition
- [ ] Test DNS propagation
- [ ] Verify SSL certificates work with new DNS

### External Service Integration
- [ ] Update Gmail SMTP relay configuration if needed
- [ ] Update any external API integrations
- [ ] Update monitoring service endpoints
- [ ] Update any webhooks or callbacks
- [ ] Test all external integrations

### Client Configuration Updates
- [ ] Update VPN client configurations (2 peers)
- [ ] Update SIP client configurations (extensions)
- [ ] Update calendar client configurations
- [ ] Update any other client configurations
- [ ] Communicate changes to users

---

## Phase 7: Cutover and Validation

### Pre-Cutover Final Checks
- [ ] Final backup of both source and target
- [ ] Verify all services operational on target
- [ ] Verify all testing completed successfully
- [ ] Prepare rollback procedures
- [ ] Notify stakeholders of cutover window

### DNS Cutover
- [ ] Update DNS to point to new gateway IP
- [ ] Monitor DNS propagation
- [ ] Verify services accessible via new DNS
- [ ] Monitor for any DNS-related issues

### Service Cutover
- [ ] Stop services on GCP instances (if applicable)
- [ ] Verify services operational on target
- [ ] Monitor service logs for errors
- [ ] Test critical user workflows

### Validation Period
- [ ] Monitor all services for 24-48 hours
- [ ] Check logs for errors or warnings
- [ ] Verify user access and functionality
- [ ] Monitor performance metrics
- [ ] Address any issues immediately

---

## Phase 8: Post-Migration

### Cleanup
- [ ] Decommission GCP instances (after validation period)
- [ ] Remove GCP firewall rules
- [ ] Clean up GCP resources
- [ ] Cancel GCP billing (if applicable)
- [ ] Update documentation with new environment details

### Optimization
- [ ] Monitor resource utilization
- [ ] Optimize service configurations for new provider
- [ ] Review and adjust firewall rules if needed
- [ ] Implement any provider-specific optimizations
- [ ] Update backup procedures for new environment

### Documentation Updates
- [ ] Update voip-config repository with new IPs
- [ ] Update SSH_ACCESS.md with new connection details
- [ ] Update GCP_ENVIRONMENT_2026-06-25.md or create new provider doc
- [ ] Update any scripts with new environment details
- [ ] Create runbook for new environment management

### Monitoring Setup
- [ ] Configure monitoring for new environment
- [ ] Set up alerting for critical services
- [ ] Configure log aggregation
- [ ] Set up backup automation
- [ ] Test disaster recovery procedures

---

## Rollback Procedures

### Trigger Conditions
- Critical service failures post-migration
- Security issues discovered
- Performance degradation beyond acceptable levels
- Data corruption or loss

### Rollback Steps
1. **Immediate DNS Reversion**
   - [ ] Update DNS back to GCP gateway IP
   - [ ] Verify DNS propagation

2. **Service Reactivation**
   - [ ] Start services on GCP instances
   - [ ] Verify service functionality
   - [ ] Check logs for any issues

3. **Investigation**
   - [ ] Identify root cause of failure
   - [ ] Document issues and lessons learned
   - [ ] Plan remediation before retry

---

## Contact and Support

### Migration Team
- **Technical Lead:** [Name]
- **Network Engineer:** [Name]
- **Application Owner:** [Name]
- **Stakeholders:** [Names]

### Emergency Contacts
- **Provider Support:** [Contact information]
- **DNS Provider:** [Contact information]
- **Critical Users:** [Contact information]

---

## Timeline Estimate

- **Phase 1 (Preparation):** 2-3 days
- **Phase 2 (Infrastructure):** 1-2 days
- **Phase 3 (Gateway):** 1-2 days
- **Phase 4 (Backend):** 1-2 days
- **Phase 5 (Integration):** 1 day
- **Phase 6 (DNS/External):** 1 day
- **Phase 7 (Cutover):** 1 day
- **Phase 8 (Post-Migration):** 2-3 days

**Total Estimated Time:** 10-15 days

---

**Checklist Created:** 2026-09-20  
**Status:** Ready for execution  
**Next Step:** Select target provider and begin Phase 1