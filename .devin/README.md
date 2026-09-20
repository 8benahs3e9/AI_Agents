# AI_Agents Workspace Configuration

This directory contains configuration for automatic runbook toolkit enforcement when working in the AI_Agents workspace.

## Automatic Enforcement

When you start a chat session in the AI_Agents directory or subdirectories, the following will happen automatically:

1. **Environment Setup**: Runbook toolkit environment variables are set
2. **Skill Activation**: The runbook-toolkit-enforcer skill activates automatically
3. **User Notification**: You'll be notified that runbook toolkit instructions are being applied
4. **Enforcement**: All system modifications will use the runbook toolkit workflow

## Current Configuration

- **Toolkit Path**: `/home/user/AI_Agents/runbook_toolkit`
- **Artifacts Directory**: `/tmp/artifacts`
- **Enforcement Mode**: Strict
- **Active Directories**: `/home/user/AI_Agents` and all subdirectories
- **Allowed Direct Commands**: read, grep, find, ls, cat, head, tail
- **Blocked Direct Commands**: rm, apt, systemctl, chmod, chown, iptables

## How It Works

1. **Detection**: The system detects when working in `/home/user/AI_Agents/`
2. **Skill Activation**: The `runbook-toolkit-enforcer` skill activates automatically
3. **Notification**: User is notified that enforcement is active
4. **Workflow Enforcement**: All modifications follow the runbook toolkit workflow:
   - INSPECTION → PLANNING → VALIDATION → APPROVAL → EXECUTION → VERIFICATION → DOCUMENTATION

## Files

- `session_init.sh` - Environment setup script
- Configuration in `~/.config/devin/config.json`
- Skill definition in `~/.config/devin/skills/runbook-toolkit-enforcer/SKILL.md`

## Manual Activation

If automatic activation doesn't work, you can manually source the environment:

```bash
source /home/user/AI_Agents/.devin/session_init.sh
```

## Emergency Override

If you need to bypass enforcement temporarily:

```bash
export RUNBOOK_EMERGENCY_OVERRIDE=true
export RUNBOOK_OVERRIDE_REASON="Reason for override"
export RUNBOOK_OVERRIDE_APPROVED_BY="admin@example.com"
```

Remember to disable the override after emergency operations:

```bash
unset RUNBOOK_EMERGENCY_OVERRIDE
```

## Documentation

- Full instructions: `/home/user/AI_Agents/runbook_toolkit/AGENT_INSTRUCTIONS.md`
- Enforcement strategy: `/home/user/AI_Agents/runbook_toolkit/ENFORCEMENT_STRATEGY.md`
- Quick start: `/home/user/AI_Agents/runbook_toolkit/ENFORCEMENT_QUICKSTART.md`
