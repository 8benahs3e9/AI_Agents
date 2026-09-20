# Security Remediation Quick Reference

## Instant Commands

```bash
# Setup
mkdir -p /tmp/artifacts
cp /home/user/AI_Agents/runbook_toolkit/templates/security_remediation_plan.json /tmp/artifacts/PLAN.json

# Customize for your repository (edit /tmp/artifacts/PLAN.json)
nano /tmp/artifacts/PLAN.json

# Execute with optimizations
cd /home/user/AI_Agents/runbook_toolkit
python -m runbook_toolkit execute \
  --plan /tmp/artifacts/PLAN.json \
  --artifacts-dir /tmp/artifacts \
  --parallel

# Review results
python -m runbook_toolkit state-show --artifacts-dir /tmp/artifacts
python -m runbook_toolkit show-metrics --metrics-file /tmp/artifacts/session_metrics.json
cat /tmp/artifacts/security_scan_results.json
```

## Template Customization

### Change Repository Path
```json
{
  "scope": {
    "include": ["/your/repository/path/**"]
  }
}
```

### Add Custom Patterns
```json
{
  "type": "secret_scan",
  "scan_patterns": ["your_custom_pattern"]
}
```

### Modify Replacements
```json
{
  "type": "batch_replace",
  "operations": [
    {
      "pattern": "your_pattern",
      "replacement": "your_replacement",
      "files": ["**/*.md"]
    }
  ]
}
```

## What It Does Automatically

✅ Scans for exposed credentials (passwords, IPs, API keys)
✅ Replaces exposed IPs with placeholders
✅ Redacts exposed credentials
✅ Enhances .gitignore with sensitive patterns
✅ Updates security documentation
✅ Removes sensitive backup files
✅ Creates automatic backups
✅ Provides rollback capability
✅ Generates comprehensive audit trail

## Expected Tool Call Savings

| Approach | Tool Calls | Savings |
|----------|------------|---------|
| Manual | 17-26 calls | - |
| Runbook Toolkit | 3-4 calls | ~80% |

## Safety Features

🔒 Pre-flight resource validation
🔒 Automatic backups before changes
🔒 Approval gates for high-risk operations
🔒 Automatic rollback on failure
🔒 Comprehensive audit logging
🔒 Cryptographic integrity verification

## Troubleshooting

**Issue**: High tool call usage
**Fix**: Ensure caching enabled, check cache hit rates

**Issue**: Parallel processing fails
**Fix**: Remove --parallel flag, check dependencies

**Issue**: Rollback fails
**Fix**: Verify backup location, check disk space

## Next Steps

1. Customize template for your repository
2. Test in non-production environment
3. Review security scan results
4. Execute with approval
5. Verify changes and metrics
6. Commit improvements to git

**Full Guide**: `/home/user/AI_Agents/runbook_toolkit/templates/SECURITY_REMEDIATION_GUIDE.md`