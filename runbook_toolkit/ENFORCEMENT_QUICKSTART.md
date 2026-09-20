# Runbook Toolkit Enforcement Quickstart

## Overview

This enforcement system ensures AI agents always use the runbook toolkit for system modifications, providing safety, audit trails, and tool call optimization.

## What Was Created

### 1. Core Enforcement Strategy Document
**File**: `/home/user/AI_Agents/runbook_toolkit/ENFORCEMENT_STRATEGY.md`

Comprehensive guide covering:
- Technical enforcement mechanisms (command wrappers, git hooks, environment variables)
- Configuration-based enforcement (agent config, system policies)
- Monitoring and compliance systems
- Training and onboarding procedures
- Automated testing and validation
- Emergency override procedures

### 2. Automated Setup Script
**File**: `/home/user/AI_Agents/runbook_toolkit/setup_enforcement.sh`

One-command setup that installs:
- Environment variables for enforcement
- Agent configuration files
- System policy files
- Monitoring logs
- Git hook templates
- Sample testing plan

## Quick Start

### Basic Setup (2 minutes)

```bash
# Run the setup script
cd /home/user/AI_Agents/runbook_toolkit
./setup_enforcement.sh

# Source the environment variables
source ~/.bashrc

# Test the toolkit
python -m runbook_toolkit execute \
  --plan /tmp/artifacts/SAMPLE_PLAN.json \
  --artifacts-dir /tmp/artifacts
```

### System-Wide Setup (recommended)

```bash
# Run with sudo for full system-wide enforcement
sudo ./setup_enforcement.sh

# Source system environment variables
source /etc/profile.d/runbook_toolkit.sh
```

## Enforcement Levels

### Level 1: Environment-Based (Basic)
- Environment variables guide agent behavior
- Configuration files define allowed/blocked operations
- Agents are expected to follow guidelines voluntarily

### Level 2: Monitoring (Intermediate)
- Logs all agent operations
- Tracks compliance and violations
- Generates alerts for policy violations
- Provides compliance dashboards

### Level 3: Active Enforcement (Advanced)
- Command wrappers intercept dangerous operations
- Git hooks prevent non-toolkit commits
- File permissions restrict direct access
- Automated testing validates compliance

## How It Works

### 1. Agent Request
AI agent requests a system modification (file edit, command execution, etc.)

### 2. Enforcement Check
System checks:
- Is this a blocked operation?
- Is the runbook toolkit required for this?
- Has the agent used the toolkit?

### 3. Toolkit Redirect
If enforcement is active:
- Direct commands are blocked
- Agent is directed to use toolkit
- PLAN.json template is suggested

### 4. Toolkit Execution
Agent uses runbook toolkit:
- Creates PLAN.json describing changes
- Executes with safety features
- Automatic backups and audit trails

### 5. Verification
System verifies:
- Toolkit was used
- Audit trail exists
- Changes are logged

## Testing Enforcement

### Test 1: Basic Toolkit Functionality
```bash
cd /home/user/AI_Agents/runbook_toolkit
python -m runbook_toolkit execute \
  --plan /tmp/artifacts/SAMPLE_PLAN.json \
  --artifacts-dir /tmp/artifacts
```

### Test 2: Environment Variables
```bash
echo $RUNBOOK_TOOLKIT_REQUIRED
# Should output: true

echo $RUNBOOK_TOOLKIT_PATH
# Should output: /home/user/AI_Agents/runbook_toolkit
```

### Test 3: Configuration Files
```bash
cat ~/.config/ai_agent_config.json
# Should show toolkit configuration

cat ~/.config/ai_agent_policy.conf
# Should show enforcement policies
```

### Test 4: Git Hooks
```bash
# Enable git hooks globally
git config --global init.templatedir ~/.git-template

# Test in a new repository
mkdir /tmp/test_repo && cd /tmp/test_repo
git init
echo "test" > test.txt
git add test.txt
git commit -m "test"
# Should show toolkit warning (or block if strict mode)
```

## Monitoring Compliance

### Check Operation Logs
```bash
# User-level logs
cat ~/.local/log/ai_agent_operations.log

# System-level logs (if run with sudo)
cat /var/log/ai_agent_operations.log
```

### Check Violations
```bash
# User-level violations
cat ~/.local/log/ai_agent_violations.log

# System-level violations (if run with sudo)
cat /var/log/ai_agent_violations.log
```

### Generate Compliance Report
```python
# Use the compliance dashboard (see ENFORCEMENT_STRATEGY.md)
python3 /usr/local/bin/compliance_dashboard.py
```

## Customization

### Modify Allowed Operations
Edit `~/.config/ai_agent_config.json`:
```json
{
  "allowed_direct_commands": ["read", "grep", "find", "ls", "cat", "your_command"],
  "blocked_direct_commands": ["rm", "apt", "your_blocked_command"]
}
```

### Change Enforcement Mode
Edit `~/.config/ai_agent_policy.conf`:
```bash
RUNBOOK_TOOLKIT_ENFORCEMENT=MODERATE  # Options: STRICT, MODERATE, PERMISSIVE
```

### Add Custom Patterns
Edit enforcement strategy to include custom operation patterns and validation rules.

## Integration with AI Agents

### For Devin CLI
The system integrates with Devin CLI through:
- Configuration files in `~/.config/devin/`
- Custom skills for automatic toolkit usage
- Behavioral enforcement in agent config

### For Custom Agents
Custom agents should:
1. Read configuration from `~/.config/ai_agent_config.json`
2. Check environment variables before operations
3. Use toolkit for blocked operations
4. Log all operations for compliance

## Emergency Override

If you need to bypass enforcement temporarily:

```bash
export RUNBOOK_EMERGENCY_OVERRIDE=true
export RUNBOOK_OVERRIDE_REASON="Critical system issue"
export RUNBOOK_OVERRIDE_APPROVED_BY="admin@example.com"

# Perform emergency operations
# ...

# Disable override after emergency
unset RUNBOOK_EMERGENCY_OVERRIDE
```

## Troubleshooting

### Toolkit Not Found
```bash
# Check toolkit path
ls -la /home/user/AI_Agents/runbook_toolkit

# Test Python module
cd /home/user/AI_Agents/runbook_toolkit
python -m runbook_toolkit --help
```

### Environment Variables Not Set
```bash
# Source the environment file
source ~/.bashrc
# or for system-wide
source /etc/profile.d/runbook_toolkit.sh
```

### Git Hooks Not Working
```bash
# Check hook template
ls -la ~/.git-template/hooks/

# Re-enable hooks
git config --global init.templatedir ~/.git-template

# Reinitialize repository to apply hooks
cd your_repo
rm .git/hooks/*
git init
```

### Permission Denied on Logs
```bash
# Fix log permissions
chmod 644 ~/.local/log/ai_agent_operations.log
chmod 644 ~/.local/log/ai_agent_violations.log
```

## Success Metrics

Monitor these metrics to ensure enforcement is working:

- **Compliance Rate**: % of operations using toolkit (target: >95%)
- **Violation Rate**: % of direct command attempts (target: <5%)
- **Alert Response Time**: Time to respond to violations (target: <15 min)
- **Test Pass Rate**: % of automated tests passing (target: >90%)

## Next Steps

1. **Immediate**: Run setup script and test basic functionality
2. **Week 1**: Monitor compliance logs and adjust policies
3. **Week 2**: Implement advanced enforcement (command wrappers)
4. **Week 3**: Set up comprehensive monitoring and dashboards
5. **Week 4**: Implement training and certification for agents

## Support

For detailed information:
- Full strategy: `/home/user/AI_Agents/runbook_toolkit/ENFORCEMENT_STRATEGY.md`
- Agent instructions: `/home/user/AI_Agents/runbook_toolkit/AGENT_INSTRUCTIONS.md`
- Optimization guide: `/home/user/AI_Agents/runbook_toolkit/OPTIMIZATION_GUIDE.md`

## Tool Call Savings Expected

With proper enforcement:
- **Without enforcement**: 17-26 tool calls per security remediation
- **With enforcement**: 3-4 tool calls per security remediation
- **Savings**: ~80% reduction in tool calls
- **Additional benefits**: Better security, audit trails, rollback capabilities