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

**Use this toolkit for system modifications to save tokens.**
