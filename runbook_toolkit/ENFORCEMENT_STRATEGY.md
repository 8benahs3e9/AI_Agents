# Runbook Toolkit Enforcement Strategy

## Overview

This document outlines comprehensive strategies to ensure AI agents always use the runbook toolkit for system modifications, providing both technical safeguards and procedural controls.

## 1. Technical Enforcement Mechanisms

### 1.1 System Command Wrappers

Create wrapper scripts that intercept direct system commands and redirect to runbook toolkit:

```bash
#!/bin/bash
# /usr/local/bin/safe_rm.sh
# Wrapper for rm command that enforces runbook toolkit usage

TOOLKIT_PATH="/home/user/AI_Agents/runbook_toolkit"
REAL_RM="/bin/rm"

# Check if running from runbook toolkit
if [[ "$RUNBOOK_TOOLKIT_ACTIVE" != "true" ]]; then
    echo "❌ ERROR: Direct rm command not allowed for AI agents"
    echo "Please use the runbook toolkit for file operations:"
    echo "  python -m runbook_toolkit execute --plan PLAN.json --artifacts-dir /tmp/artifacts"
    exit 1
fi

# Execute the real command if authorized
exec "$REAL_RM" "$@"
```

**Deploy wrappers for dangerous commands:**
- `rm`, `rmdir` - file deletion
- `apt`, `apt-get` - package management  
- `systemctl` - service management
- `chmod`, `chown` - permission changes
- `iptables`, `ufw` - firewall modifications

### 1.2 Git Hooks for Repository Operations

Add pre-commit hooks to ensure runbook toolkit usage for repository modifications:

```bash
#!/bin/bash
# .git/hooks/pre-commit
# Check if changes were made using runbook toolkit

ARTIFACTS_DIR="/tmp/artifacts"
TOOLKIT_MARKER=".runbook_toolkit_used"

# Check for toolkit usage marker
if [ ! -f "$ARTIFACTS_DIR/$TOOLKIT_MARKER" ]; then
    echo "❌ ERROR: Changes not made using runbook toolkit"
    echo "Please use: python -m runbook_toolkit execute --plan PLAN.json --artifacts-dir $ARTIFACTS_DIR"
    exit 1
fi

# Verify audit trail exists
if [ ! -f "$ARTIFACTS_DIR/audit_log.jsonl" ]; then
    echo "❌ ERROR: No audit trail found for these changes"
    exit 1
fi

echo "✅ Runbook toolkit usage verified"
exit 0
```

### 1.3 Environment Variable Enforcement

Set environment variables that agents must respect:

```bash
# In agent startup script or system profile
export RUNBOOK_TOOLKIT_REQUIRED=true
export RUNBOOK_TOOLKIT_PATH="/home/user/AI_Agents/runbook_toolkit"
export RUNBOOK_ARTIFACTS_DIR="/tmp/artifacts"
export RUNBOOK_ENFORCEMENT_MODE=strict
```

### 1.4 File Permission Controls

Restrict direct access to dangerous system files:

```bash
# Set restrictive permissions on critical system files
chmod 750 /etc/systemd/system/
chmod 750 /etc/iptables/
chmod 750 /etc/postfix/

# Create a group for runbook toolkit operations
sudo groupadd runbook_operators
sudo chown -R :runbook_operators /home/user/AI_Agents/runbook_toolkit
chmod 775 /home/user/AI_Agents/runbook_toolkit
```

## 2. Configuration-Based Enforcement

### 2.1 Agent Configuration File

Create a mandatory configuration file that agents must load:

```json
// /etc/ai_agent_config.json
{
  "runbook_toolkit": {
    "required": true,
    "path": "/home/user/AI_Agents/runbook_toolkit",
    "enforcement_mode": "strict",
    "allowed_direct_commands": ["read", "grep", "find", "ls"],
    "blocked_direct_commands": ["rm", "apt", "systemctl", "chmod", "iptables"],
    "artifacts_directory": "/tmp/artifacts",
    "audit_required": true,
    "approval_required_for": ["delete", "service_restart", "firewall_changes"]
  },
  "monitoring": {
    "log_toolkit_usage": true,
    "log_direct_command_attempts": true,
    "alert_on_violations": true
  }
}
```

### 2.2 System Policy File

Create a system-wide policy for AI agent operations:

```bash
# /etc/ai_agent_policy.conf
# AI Agent Operations Policy

RUNBOOK_TOOLKIT_ENFORCEMENT=STRICT
TOOLKIT_PATH=/home/user/AI_Agents/runbook_toolkit
ARTIFACTS_DIR=/tmp/artifacts

# Allowed operations without toolkit
ALLOWED_READ_ONLY_OPERATIONS="read grep find ls cat head tail"
ALLOWED_INFORMATION_OPERATIONS="ps df free netstat"

# Blocked operations (must use toolkit)
BLOCKED_DESTRUCTIVE_OPERATIONS="rm rmdir dd shred"
BLOCKED_SYSTEM_OPERATIONS="apt apt-get yum dnf systemctl"
BLOCKED_NETWORK_OPERATIONS="iptables ufw firewall-cmd"
BLOCKED_PERMISSION_OPERATIONS="chmod chown chgrp"

# Approval requirements
APPROVAL_REQUIRED_FOR_DELETES=true
APPROVAL_REQUIRED_FOR_SERVICE_CHANGES=true
APPROVAL_REQUIRED_FOR_FIREWALL_CHANGES=true
APPROVAL_REQUIRED_FOR_PACKAGE_INSTALLS=true
```

## 3. Monitoring and Compliance

### 3.1 Audit Logging System

Implement comprehensive logging of all agent operations:

```python
#!/usr/bin/env python3
# /usr/local/bin/agent_operation_monitor.py
import os
import json
import datetime
from pathlib import Path

class AgentOperationMonitor:
    def __init__(self):
        self.log_file = "/var/log/ai_agent_operations.log"
        self.violation_log = "/var/log/ai_agent_violations.log"
        
    def log_operation(self, agent_id, operation_type, command, used_toolkit):
        """Log all agent operations"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent_id": agent_id,
            "operation_type": operation_type,
            "command": command,
            "used_toolkit": used_toolkit,
            "compliance": "COMPLIANT" if used_toolkit else "VIOLATION"
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        if not used_toolkit:
            self.log_violation(log_entry)
            
    def log_violation(self, entry):
        """Log violations separately for alerting"""
        with open(self.violation_log, "a") as f:
            f.write(json.dumps(entry) + "\n")
        # Trigger alert
        self.send_alert(entry)
        
    def send_alert(self, violation):
        """Send alert for violations"""
        # Implement alerting (email, gotify, etc.)
        pass
```

### 3.2 Compliance Dashboard

Create a dashboard to monitor compliance:

```python
#!/usr/bin/env python3
# /usr/local/bin/compliance_dashboard.py
import json
from collections import Counter
from datetime import datetime, timedelta

class ComplianceDashboard:
    def __init__(self):
        self.log_file = "/var/log/ai_agent_operations.log"
        
    def generate_report(self, days=7):
        """Generate compliance report"""
        cutoff = datetime.now() - timedelta(days=days)
        
        operations = []
        with open(self.log_file, "r") as f:
            for line in f:
                entry = json.loads(line)
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time >= cutoff:
                    operations.append(entry)
        
        total = len(operations)
        compliant = sum(1 for op in operations if op["compliance"] == "COMPLIANT")
        violations = total - compliant
        
        return {
            "period_days": days,
            "total_operations": total,
            "compliant_operations": compliant,
            "violations": violations,
            "compliance_rate": f"{(compliant/total)*100:.1f}%" if total > 0 else "N/A",
            "top_violations": self.get_top_violations(operations)
        }
```

## 4. Training and Onboarding

### 4.1 Agent Onboarding Checklist

Create a mandatory onboarding process:

```markdown
# AI Agent Onboarding Checklist

## Required Training Modules

1. **Runbook Toolkit Basics** (30 min)
   - [ ] Complete toolkit overview
   - [ ] Practice creating PLAN.json files
   - [ ] Execute sample operations
   - [ ] Review audit trails

2. **Security Procedures** (20 min)
   - [ ] Secret scanning procedures
   - [ ] Approval gate workflows
   - [ ] Rollback procedures
   - [ ] Emergency procedures

3. **Optimization Features** (15 min)
   - [ ] Caching configuration
   - [ ] Parallel processing usage
   - [ ] Metrics interpretation
   - [ ] Performance tuning

## Practical Assessment

- [ ] Create and execute a sample plan
- [ ] Handle a simulated approval scenario
- [ ] Perform a rollback operation
- [ ] Interpret metrics output
- [ ] Pass compliance quiz (90%+ required)

## Certification

Upon completion, agents receive:
- Runbook Toolkit Certification
- Compliance Badge
- Toolkit Access Credentials
```

### 4.2 Regular Training Refreshers

Implement periodic training refreshers:

```bash
#!/bin/bash
# Monthly training refresher scheduler

# Schedule monthly training sessions
0 9 1 * * /usr/local/bin/run_training_refresher.sh

#!/bin/bash
# /usr/local/bin/run_training_refresher.sh
# Monthly training refresher

AGENT_LOG="/var/log/agent_training.log"
date >> $AGENT_LOG
echo "Starting monthly training refresher" >> $AGENT_LOG

# Check which agents need refresher
for agent in /home/agent_*; do
    if [[ $(find $agent -name "*.last_training" -mtime +30) ]]; then
        echo "Agent $agent needs training refresher" >> $AGENT_LOG
        # Trigger training notification
    fi
done
```

## 5. Automated Testing and Validation

### 5.1 Compliance Testing Suite

Create automated tests to verify toolkit usage:

```python
#!/usr/bin/env python3
# /usr/local/bin/compliance_test_suite.py
import subprocess
import json
import os

class ComplianceTestSuite:
    def __init__(self):
        self.toolkit_path = "/home/user/AI_Agents/runbook_toolkit"
        self.test_results = []
        
    def test_toolkit_availability(self):
        """Test if toolkit is accessible"""
        result = subprocess.run(
            ["python", "-m", "runbook_toolkit", "--help"],
            cwd=self.toolkit_path,
            capture_output=True
        )
        return result.returncode == 0
        
    def test_wrapper_functionality(self):
        """Test if command wrappers are working"""
        # Test that blocked commands are intercepted
        result = subprocess.run(
            ["safe_rm.sh", "/tmp/test_file"],
            capture_output=True,
            env={"RUNBOOK_TOOLKIT_ACTIVE": "false"}
        )
        return result.returncode != 0  # Should fail
        
    def test_git_hook_enforcement(self):
        """Test if git hooks are enforcing toolkit usage"""
        # Try to commit without toolkit marker
        test_dir = "/tmp/test_git_repo"
        os.makedirs(test_dir, exist_ok=True)
        subprocess.run(["git", "init"], cwd=test_dir)
        # ... test commit without marker
        return True  # Implementation depends on hook logic
        
    def run_all_tests(self):
        """Run all compliance tests"""
        tests = [
            ("Toolkit Availability", self.test_toolkit_availability),
            ("Wrapper Functionality", self.test_wrapper_functionality),
            ("Git Hook Enforcement", self.test_git_hook_enforcement)
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                self.test_results.append({
                    "test": test_name,
                    "result": "PASS" if result else "FAIL",
                    "timestamp": datetime.datetime.now().isoformat()
                })
            except Exception as e:
                self.test_results.append({
                    "test": test_name,
                    "result": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.datetime.now().isoformat()
                })
        
        return self.test_results
```

### 5.2 Continuous Compliance Monitoring

Implement continuous monitoring:

```bash
#!/bin/bash
# /usr/local/bin/continuous_compliance_monitor.sh
# Run compliance checks every hour

while true; do
    # Run compliance tests
    python3 /usr/local/bin/compliance_test_suite.py > /tmp/compliance_results.json
    
    # Check for violations
    if grep -q "FAIL" /tmp/compliance_results.json; then
        # Send alert
        echo "Compliance test failed" | mail -s "Compliance Alert" admin@example.com
    fi
    
    # Check for direct command usage
    if grep -q "VIOLATION" /var/log/ai_agent_operations.log; then
        echo "Direct command usage detected" | mail -s "Policy Violation" admin@example.com
    fi
    
    sleep 3600  # Check every hour
done
```

## 6. Integration with Devin CLI

### 6.1 Devin CLI Configuration

Create Devin CLI-specific configuration:

```json
// ~/.config/devin/agent_config.json
{
  "toolkit_integration": {
    "runbook_toolkit_path": "/home/user/AI_Agents/runbook_toolkit",
    "enforcement_enabled": true,
    "auto_plan_generation": true,
    "mandatory_for_operations": [
      "file_edit",
      "file_delete", 
      "command_execution",
      "package_installation",
      "service_management"
    ]
  },
  "behavior": {
    "default_to_toolkit": true,
    "require_confirmation_for_direct_commands": true,
    "log_all_operations": true
  }
}
```

### 6.2 Custom Skill for Devin

Create a custom Devin skill to enforce toolkit usage:

```markdown
# runbook-toolkit-enforcer/SKILL.md

## Runbook Toolkit Enforcer

**Purpose**: Ensures all AI agents use the runbook toolkit for system modifications

## Activation

This skill activates automatically when:
- Any file modification operation is requested
- System command execution is requested
- Package installation/removal is requested
- Service management is requested

## Behavior

When activated, this skill:
1. Intercepts the operation request
2. Creates a PLAN.json template
3. Requires agent to use runbook toolkit
4. Validates toolkit usage before proceeding
5. Logs all operations for compliance

## Configuration

Toolkit path: /home/user/AI_Agents/runbook_toolkit
Artifacts directory: /tmp/artifacts
Enforcement mode: strict

## Examples

### File Edit Operation
Instead of direct edit:
```
edit file_path="/etc/config.conf" old_string="..." new_string="..."
```

Skill enforces:
```
1. Create PLAN.json with file_update operation
2. Execute: python -m runbook_toolkit execute --plan PLAN.json --artifacts-dir /tmp/artifacts
3. Verify results
```

### Command Execution
Instead of direct exec:
```
exec command="apt install nginx"
```

Skill enforces:
```
1. Create PLAN.json with apt_install operation  
2. Execute with toolkit
3. Verify installation
```

## Enforcement Levels

- **STRICT**: All modifications must use toolkit
- **MODERATE**: Warn but allow with confirmation
- **PERMISSIVE**: Log only, no enforcement

Current level: STRICT
```

## 7. Emergency Procedures

### 7.1 Emergency Override Process

Define emergency override procedures:

```markdown
# Emergency Override Procedures

## When to Use Emergency Override

Emergency override may be used when:
1. Runbook toolkit is unavailable or malfunctioning
2. Critical system issue requires immediate intervention
3. Toolkit execution is causing system instability
4. Time-critical security incident response

## Override Process

1. **Authorization Required**
   - Must be approved by system administrator
   - Document justification in emergency log
   - Set temporary override flag

2. **Execute Emergency Procedure**
   ```bash
   export RUNBOOK_EMERGENCY_OVERRIDE=true
   export RUNBOOK_OVERRIDE_REASON="Critical security incident"
   export RUNBOOK_OVERRIDE_APPROVED_BY="admin@example.com"
   ```

3. **Execute Direct Operations**
   - Perform necessary operations directly
   - Document all changes manually
   - Create manual audit trail

4. **Post-Emergency Recovery**
   - Disable override flag
   - Create retrospective PLAN.json
   - Execute retrospective audit
   - Update compliance documentation
   - Review and improve procedures

## Emergency Log

All emergency overrides must be logged in:
/var/log/runbook_emergency_overrides.log

## Review Process

All emergency overrides are reviewed within 24 hours by:
- System administrator
- Security team
- Compliance officer
```

## Implementation Priority

### Phase 1: Foundation (Immediate)
- [ ] Deploy command wrappers for dangerous operations
- [ ] Implement environment variable enforcement
- [ ] Create agent configuration file
- [ ] Set up basic monitoring

### Phase 2: Integration (Week 1-2)
- [ ] Implement git hooks
- [ ] Create monitoring system
- [ ] Develop compliance dashboard
- [ ] Set up automated testing

### Phase 3: Training (Week 2-3)
- [ ] Develop onboarding program
- [ ] Create training materials
- [ ] Implement certification process
- [ ] Schedule regular refreshers

### Phase 4: Advanced (Week 3-4)
- [ ] Integrate with Devin CLI
- [ ] Create custom skills
- [ ] Implement emergency procedures
- [ ] Full compliance monitoring

## Success Metrics

- **Compliance Rate**: Target >95% toolkit usage
- **Violation Rate**: Target <5% direct command usage
- **Training Completion**: 100% agent certification
- **Test Coverage**: >90% automated test pass rate
- **Alert Response**: <15 minutes for violation alerts

## Maintenance

- Review enforcement strategies monthly
- Update patterns based on new threats
- Refresh training materials quarterly
- Audit compliance logs weekly
- Update emergency procedures as needed