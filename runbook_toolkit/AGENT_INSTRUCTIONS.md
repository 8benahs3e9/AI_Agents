# Runbook Toolkit - Token-Saving Instructions

## Token Savings
- Normal: 17-26 tool calls per operation  
- With toolkit: 3-4 tool calls per operation
- **Savings: ~80% reduction**

## Basic Workflow
1. Create PLAN.json in /tmp/artifacts/
2. Execute: `python -m runbook_toolkit execute --plan /tmp/artifacts/PLAN.json --artifacts-dir /tmp/artifacts`
3. Verify results

## Toolkit Location
`/home/user/AI_Agents/runbook_toolkit`

## Optimization Flags
- `--parallel` for independent operations
- Caching enabled by default (saves tokens)

## New Features (v2.1)

### Health Check Command
Run comprehensive toolkit health checks to verify dependencies, configuration, and operational status:

```bash
# Basic health check
python -m runbook_toolkit health-check

# Detailed health check with verbose output
python -m runbook_toolkit health-check --verbose

# Save health report to file
python -m runbook_toolkit health-check --output /tmp/health_report.json
```

**Health checks include:**
- Python version compatibility
- Dependency verification
- Directory accessibility
- File permissions
- Template validation
- Cache status
- Metrics directory status
- Disk space availability

### Template Generator
Generate optimized PLAN.json templates for common automation tasks:

```bash
# System update template
python -m runbook_toolkit generate-template --type system-update

# Log cleanup template
python -m runbook_toolkit generate-template --type log-cleanup

# Service restart template
python -m runbook_toolkit generate-template --type service-restart --services nginx fail2ban

# Backup template
python -m runbook_toolkit generate-template --type backup --backup-dirs /etc/nginx /var/lib/radicale

# Specify custom output path
python -m runbook_toolkit generate-template --type system-update --output /tmp/my_template.json
```

**Available template types:**
- `system-update` - Package updates and security patches
- `log-cleanup` - Log file cleanup and disk space recovery
- `service-restart` - Service restart operations
- `backup` - Directory backup operations

## Quick Commands
```bash
# Execute plan
python -m runbook_toolkit execute --plan /tmp/artifacts/PLAN.json --artifacts-dir /tmp/artifacts

# With optimizations
python -m runbook_toolkit execute --plan /tmp/artifacts/PLAN.json --artifacts-dir /tmp/artifacts --parallel

# Health check
python -m runbook_toolkit health-check --verbose

# Generate template
python -m runbook_toolkit generate-template --type system-update

# Scan secrets
python -m runbook_toolkit scan-secrets --path /target/directory

# Show metrics
python -m runbook_toolkit show-metrics
```

## Available Templates
Located in `/home/user/AI_Agents/runbook_toolkit/templates/`:
- `vm_migration_analysis.json` - VM infrastructure migration analysis
- `documentation_consolidation.json` - Documentation repository consolidation
- `security_remediation_plan.json` - Security issue remediation
- `dns_troubleshooting.json` - DNS troubleshooting procedures
- `dns_verification_procedures.json` - DNS verification and testing
- `wireguard_configuration.json` - WireGuard VPN setup
- `toolkit_health_check.json` - Toolkit health verification

## Usage Pattern: VM Migration Analysis
When analyzing VMs for migration:
1. Use existing documentation in voip-config repository
2. Run diagnostic commands to gather current state
3. Backup configuration files
4. Create comprehensive migration documentation
5. Generate reusable templates for future migrations

## Usage Pattern: Documentation Consolidation
When consolidating documentation repositories:
1. Analyze current documentation structure and file dates
2. Verify system state against documented information
3. Create consolidation report with recommendations
4. Update core documentation with current state
5. Archive outdated files to maintain clean structure

## Usage Pattern: System Maintenance
When performing system maintenance:
1. Run health check to verify toolkit status
2. Generate appropriate template for the task
3. Customize template if needed
4. Execute the plan with appropriate flags
5. Verify results with post-execution checks

## New Modules
- `toolkit_health.py` - Comprehensive health checking system
- `template_generator.py` - Automated template generation for common tasks

**Use this toolkit for system modifications to save tokens.**
