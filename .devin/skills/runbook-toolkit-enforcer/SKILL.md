---
name: runbook-toolkit-enforcer
description: Enforce runbook toolkit usage for system modifications in AI_Agents workspace
triggers:
  - user
  - model
---

# Runbook Toolkit Enforcer

🛡️ **Runbook Toolkit Enforcer Active** - Working in AI_Agents directory - runbook toolkit instructions will be applied automatically.

**Toolkit location**: `/home/user/AI_Agents/runbook_toolkit/`

## Purpose

Ensures all AI agents use the runbook toolkit for system modifications when working in the AI_Agents directory/workspace.

## Required Workflow

For any system modification task, you must follow this workflow:

1. **INSPECTION**: Use read-only operations to understand current state
2. **PLANNING**: Create a PLAN.json file in /tmp/artifacts/ with:
   - Clear goal description
   - Scope boundaries (include/exclude paths)
   - Specific operations with parameters
   - Verification checks
3. **VALIDATION**: Run dry-run validation to check scope and safety
4. **APPROVAL**: For high-risk changes, request human approval
5. **EXECUTION**: Use `python -m runbook_toolkit execute --plan /tmp/artifacts/PLAN.json --artifacts-dir /tmp/artifacts`
6. **VERIFICATION**: Review results and run verification checks
7. **DOCUMENTATION**: Provide summary of changes, metrics, and any issues

## Configuration

- **Toolkit Path**: `/home/user/AI_Agents/runbook_toolkit`
- **Artifacts Directory**: `/tmp/artifacts`
- **Enforcement Mode**: Strict
- **Allowed Direct Commands**: read, grep, find, ls, cat, head, tail
- **Blocked Direct Commands**: rm, apt, systemctl, chmod, chown, iptables

## Quick Reference Commands

```bash
# Execute a plan
python -m runbook_toolkit execute --plan /tmp/artifacts/PLAN.json --artifacts-dir /tmp/artifacts

# Execute with optimizations
python -m runbook_toolkit execute --plan /tmp/artifacts/PLAN.json --artifacts-dir /tmp/artifacts --parallel

# Scan for secrets
python -m runbook_toolkit scan-secrets --path /target/directory

# Verify audit chain
python -m runbook_toolkit verify-audit --artifacts-dir /tmp/artifacts

# Show current state
python -m runbook_toolkit state-show --artifacts-dir /tmp/artifacts

# Show metrics
python -m runbook_toolkit show-metrics
```

## Documentation References

- Agent Instructions: `/home/user/AI_Agents/runbook_toolkit/AGENT_INSTRUCTIONS.md`
- Enforcement Strategy: `/home/user/AI_Agents/runbook_toolkit/ENFORCEMENT_STRATEGY.md`
- Quick Start: `/home/user/AI_Agents/runbook_toolkit/ENFORCEMENT_QUICKSTART.md`
