# Asterisk Troubleshooting Tools

This directory contains Asterisk PBX verification, troubleshooting, and remediation tools.

## Files

- **asterisk_checker.py** - Backend verification script (for SSH access to remote Asterisk servers)
- **asterisk_local_checker.py** - Local verification script (for checking Asterisk on the current system)
- **asterisk_runner.py** - Runbook toolkit integration for Asterisk operations
- **asterisk_troubleshooter.py** - Advanced troubleshooting script with comprehensive diagnostics
- **fix_asterisk_issues.sh** - Comprehensive fix script for common Asterisk issues
- **asterisk_verification_plan.json** - Runbook toolkit template for Asterisk verification procedures

## Usage

Most scripts can be run directly:
```bash
# Local Asterisk verification
python asterisk_local_checker.py

# Remote Asterisk verification (requires SSH access)
python asterisk_checker.py

# Comprehensive troubleshooting
python asterisk_troubleshooter.py

# Automatic fixes
./fix_asterisk_issues.sh
```

For runbook toolkit integration, use the verification plan template with the main toolkit CLI.

## Integration

These tools are designed to work with the main runbook toolkit for safe, auditable system operations. See the main toolkit documentation for details on plan-based execution.
