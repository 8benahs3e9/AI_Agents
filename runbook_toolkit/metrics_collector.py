#!/usr/bin/env python3
"""metrics_collector.py — Performance Metrics and Optimization Analytics"""

import json
import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

class MetricsCollector:
    """Collects and analyzes performance metrics for optimization insights."""
    
    def __init__(self, metrics_dir: Optional[str] = None):
        self.metrics_dir = metrics_dir or os.path.join(os.path.expanduser("~"), ".runbook_metrics")
        os.makedirs(self.metrics_dir, exist_ok=True)
        
        self.tool_call_counts: Dict[str, int] = defaultdict(int)
        self.operation_timings: Dict[str, List[float]] = defaultdict(list)
        self.resource_usage: List[Dict] = []
        self.tranche_stats: List[Dict] = []
        self.cache_stats: List[Dict] = []
        self.failure_stats: Dict[str, int] = defaultdict(int)
        self.attempt_stats: Dict[str, int] = defaultdict(int)
        
        self.session_start = datetime.now(timezone.utc)
        self._load_historical_stats()
    
    def _load_historical_stats(self):
        """Load historical statistics from disk."""
        stats_path = os.path.join(self.metrics_dir, "historical_stats.json")
        if os.path.exists(stats_path):
            try:
                with open(stats_path, "r") as fh:
                    data = json.load(fh)
                    self.failure_stats = defaultdict(int, data.get("failure_stats", {}))
                    self.attempt_stats = defaultdict(int, data.get("attempt_stats", {}))
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_historical_stats(self):
        """Save historical statistics to disk."""
        stats_path = os.path.join(self.metrics_dir, "historical_stats.json")
        with open(stats_path, "w") as fh:
            json.dump({
                "failure_stats": dict(self.failure_stats),
                "attempt_stats": dict(self.attempt_stats),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }, fh, indent=2)
    
    def record_operation(self, op_type: str, duration: float, tool_calls: int, success: bool = True):
        """Record metrics for a single operation."""
        self.tool_call_counts[op_type] += tool_calls
        self.operation_timings[op_type].append(duration)
        self.attempt_stats[op_type] += 1
        
        if not success:
            self.failure_stats[op_type] += 1
    
    def record_tranche(self, tranche_num: int, size: int, duration: float, success: bool):
        """Record metrics for a tranche execution."""
        self.tranche_stats.append({
            "tranche_num": tranche_num,
            "size": size,
            "duration": duration,
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def record_cache_stats(self, cache_stats: Dict):
        """Record cache performance statistics."""
        self.cache_stats.append({
            **cache_stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def record_resource_usage(self, cpu_percent: float, memory_percent: float, disk_free: int):
        """Record system resource usage."""
        self.resource_usage.append({
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "disk_free": disk_free,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def get_operation_summary(self) -> Dict[str, Any]:
        """Get summary statistics for each operation type."""
        summary = {}
        for op_type in self.tool_call_counts:
            timings = self.operation_timings[op_type]
            summary[op_type] = {
                "total_calls": self.tool_call_counts[op_type],
                "total_time": sum(timings),
                "avg_time": sum(timings) / len(timings) if timings else 0,
                "min_time": min(timings) if timings else 0,
                "max_time": max(timings) if timings else 0,
                "count": len(timings),
                "failures": self.failure_stats[op_type],
                "attempts": self.attempt_stats[op_type],
                "success_rate": (self.attempt_stats[op_type] - self.failure_stats[op_type]) / self.attempt_stats[op_type] if self.attempt_stats[op_type] > 0 else 0
            }
        return summary
    
    def get_tranche_summary(self) -> Dict[str, Any]:
        """Get summary statistics for tranche execution."""
        if not self.tranche_stats:
            return {}
        
        successful_tranches = [t for t in self.tranche_stats if t["success"]]
        failed_tranches = [t for t in self.tranche_stats if not t["success"]]
        
        return {
            "total_tranches": len(self.tranche_stats),
            "successful": len(successful_tranches),
            "failed": len(failed_tranches),
            "avg_size": sum(t["size"] for t in self.tranche_stats) / len(self.tranche_stats),
            "avg_duration": sum(t["duration"] for t in self.tranche_stats) / len(self.tranche_stats),
            "success_rate": len(successful_tranches) / len(self.tranche_stats) if self.tranche_stats else 0
        }
    
    def get_cache_summary(self) -> Dict[str, Any]:
        """Get summary statistics for cache performance."""
        if not self.cache_stats:
            return {}
        
        latest = self.cache_stats[-1]
        return {
            "latest_entries": latest.get("entries", 0),
            "latest_size_mb": latest.get("total_size_mb", 0),
            "avg_hit_rate": self._calculate_avg_hit_rate(),
            "total_cached_items": sum(c.get("in_memory_hashes", 0) + c.get("in_memory_contents", 0) for c in self.cache_stats)
        }
    
    def _calculate_avg_hit_rate(self) -> float:
        """Calculate average cache hit rate."""
        if not self.cache_stats:
            return 0.0
        
        # Simple estimation based on cache stats
        total_requests = sum(c.get("in_memory_hashes", 0) + c.get("in_memory_contents", 0) for c in self.cache_stats)
        if total_requests == 0:
            return 0.0
        
        # This is a simplified calculation - in practice you'd track actual hits/misses
        return min(0.85, total_requests / (total_requests + len(self.cache_stats) * 10))
    
    def get_optimization_suggestions(self) -> List[str]:
        """Generate optimization suggestions based on collected metrics."""
        suggestions = []
        
        # Check file read operations
        file_reads = self.tool_call_counts.get("file_read", 0)
        if file_reads > 100:
            suggestions.append("High file read count - ensure caching is enabled for better performance")
        
        # Check operation timings
        op_summary = self.get_operation_summary()
        for op_type, stats in op_summary.items():
            if stats["avg_time"] > 30:
                suggestions.append(f"{op_type} operations averaging {stats['avg_time']:.1f}s - consider batching or parallelization")
            if stats["success_rate"] < 0.8:
                suggestions.append(f"{op_type} has low success rate ({stats['success_rate']:.1%}) - review operation parameters")
        
        # Check tranche performance
        tranche_summary = self.get_tranche_summary()
        if tranche_summary.get("success_rate", 1.0) < 0.9:
            suggestions.append("Tranche success rate below 90% - consider reducing tranche size")
        
        # Check cache performance
        cache_summary = self.get_cache_summary()
        if cache_summary.get("latest_size_mb", 0) > 50:
            suggestions.append("Cache size > 50MB - consider cache cleanup or size limits")
        
        # Check resource usage
        if self.resource_usage:
            avg_memory = sum(r["memory_percent"] for r in self.resource_usage) / len(self.resource_usage)
            if avg_memory > 80:
                suggestions.append("High memory usage detected - consider reducing concurrent operations")
        
        return suggestions
    
    def predict_failure_probability(self, operation_type: str) -> float:
        """Predict failure probability based on historical data."""
        if self.attempt_stats[operation_type] == 0:
            return 0.0  # No data, assume safe
        
        return self.failure_stats[operation_type] / self.attempt_stats[operation_type]
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get comprehensive session summary."""
        duration = (datetime.now(timezone.utc) - self.session_start).total_seconds()
        
        return {
            "session_duration_seconds": duration,
            "session_start": self.session_start.isoformat(),
            "total_tool_calls": sum(self.tool_call_counts.values()),
            "operation_summary": self.get_operation_summary(),
            "tranche_summary": self.get_tranche_summary(),
            "cache_summary": self.get_cache_summary(),
            "optimization_suggestions": self.get_optimization_suggestions(),
            "resource_samples": len(self.resource_usage)
        }
    
    def export_metrics(self, filepath: Optional[str] = None) -> str:
        """Export all metrics to a JSON file."""
        if filepath is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.metrics_dir, f"metrics_{timestamp}.json")
        
        with open(filepath, "w") as fh:
            json.dump({
                "session_summary": self.get_session_summary(),
                "tool_call_counts": dict(self.tool_call_counts),
                "operation_timings": dict(self.operation_timings),
                "tranche_stats": self.tranche_stats,
                "cache_stats": self.cache_stats,
                "resource_usage": self.resource_usage,
                "failure_stats": dict(self.failure_stats),
                "attempt_stats": dict(self.attempt_stats)
            }, fh, indent=2)
        
        self._save_historical_stats()
        return filepath
    
    def reset_session(self):
        """Reset current session metrics while keeping historical stats."""
        self.tool_call_counts.clear()
        self.operation_timings.clear()
        self.resource_usage.clear()
        self.tranche_stats.clear()
        self.cache_stats.clear()
        self.session_start = datetime.now(timezone.utc)