#!/usr/bin/env python3
"""toolkit_health.py — Runbook Toolkit Health Check Module"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class HealthCheckResult:
    """Data class for health check results."""
    component: str
    status: str  # healthy, warning, error
    message: str
    details: Optional[Dict] = None

class ToolkitHealthChecker:
    """Comprehensive health checking for runbook toolkit."""
    
    def __init__(self, toolkit_path: str = "/home/user/AI_Agents/runbook_toolkit"):
        self.toolkit_path = toolkit_path
        self.results: List[HealthCheckResult] = []
    
    def check_python_version(self) -> HealthCheckResult:
        """Check Python version compatibility."""
        version = sys.version_info
        required = (3, 8)
        
        if version >= required:
            return HealthCheckResult(
                component="python_version",
                status="healthy",
                message=f"Python {version.major}.{version.minor}.{version.micro} (required: {required[0]}.{required[1]}+)"
            )
        else:
            return HealthCheckResult(
                component="python_version",
                status="error",
                message=f"Python {version.major}.{version.minor}.{version.micro} (required: {required[0]}.{required[1]}+)"
            )
    
    def check_dependencies(self) -> HealthCheckResult:
        """Check required Python dependencies."""
        required_packages = ["yaml", "requests"]
        missing = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        
        if not missing:
            return HealthCheckResult(
                component="dependencies",
                status="healthy",
                message=f"All dependencies installed: {', '.join(required_packages)}"
            )
        else:
            return HealthCheckResult(
                component="dependencies",
                status="error",
                message=f"Missing dependencies: {', '.join(missing)}",
                details={"missing": missing, "install_command": f"pip install {' '.join(missing)}"}
            )
    
    def check_directories(self) -> HealthCheckResult:
        """Check required directories exist."""
        required_dirs = ["templates", "runbooks", "asterisk"]
        missing = []
        inaccessible = []
        
        for dir_name in required_dirs:
            dir_path = os.path.join(self.toolkit_path, dir_name)
            if not os.path.exists(dir_path):
                missing.append(dir_name)
            elif not os.access(dir_path, os.R_OK):
                inaccessible.append(dir_name)
        
        if not missing and not inaccessible:
            return HealthCheckResult(
                component="directories",
                status="healthy",
                message=f"All directories accessible: {', '.join(required_dirs)}"
            )
        else:
            issues = []
            if missing:
                issues.append(f"missing: {', '.join(missing)}")
            if inaccessible:
                issues.append(f"inaccessible: {', '.join(inaccessible)}")
            
            return HealthCheckResult(
                component="directories",
                status="error",
                message=f"Directory issues: {'; '.join(issues)}",
                details={"missing": missing, "inaccessible": inaccessible}
            )
    
    def check_permissions(self) -> HealthCheckResult:
        """Check file permissions for toolkit files."""
        main_file = os.path.join(self.toolkit_path, "__main__.py")
        python_files = list(Path(self.toolkit_path).glob("*.py"))
        
        issues = []
        
        # Check main file is executable
        if os.path.exists(main_file):
            if not os.access(main_file, os.X_OK):
                issues.append("__main__.py not executable")
        else:
            issues.append("__main__.py not found")
        
        # Check Python files are readable
        for py_file in python_files:
            if not os.access(py_file, os.R_OK):
                issues.append(f"{py_file.name} not readable")
        
        if not issues:
            return HealthCheckResult(
                component="permissions",
                status="healthy",
                message=f"All {len(python_files)} Python files have correct permissions"
            )
        else:
            return HealthCheckResult(
                component="permissions",
                status="warning",
                message=f"Permission issues: {'; '.join(issues)}",
                details={"issues": issues}
            )
    
    def check_templates(self) -> HealthCheckResult:
        """Validate JSON templates in templates directory."""
        templates_dir = os.path.join(self.toolkit_path, "templates")
        
        if not os.path.exists(templates_dir):
            return HealthCheckResult(
                component="templates",
                status="error",
                message="Templates directory not found"
            )
        
        json_files = list(Path(templates_dir).glob("*.json"))
        invalid_files = []
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                invalid_files.append(f"{json_file.name}: {str(e)}")
        
        if not invalid_files:
            return HealthCheckResult(
                component="templates",
                status="healthy",
                message=f"All {len(json_files)} JSON templates are valid"
            )
        else:
            return HealthCheckResult(
                component="templates",
                status="error",
                message=f"Invalid JSON templates: {len(invalid_files)} files",
                details={"invalid_files": invalid_files}
            )
    
    def check_cache(self) -> HealthCheckResult:
        """Check cache directory status."""
        cache_dir = os.path.expanduser("~/.runbook_cache")
        max_size_mb = 100
        
        if not os.path.exists(cache_dir):
            return HealthCheckResult(
                component="cache",
                status="warning",
                message="Cache directory does not exist (will be created on first use)"
            )
        
        # Check cache size
        total_size = sum(
            os.path.getsize(os.path.join(cache_dir, f))
            for f in os.listdir(cache_dir)
            if os.path.isfile(os.path.join(cache_dir, f))
        )
        
        size_mb = total_size / (1024 * 1024)
        
        if size_mb > max_size_mb:
            return HealthCheckResult(
                component="cache",
                status="warning",
                message=f"Cache size {size_mb:.1f}MB exceeds limit {max_size_mb}MB",
                details={"size_mb": size_mb, "limit_mb": max_size_mb}
            )
        else:
            return HealthCheckResult(
                component="cache",
                status="healthy",
                message=f"Cache size {size_mb:.1f}MB within limit {max_size_mb}MB"
            )
    
    def check_metrics(self) -> HealthCheckResult:
        """Check metrics directory and recent data."""
        metrics_dir = os.path.expanduser("~/.runbook_metrics")
        
        if not os.path.exists(metrics_dir):
            return HealthCheckResult(
                component="metrics",
                status="warning",
                message="Metrics directory does not exist (will be created on first use)"
            )
        
        # Check for recent metrics files
        metrics_files = list(Path(metrics_dir).glob("metrics_*.json"))
        
        if not metrics_files:
            return HealthCheckResult(
                component="metrics",
                status="warning",
                message="No metrics files found"
            )
        
        # Check for recent metrics (last 7 days)
        import time
        recent_files = [
            f for f in metrics_files
            if time.time() - f.stat().st_mtime < 7 * 24 * 3600
        ]
        
        if recent_files:
            return HealthCheckResult(
                component="metrics",
                status="healthy",
                message=f"Found {len(recent_files)} recent metrics files (last 7 days)"
            )
        else:
            return HealthCheckResult(
                component="metrics",
                status="warning",
                message=f"Found {len(metrics_files)} metrics files, but none recent (last 7 days)"
            )
    
    def check_disk_space(self) -> HealthCheckResult:
        """Check available disk space."""
        import shutil
        
        disk_usage = shutil.disk_usage(self.toolkit_path)
        free_gb = disk_usage.free / (1024**3)
        total_gb = disk_usage.total / (1024**3)
        usage_percent = (disk_usage.used / disk_usage.total) * 100
        
        if free_gb < 1:
            return HealthCheckResult(
                component="disk_space",
                status="error",
                message=f"Critical disk space: {free_gb:.1f}GB free ({usage_percent:.1f}% used)",
                details={"free_gb": free_gb, "total_gb": total_gb, "usage_percent": usage_percent}
            )
        elif free_gb < 2:
            return HealthCheckResult(
                component="disk_space",
                status="warning",
                message=f"Low disk space: {free_gb:.1f}GB free ({usage_percent:.1f}% used)",
                details={"free_gb": free_gb, "total_gb": total_gb, "usage_percent": usage_percent}
            )
        else:
            return HealthCheckResult(
                component="disk_space",
                status="healthy",
                message=f"Disk space OK: {free_gb:.1f}GB free ({usage_percent:.1f}% used)"
            )
    
    def run_all_checks(self) -> List[HealthCheckResult]:
        """Run all health checks and return results."""
        self.results = [
            self.check_python_version(),
            self.check_dependencies(),
            self.check_directories(),
            self.check_permissions(),
            self.check_templates(),
            self.check_cache(),
            self.check_metrics(),
            self.check_disk_space()
        ]
        return self.results
    
    def generate_report(self) -> Dict:
        """Generate comprehensive health report."""
        self.run_all_checks()
        
        healthy = sum(1 for r in self.results if r.status == "healthy")
        warnings = sum(1 for r in self.results if r.status == "warning")
        errors = sum(1 for r in self.results if r.status == "error")
        
        overall_status = "healthy" if errors == 0 else "error" if warnings == 0 else "warning"
        
        return {
            "timestamp": subprocess.check_output(["date", "-Iseconds"]).decode().strip(),
            "overall_status": overall_status,
            "total_checks": len(self.results),
            "healthy": healthy,
            "warnings": warnings,
            "errors": errors,
            "checks": [asdict(result) for result in self.results]
        }

def main():
    """CLI entry point for health check."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Runbook Toolkit Health Check")
    parser.add_argument("--toolkit-path", default="/home/user/AI_Agents/runbook_toolkit", 
                       help="Path to runbook toolkit directory")
    parser.add_argument("--output", help="Output file for JSON report")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    checker = ToolkitHealthChecker(args.toolkit_path)
    report = checker.generate_report()
    
    # Print summary
    print(f"Overall Status: {report['overall_status'].upper()}")
    print(f"Healthy: {report['healthy']}/{report['total_checks']}")
    print(f"Warnings: {report['warnings']}/{report['total_checks']}")
    print(f"Errors: {report['errors']}/{report['total_checks']}")
    
    if args.verbose:
        print("\nDetailed Results:")
        for check in report['checks']:
            status_symbol = "✓" if check['status'] == "healthy" else "⚠" if check['status'] == "warning" else "✗"
            print(f"  {status_symbol} {check['component']}: {check['message']}")
            if check.get('details'):
                print(f"      Details: {check['details']}")
    
    # Save report if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to: {args.output}")
    
    # Exit with error code if there are errors
    if report['errors'] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()