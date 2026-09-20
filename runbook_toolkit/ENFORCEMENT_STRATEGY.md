# Runbook Toolkit Strategy

## Token Savings Priority

Primary goal: Reduce tool calls from 17-26 to 3-4 per operation (~80% reduction).

## Key Mechanisms

1. **Batch Processing**: Handle multiple operations in single toolkit call
2. **Caching**: Avoid repeated expensive operations (enabled by default)
3. **Parallel Execution**: Use `--parallel` flag for independent operations
4. **Optimization Metrics**: Review with `python -m runbook_toolkit show-metrics`

## Usage Pattern

Instead of multiple direct commands:
```bash
# Inefficient: Multiple tool calls
exec command="ls -la"
exec command="cat file.txt" 
exec command="grep pattern file.txt"
```

Use toolkit batching:
```bash
# Efficient: Single toolkit call
python -m runbook_toolkit execute --plan PLAN.json --artifacts-dir /tmp/artifacts
```

## Documentation

- Optimization details: `OPTIMIZATION_GUIDE.md`
- Quick instructions: `AGENT_INSTRUCTIONS.md`
