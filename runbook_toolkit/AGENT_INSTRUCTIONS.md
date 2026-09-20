# AI Agent Instructions for Runbook Toolkit Usage

## Overview

This document provides comprehensive instructions for AI agents on how to effectively use the runbook toolkit for safe, auditable system operations.

## Toolkit Location

```
/home/user/AI_Agents/runbook_toolkit/
```

## 1. Initial Toolkit Introduction

### Basic Setup Instructions
You have access to a runbook toolkit that provides safe, auditable system operations. The toolkit includes:

- Plan-based execution with approval gates
- Automatic backup and rollback capabilities  
- Secret scanning and detection
- Audit logging with cryptographic integrity
- Adaptive batch processing for efficiency
- Performance optimization features

**Always use this toolkit for system modifications rather than direct commands.**

## 2. Task-Specific Instructions

### For System Modifications
When making system changes:
1. First inspect the current state using read-only operations
2. Create a PLAN.json file in /tmp/artifacts/ describing the intended changes
3. Use the toolkit to execute: `python -m runbook_toolkit execute --plan /tmp/artifacts/PLAN.json --artifacts-dir /tmp/artifacts`
4. Review the results and verify the changes
5. If human approval is required, wait for explicit approval before proceeding

### For Security Audits
When scanning for security issues:
1. Use: `python -m runbook_toolkit scan-secrets --path /target/directory`
2. Review any secrets found and their locations
3. Never modify files based on secret detection without explicit approval
4. Use redaction guidance from the toolkit for handling sensitive data

## 3. Prompt Patterns

### Pattern 1: Infrastructure Changes
```
I need to update the application configuration. Use the runbook toolkit to:

1. Inspect the current state of /opt/app/config
2. Create a PLAN.json with the necessary changes
3. Execute the plan with the toolkit's safety features
4. Verify the changes were applied correctly
5. Provide a summary of what was changed

The toolkit is located at /home/user/AI_Agents/runbook_toolkit/
```

### Pattern 2: Package Installation
```
Install Python packages for the application. Use the runbook toolkit:

1. Check current Python environment
2. Create a PLAN.json with apt_install operations for required packages
3. Execute with --parallel flag for efficiency
4. Verify installations were successful
5. Review metrics for optimization insights

Toolkit location: /home/user/AI_Agents/runbook_toolkit/
```

### Pattern 3: Rollback Operations
```
The last deployment failed. Use the runbook toolkit to:

1. Check the STATE.md in /tmp/artifacts/ for current status
2. Review the change_manifest.json for what was changed
3. Use the toolkit's rollback capabilities if available
4. Verify system state after rollback
5. Report on what was restored and what needs manual intervention

Toolkit location: /home/user/AI_Agents/runbook_toolkit/
```

## 4. Integration into Agent Workflows

### As a Standard Operating Procedure
For any system modification task, you must:

1. **ASSESS**: Use read-only inspection first
2. **PLAN**: Create a PLAN.json describing intended changes
3. **EXECUTE**: Use the runbook toolkit to apply changes
4. **VERIFY**: Run verification checks from the plan
5. **DOCUMENT**: Review and report on the results

The runbook toolkit is your primary interface for system changes. Location: `/home/user/AI_Agents/runbook_toolkit/`

**Never bypass the toolkit for direct system modifications.**

### With Optimization Awareness
Use the runbook toolkit's optimization features for efficiency:

- Enable caching for repeated operations (default enabled)
- Use parallel processing for independent changes: `--parallel` flag
- Review metrics after execution: `python -m runbook_toolkit show-metrics`
- Consider adaptive sizing feedback from logs

Toolkit location: `/home/user/AI_Agents/runbook_toolkit/`

## 5. Safety and Approval Instructions

### High-Risk Operations
For high-risk operations (deletions, service restarts, production changes):

1. Always create a comprehensive PLAN.json first
2. Use the toolkit's dry-run validation
3. Request explicit human approval before execution
4. Execute with all safety features enabled
5. Be prepared to rollback using toolkit capabilities

Toolkit location: `/home/user/AI_Agents/runbook_toolkit/`

### Cryptographic Signing
After successful plan execution, if cryptographic verification is required:

1. Review the change_manifest.json for accuracy
2. Sign the manifest: `python -m runbook_toolkit sign-manifest --artifacts-dir /tmp/artifacts --gpg-key <key-id>`
3. Verify the signature: `python -m runbook_toolkit verify-manifest --artifacts-dir /tmp/artifacts --gpg-key <key-id>`
4. Document the signature in your report

Toolkit location: `/home/user/AI_Agents/runbook_toolkit/`

## 6. Example Complete Instruction

```
You are an AI agent tasked with system administration. You have access to a 
runbook toolkit at /home/user/AI_Agents/runbook_toolkit/ that provides safe,
auditable system operations.

Your workflow for any system modification must be:

1. INSPECTION: Use read-only commands to understand current state
2. PLANNING: Create a PLAN.json file in /tmp/artifacts/ with:
   - Clear goal description
   - Scope boundaries (include/exclude paths)
   - Specific operations with parameters
   - Verification checks

3. VALIDATION: Run dry-run validation to check scope and safety
4. APPROVAL: For high-risk changes, request human approval
5. EXECUTION: Use python -m runbook_toolkit execute --plan /tmp/artifacts/PLAN.json --artifacts-dir /tmp/artifacts
6. VERIFICATION: Review results and run verification checks
7. DOCUMENTATION: Provide summary of changes, metrics, and any issues

Use optimization flags when appropriate:
- --parallel for independent operations
- Review metrics with show-metrics command

Never use direct system commands (rm, apt, etc.) - always use the toolkit.
The toolkit provides automatic backups, rollback, secret scanning, and audit logging.
```

## 7. Troubleshooting Instructions

If the toolkit reports issues:

1. Check STATE.md for current execution state
2. Review audit_log.jsonl for detailed operation history
3. Examine change_manifest.json for what was attempted
4. Use rollback capabilities if changes were partially applied
5. Review metrics: `python -m runbook_toolkit show-metrics --metrics-file /tmp/artifacts/session_metrics.json`
6. Report specific errors and context for resolution

Toolkit location: `/home/user/AI_Agents/runbook_toolkit/`

## 8. Monitoring and Reporting

After toolkit operations, always report:

1. Execution status (success/failure/partial)
2. Number of files processed/changed
3. Any secrets detected and how they were handled
4. Resource usage and any throttling that occurred
5. Optimization metrics if available
6. Any rollback operations performed
7. Next steps or manual intervention required

Use the toolkit's built-in reporting capabilities for accurate information.

## Key Principles for Agent Instructions

1. **Always reference the toolkit location** explicitly
2. **Emphasize safety over speed** - use all available safety features
3. **Require explicit approval** for high-risk operations
4. **Leverage optimization features** but don't compromise safety
5. **Use toolkit reporting** rather than manual assessment
6. **Follow the workflow strictly** - inspection → planning → execution → verification
7. **Never bypass the toolkit** for direct system commands

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

# Sign manifest
python -m runbook_toolkit sign-manifest --artifacts-dir /tmp/artifacts --gpg-key <key-id>

# Verify manifest
python -m runbook_toolkit verify-manifest --artifacts-dir /tmp/artifacts --gpg-key <key-id>
```

## Tool Location Reminder

```
Toolkit location: /home/user/AI_Agents/runbook_toolkit/
```