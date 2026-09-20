# Runbook Toolkit Optimization Guide

## Overview

The runbook toolkit now includes advanced optimization features designed to reduce tool call usage, improve performance, and provide actionable insights for efficient automation.

## New Features

### 1. Adaptive Tranche Sizing

**Purpose**: Dynamically adjust batch sizes based on operation complexity and system resources.

**How it works**:
- Analyzes operation types (apt_install, service_restart, delete are considered complex)
- Evaluates total file sizes in each tranche
- Checks available disk space
- Considers remaining tool call quota
- Automatically adjusts tranche size between 1-50 operations

**Benefits**:
- Larger tranches for simple operations → fewer tool calls
- Smaller tranches for complex operations → better error isolation
- Resource-aware sizing → prevents failures due to resource constraints

**Usage**: Automatically enabled by default during plan execution.

### 2. Smart Caching Layer

**Purpose**: Eliminate redundant file operations and computations.

**Cache types**:
- **File hashes**: Avoid recomputing SHA256 hashes for unchanged files
- **File contents**: Cache file reads to avoid repeated disk I/O
- **Validation results**: Cache dry-run and validation outcomes

**Features**:
- TTL-based cache invalidation (default 2 hours)
- Automatic cache cleanup when size limit exceeded (default 100MB)
- In-memory cache for frequently accessed data
- Persistent disk cache for session continuity

**Benefits**:
- Reduces file I/O operations significantly
- Speeds up hash verification and rollback operations
- Minimizes redundant computations

**Usage**: Enabled by default (`--no-cache` to disable)

### 3. Metrics Collection & Analytics

**Purpose**: Track performance and provide optimization recommendations.

**Metrics tracked**:
- Tool call counts per operation type
- Operation timing statistics (avg, min, max)
- Tranche execution performance
- Cache hit rates and efficiency
- Resource usage (CPU, memory, disk)
- Failure rates and success patterns

**Features**:
- Historical failure analysis
- Optimization suggestions based on collected data
- Session summaries with actionable insights
- JSON export for external analysis

**Benefits**:
- Data-driven optimization decisions
- Identification of performance bottlenecks
- Predictive failure analysis
- Continuous improvement guidance

**Usage**: 
- Enabled by default (`--no-metrics` to disable)
- View suggestions: `python -m runbook_toolkit show-metrics`
- Analyze specific session: `python -m runbook_toolkit show-metrics --metrics-file <path>`

### 4. Resource-Aware Throttling

**Purpose**: Prevent failures due to resource constraints.

**Checks performed**:
- Disk space availability (critical: <1GB, warning: <2GB)
- Memory usage (critical: >90%)
- CPU load monitoring

**Features**:
- Pre-execution resource validation
- Automatic abort if resources insufficient
- Resource usage tracking for metrics
- Configurable thresholds

**Benefits**:
- Prevents mid-execution failures
- Protects system stability
- Provides early warning of resource issues

**Usage**: Automatically enabled during pre-flight checks.

### 5. Parallel Processing

**Purpose**: Process independent operations concurrently.

**How it works**:
- Identifies operations that can run in parallel (different files, independent packages)
- Uses thread pool execution (max 3 workers)
- Maintains operation ordering where dependencies exist
- Falls back to sequential processing if dependencies detected

**Features**:
- Safe parallelization with dependency awareness
- Configurable worker pool size
- Automatic error handling and rollback
- Metrics tracking for parallel operations

**Benefits**:
- Significant speedup for independent operations
- Better resource utilization
- Reduced total execution time

**Usage**: Enable with `--parallel` flag

## Command Line Options

### Execute Command Enhancements

```bash
python -m runbook_toolkit execute \
  --plan /tmp/artifacts/PLAN.json \
  --artifacts-dir /tmp/artifacts \
  --no-cache          \  # Disable caching
  --no-metrics         \  # Disable metrics collection  
  --parallel           \  # Enable parallel processing
```

### New Commands

```bash
# Show optimization suggestions
python -m runbook_toolkit show-metrics

# Analyze specific metrics file
python -m runbook_toolkit show-metrics --metrics-file /tmp/artifacts/session_metrics.json
```

## Performance Impact

### Expected Improvements

**Tool Call Reduction**:
- Caching: 30-50% reduction in file operations
- Adaptive sizing: 20-40% reduction in total operations
- Parallel processing: 40-60% faster execution for independent ops

**Resource Efficiency**:
- Better disk space management
- Reduced memory pressure through caching
- Optimized CPU utilization with parallel processing

**Reliability**:
- Resource-aware throttling prevents failures
- Metrics enable proactive optimization
- Adaptive sizing reduces error propagation

## Configuration

### Cache Configuration

Cache settings are managed in `~/.runbook_cache/`:
- Default max size: 100MB
- Default TTL: 2 hours
- Automatic cleanup when size limit reached

### Metrics Storage

Metrics are stored in `~/.runbook_metrics/`:
- Historical statistics persist across sessions
- Session-specific exports to artifacts directory
- JSON format for easy analysis

### Resource Thresholds

Default thresholds (configurable in code):
- Disk critical: <1GB free
- Disk warning: <2GB free  
- Memory critical: >90% usage
- Tranche size range: 1-50 operations

## Best Practices

### When to Use Each Feature

**Always enable**:
- Adaptive tranche sizing (automatic)
- Resource-aware throttling (automatic)

**Enable for performance**:
- Caching (default enabled)
- Metrics collection (default enabled)

**Enable when appropriate**:
- Parallel processing (use for independent operations)

**Disable when**:
- Caching: Debugging cache-related issues
- Metrics: Minimal resource usage required
- Parallel: Operations have dependencies or resource constraints

### Monitoring and Optimization

1. **Review metrics regularly**: Use `show-metrics` to identify bottlenecks
2. **Analyze failure patterns**: High failure rates indicate need for plan adjustment
3. **Monitor cache efficiency**: Low hit rates suggest cache configuration issues
4. **Check resource usage**: High resource consumption may indicate need for throttling

### Troubleshooting

**High tool call usage**:
- Ensure caching is enabled
- Check cache hit rates in metrics
- Review adaptive sizing logs

**Slow execution**:
- Enable parallel processing for independent operations
- Review operation timing in metrics
- Check for resource bottlenecks

**Resource exhaustion**:
- Review resource health checks in logs
- Consider reducing tranche size
- Monitor memory and disk usage patterns

## Migration Guide

### Existing Plans

No changes required to existing PLAN.json files. All optimizations are transparent to plan structure.

### Existing Code

If you have custom code using TrancheProcessor:

```python
# Old usage
processor = TrancheProcessor(plan_path="PLAN.json", artifacts_dir="/tmp/artifacts")

# New usage (with defaults)
processor = TrancheProcessor(
    plan_path="PLAN.json", 
    artifacts_dir="/tmp/artifacts",
    enable_caching=True,      # New: default True
    enable_metrics=True,      # New: default True  
    enable_parallel=False     # New: default False
)
```

## Future Enhancements

Planned improvements:
- Dependency graph analysis for smarter parallelization
- Machine learning-based tranche size optimization
- Predictive resource allocation
- Advanced cache warming strategies
- Real-time performance dashboards

## Support

For issues or questions about optimization features:
1. Check metrics output for diagnostic information
2. Review cache statistics in `~/.runbook_cache/`
3. Examine session metrics in artifacts directory
4. Consult optimization suggestions from `show-metrics`