# Runbook Toolkit Summary

## Token Savings Features

- **Batch Operations**: Handle multiple changes in single call
- **Caching**: Skip repeated operations (default enabled)
- **Parallel Processing**: Use `--parallel` for independent tasks
- **Metrics**: Track optimization with `show-metrics`

## Key Components

- Security remediation templates
- Asterisk troubleshooting tools
- Optimization guidance

## Performance

- Normal: 17-26 tool calls per operation
- With toolkit: 3-4 tool calls per operation
- **Savings: ~80% reduction**

## Usage

```bash
python -m runbook_toolkit execute --plan /tmp/artifacts/PLAN.json --artifacts-dir /tmp/artifacts --parallel
```
