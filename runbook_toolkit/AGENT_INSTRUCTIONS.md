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

## Quick Commands
```bash
# Execute plan
python -m runbook_toolkit execute --plan /tmp/artifacts/PLAN.json --artifacts-dir /tmp/artifacts

# With optimizations
python -m runbook_toolkit execute --plan /tmp/artifacts/PLAN.json --artifacts-dir /tmp/artifacts --parallel

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

**Use this toolkit for system modifications to save tokens.**
