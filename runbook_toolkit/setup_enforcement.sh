#!/bin/bash
# Runbook Toolkit Enforcement Setup Script
# This script sets up basic enforcement mechanisms to ensure AI agents use the runbook toolkit

set -e

TOOLKIT_PATH="/home/user/AI_Agents/runbook_toolkit"
ARTIFACTS_DIR="/tmp/artifacts"
CONFIG_FILE="/etc/ai_agent_config.json"
POLICY_FILE="/etc/ai_agent_policy.conf"

echo "=== Runbook Toolkit Enforcement Setup ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root for system-wide enforcement setup"
    echo "For user-level setup, run without sudo (limited functionality)"
    SUDO=""
else
    SUDO="sudo"
    echo "Running with system-wide permissions"
fi
echo ""

# Create artifacts directory
echo "1. Creating artifacts directory..."
mkdir -p "$ARTIFACTS_DIR"
chmod 755 "$ARTIFACTS_DIR"
echo "✅ Artifacts directory created: $ARTIFACTS_DIR"
echo ""

# Set environment variables
echo "2. Setting environment variables..."
if [ -n "$SUDO" ]; then
    cat << 'EOF' | $SUDO tee /etc/profile.d/runbook_toolkit.sh > /dev/null
export RUNBOOK_TOOLKIT_REQUIRED=true
export RUNBOOK_TOOLKIT_PATH="/home/user/AI_Agents/runbook_toolkit"
export RUNBOOK_ARTIFACTS_DIR="/tmp/artifacts"
export RUNBOOK_ENFORCEMENT_MODE=strict
EOF
    echo "✅ Environment variables set in /etc/profile.d/runbook_toolkit.sh"
else
    cat << 'EOF' >> ~/.bashrc
export RUNBOOK_TOOLKIT_REQUIRED=true
export RUNBOOK_TOOLKIT_PATH="/home/user/AI_Agents/runbook_toolkit"
export RUNBOOK_ARTIFACTS_DIR="/tmp/artifacts"
export RUNBOOK_ENFORCEMENT_MODE=strict
EOF
    echo "✅ Environment variables set in ~/.bashrc"
fi
echo ""

# Create agent configuration file
echo "3. Creating agent configuration file..."
if [ -n "$SUDO" ]; then
    cat << 'EOF' | $SUDO tee "$CONFIG_FILE" > /dev/null
{
  "runbook_toolkit": {
    "required": true,
    "path": "/home/user/AI_Agents/runbook_toolkit",
    "enforcement_mode": "strict",
    "allowed_direct_commands": ["read", "grep", "find", "ls", "cat"],
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
EOF
    echo "✅ Configuration file created: $CONFIG_FILE"
else
    mkdir -p ~/.config
    cat << 'EOF' > ~/.config/ai_agent_config.json
{
  "runbook_toolkit": {
    "required": true,
    "path": "/home/user/AI_Agents/runbook_toolkit",
    "enforcement_mode": "strict",
    "allowed_direct_commands": ["read", "grep", "find", "ls", "cat"],
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
EOF
    echo "✅ Configuration file created: ~/.config/ai_agent_config.json"
fi
echo ""

# Create system policy file
echo "4. Creating system policy file..."
if [ -n "$SUDO" ]; then
    cat << 'EOF' | $SUDO tee "$POLICY_FILE" > /dev/null
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
EOF
    echo "✅ Policy file created: $POLICY_FILE"
else
    cat << 'EOF' > ~/.config/ai_agent_policy.conf
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
EOF
    echo "✅ Policy file created: ~/.config/ai_agent_policy.conf"
fi
echo ""

# Create basic monitoring log
echo "5. Setting up monitoring logs..."
if [ -n "$SUDO" ]; then
    $SUDO touch /var/log/ai_agent_operations.log
    $SUDO touch /var/log/ai_agent_violations.log
    $SUDO chmod 644 /var/log/ai_agent_operations.log
    $SUDO chmod 644 /var/log/ai_agent_violations.log
    echo "✅ Monitoring logs created in /var/log/"
else
    mkdir -p ~/.local/log
    touch ~/.local/log/ai_agent_operations.log
    touch ~/.local/log/ai_agent_violations.log
    chmod 644 ~/.local/log/ai_agent_operations.log
    chmod 644 ~/.local/log/ai_agent_violations.log
    echo "✅ Monitoring logs created in ~/.local/log/"
fi
echo ""

# Create git hook template
echo "6. Creating git hook template..."
HOOK_TEMPLATE_DIR="$HOME/.git-template"
mkdir -p "$HOOK_TEMPLATE_DIR/hooks"
cat << 'EOF' > "$HOOK_TEMPLATE_DIR/hooks/pre-commit"
#!/bin/bash
# Git pre-commit hook to enforce runbook toolkit usage

ARTIFACTS_DIR="/tmp/artifacts"
TOOLKIT_MARKER=".runbook_toolkit_used"

# Check if artifacts directory exists
if [ ! -d "$ARTIFACTS_DIR" ]; then
    echo "⚠️  Warning: No runbook toolkit artifacts directory found"
    echo "Consider using the runbook toolkit for modifications"
    exit 0
fi

# Check for toolkit usage marker
if [ ! -f "$ARTIFACTS_DIR/$TOOLKIT_MARKER" ]; then
    echo "⚠️  Warning: Changes may not have been made using runbook toolkit"
    echo "Recommended: Use python -m runbook_toolkit execute --plan PLAN.json --artifacts-dir $ARTIFACTS_DIR"
    echo "To bypass this warning, run: git commit --no-verify"
    # exit 1  # Uncomment to enforce strictly
    exit 0
fi

# Verify audit trail exists
if [ ! -f "$ARTIFACTS_DIR/audit_log.jsonl" ]; then
    echo "⚠️  Warning: No audit trail found for these changes"
    echo "Consider using the runbook toolkit for proper audit trail"
    exit 0
fi

echo "✅ Runbook toolkit usage verified"
exit 0
EOF
chmod +x "$HOOK_TEMPLATE_DIR/hooks/pre-commit"
echo "✅ Git hook template created: $HOOK_TEMPLATE_DIR/hooks/pre-commit"
echo "   To enable globally: git config --global init.templatedir $HOOK_TEMPLATE_DIR"
echo ""

# Test toolkit availability
echo "7. Testing toolkit availability..."
if [ -d "$TOOLKIT_PATH" ]; then
    cd "$TOOLKIT_PATH"
    if python -m runbook_toolkit --help &>/dev/null; then
        echo "✅ Runbook toolkit is available and functional"
    else
        echo "⚠️  Warning: Runbook toolkit found but not functional"
        echo "   Check Python dependencies and configuration"
    fi
else
    echo "❌ Error: Runbook toolkit not found at $TOOLKIT_PATH"
    echo "   Please ensure the toolkit is properly installed"
fi
echo ""

# Create sample PLAN.json for testing
echo "8. Creating sample PLAN.json for testing..."
cat << 'EOF' > "$ARTIFACTS_DIR/SAMPLE_PLAN.json"
{
  "goal": "Sample runbook toolkit operation",
  "description": "Template for testing runbook toolkit functionality",
  "version": "1.0",
  "scope": {
    "include": ["/tmp/test/**"],
    "exclude": []
  },
  "operations": [
    {
      "type": "file_create",
      "description": "Create test file",
      "file": "/tmp/test_runbook.txt",
      "content": "Test file created by runbook toolkit"
    }
  ],
  "verification": {
    "post_execution": [
      {
        "type": "file_exists",
        "file": "/tmp/test_runbook.txt"
      }
    ]
  },
  "optimization": {
    "enable_caching": true,
    "enable_metrics": true,
    "enable_parallel": false
  }
}
EOF
echo "✅ Sample PLAN.json created: $ARTIFACTS_DIR/SAMPLE_PLAN.json"
echo ""

# Summary
echo "=== Enforcement Setup Complete ==="
echo ""
echo "Installed Components:"
if [ -n "$SUDO" ]; then
    echo "  • Environment variables: /etc/profile.d/runbook_toolkit.sh"
    echo "  • Agent configuration: $CONFIG_FILE"
    echo "  • System policy: $POLICY_FILE"
    echo "  • Monitoring logs: /var/log/ai_agent_operations.log"
else
    echo "  • Environment variables: ~/.bashrc"
    echo "  • Agent configuration: ~/.config/ai_agent_config.json"
    echo "  • System policy: ~/.config/ai_agent_policy.conf"
    echo "  • Monitoring logs: ~/.local/log/ai_agent_operations.log"
fi
echo "  • Git hook template: $HOOK_TEMPLATE_DIR/hooks/pre-commit"
echo "  • Sample plan: $ARTIFACTS_DIR/SAMPLE_PLAN.json"
echo ""
echo "Next Steps:"
echo "1. Source environment variables: source ~/.bashrc (or /etc/profile.d/runbook_toolkit.sh)"
echo "2. Test toolkit: cd $TOOLKIT_PATH && python -m runbook_toolkit execute --plan $ARTIFACTS_DIR/SAMPLE_PLAN.json --artifacts-dir $ARTIFACTS_DIR"
echo "3. Enable git hooks: git config --global init.templatedir $HOOK_TEMPLATE_DIR"
echo "4. Review enforcement strategy: cat $TOOLKIT_PATH/ENFORCEMENT_STRATEGY.md"
echo ""
echo "For advanced enforcement features, see: $TOOLKIT_PATH/ENFORCEMENT_STRATEGY.md"
echo ""
echo "Enforcement mode: STRICT"
echo "Artifacts directory: $ARTIFACTS_DIR"
echo "Toolkit path: $TOOLKIT_PATH"
echo ""