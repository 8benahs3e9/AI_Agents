# AI_Agents Workspace Configuration

## Token-Saving Mode

This workspace uses runbook toolkit for token-efficient operations:
- **Tool call reduction**: 17-26 → 3-4 per operation (80% savings)
- **Batch processing**: Handle multiple operations in single call
- **Caching**: Avoid repeated expensive operations

## Usage

When modifying files or running commands in this workspace, use the runbook toolkit:
```bash
python -m runbook_toolkit execute --plan /tmp/artifacts/PLAN.json --artifacts-dir /tmp/artifacts
```

## Configuration

- `TOOLKIT_MODE` - Token-saving instructions (minimal overhead)
- `README.md` - This file

## Toolkit Location

`/home/user/AI_Agents/runbook_toolkit`
