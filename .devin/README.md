# AI_Agents Workspace Configuration

This directory contains all configuration for the AI_Agents workspace.

## Runbook Toolkit Enforcement

The `runbook-toolkit-enforcer` skill ensures all AI agents use the runbook toolkit for system modifications when working in this workspace.

## Configuration Structure

All workspace-specific configuration is consolidated in this `.devin/` directory:

- `skills/runbook-toolkit-enforcer/SKILL.md` - Runbook toolkit enforcement skill
- `README.md` - This documentation file

## Runbook Toolkit

- **Toolkit Path**: `/home/user/AI_Agents/runbook_toolkit`
- **Artifacts Directory**: `/tmp/artifacts`
- **Enforcement Mode**: Strict

## Documentation

- Full instructions: `/home/user/AI_Agents/runbook_toolkit/AGENT_INSTRUCTIONS.md`
- Enforcement strategy: `/home/user/AI_Agents/runbook_toolkit/ENFORCEMENT_STRATEGY.md`
- Quick start: `/home/user/AI_Agents/runbook_toolkit/ENFORCEMENT_QUICKSTART.md`
