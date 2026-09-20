# Runbook Toolkit Quickstart

## Token Savings Focus

The runbook toolkit reduces tool calls from 17-26 to 3-4 per operation (~80% reduction).

## Quick Start

```bash
# Create a plan
cd /home/user/AI_Agents/runbook_toolkit
python -m runbook_toolkit execute --plan /tmp/artifacts/PLAN.json --artifacts-dir /tmp/artifacts
```

## Optimization

- Use `--parallel` for independent operations
- Caching is enabled by default
- Review metrics: `python -m runbook_toolkit show-metrics`

## Documentation

- Token-saving instructions: `AGENT_INSTRUCTIONS.md`
- Optimization guide: `OPTIMIZATION_GUIDE.md`
