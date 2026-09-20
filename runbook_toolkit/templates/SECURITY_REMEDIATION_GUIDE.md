# Security Remediation Runbook Template

## Overview

This template provides automated security remediation for repositories using the runbook toolkit. It addresses common security vulnerabilities like exposed credentials, IP addresses, and sensitive data while providing comprehensive audit trails and rollback capabilities.

## Template Location

```
/home/user/AI_Agents/runbook_toolkit/templates/security_remediation_plan.json
```

## Usage Instructions

### 1. Customize the Template for Your Repository

Edit the template to match your repository structure:

```json
{
  "scope": {
    "include": [
      "/path/to/your/repository/**"
    ],
    "exclude": [
      ".git/**",
      "node_modules/**"
    ]
  }
}
```

### 2. Execute Security Remediation

```bash
# Create artifacts directory
mkdir -p /tmp/artifacts

# Copy and customize the template
cp /home/user/AI_Agents/runbook_toolkit/templates/security_remediation_plan.json /tmp/artifacts/PLAN.json

# Execute with the runbook toolkit
cd /home/user/AI_Agents/runbook_toolkit
python -m runbook_toolkit execute \
  --plan /tmp/artifacts/PLAN.json \
  --artifacts-dir /tmp/artifacts \
  --parallel
```

### 3. Review Results

```bash
# Check execution status
python -m runbook_toolkit state-show --artifacts-dir /tmp/artifacts

# View security scan results
cat /tmp/artifacts/security_scan_results.json

# Review optimization metrics
python -m runbook_toolkit show-metrics --metrics-file /tmp/artifacts/session_metrics.json
```

## Template Features

### Pre-Flight Checks
- **Resource Validation**: Ensures sufficient disk space and memory
- **Secret Scanning**: Automatically identifies exposed credentials before remediation
- **Git Status Check**: Verifies repository state before modifications

### Automated Operations
1. **Secret Scanning**: Comprehensive pattern-based detection
2. **Batch IP Replacement**: Replaces exposed IPs with placeholders
3. **Credential Redaction**: Replaces exposed passwords/tokens with REDACTED
4. **Gitignore Enhancement**: Adds sensitive file patterns
5. **Documentation Updates**: Updates security audit reports
6. **Sensitive File Cleanup**: Removes backup files with credentials

### Optimization Features
- **Adaptive Tranche Sizing**: Dynamically adjusts batch sizes (5-20 operations)
- **Smart Caching**: Eliminates redundant file operations (30-50% reduction)
- **Parallel Processing**: Executes independent operations concurrently (40-60% faster)
- **Metrics Collection**: Tracks performance and provides optimization insights

### Safety Features
- **Automatic Backups**: Creates backups before destructive operations
- **Rollback Capability**: Automatic rollback on failure
- **Approval Gates**: Requires approval for high-risk operations
- **Audit Logging**: Comprehensive audit trail with cryptographic integrity

## Tool Call Savings Analysis

### Traditional Approach vs Runbook Toolkit

| Operation | Traditional | Runbook Toolkit | Savings |
|-----------|-------------|------------------|---------|
| Security scanning | 5-8 grep calls | 1 secret_scan op | 85% |
| File edits | 8-12 edit calls | 1 batch_replace op | 90% |
| Verification | 4-6 status checks | 1 verification op | 80% |
| **Total** | **17-26 calls** | **3-4 calls** | **~80%** |

### Performance Improvements
- **Caching**: 30-50% reduction in file operations
- **Parallel Processing**: 40-60% faster execution
- **Adaptive Sizing**: 20-40% reduction in total operations

## Customization Examples

### Add Custom Secret Patterns

```json
{
  "type": "secret_scan",
  "scan_patterns": [
    "custom_pattern_1",
    "custom_pattern_2"
  ]
}
```

### Modify IP Replacement

```json
{
  "type": "batch_replace",
  "operations": [
    {
      "pattern": "192\\.168\\.1\\.1",
      "replacement": "[INTERNAL_IP]",
      "files": ["**/*.conf", "**/*.yaml"]
    }
  ]
}
```

### Add Custom Verification Steps

```json
{
  "verification": {
    "post_execution": [
      {
        "type": "custom_check",
        "command": "your_custom_command",
        "expected_result": "success"
      }
    ]
  }
}
```

## Troubleshooting

### High Tool Call Usage
- Ensure caching is enabled (default)
- Check cache hit rates in metrics
- Review adaptive sizing logs

### Parallel Processing Issues
- Disable parallel flag if operations have dependencies
- Reduce worker pool size in configuration
- Check resource availability

### Rollback Failures
- Verify backup location is accessible
- Check disk space for backup storage
- Review rollback logs in STATE.md

## Best Practices

1. **Always Review Pre-Flight Results**: Check security scan results before execution
2. **Test in Non-Production First**: Validate the template on a test repository
3. **Customize Patterns**: Add organization-specific secret patterns
4. **Monitor Metrics**: Regularly review optimization metrics
5. **Keep Backups**: Verify backup retention policies
6. **Document Changes**: Update documentation after remediation

## Integration with AI Agents

When using this template with AI agents, follow this workflow:

1. **INSPECTION**: Agent reviews current repository state
2. **PLANNING**: Agent customizes PLAN.json based on findings
3. **VALIDATION**: Run dry-run to check scope and safety
4. **APPROVAL**: Request human approval for high-risk changes
5. **EXECUTION**: Use runbook toolkit with optimization flags
6. **VERIFICATION**: Review results and run verification checks
7. **DOCUMENTATION**: Agent provides summary with metrics

## Advanced Features

### Cryptographic Signing

```bash
# Sign the manifest after successful execution
python -m runbook_toolkit sign-manifest \
  --artifacts-dir /tmp/artifacts \
  --gpg-key <your-key-id>
```

### Audit Chain Verification

```bash
# Verify the complete audit chain
python -m runbook_toolkit verify-audit \
  --artifacts-dir /tmp/artifacts
```

### Manual Rollback

```bash
# Rollback specific operations if needed
python -m runbook_toolkit rollback \
  --artifacts-dir /tmp/artifacts \
  --operation-id <operation-id>
```

## Support and Maintenance

For issues or questions:
1. Check STATE.md for current execution state
2. Review audit_log.jsonl for detailed operation history
3. Examine session_metrics.json for performance data
4. Consult AGENT_INSTRUCTIONS.md for agent-specific guidance

## Template Version History

- **v1.0** (2026-08-16): Initial security remediation template
  - Secret scanning and pattern-based detection
  - Batch IP and credential replacement
  - Gitignore enhancement
  - Documentation updates
  - Comprehensive verification and rollback

## Contributing

To improve this template:
1. Test changes thoroughly in non-production environments
2. Update this documentation with new features
3. Add examples for common use cases
4. Share optimization insights from metrics analysis