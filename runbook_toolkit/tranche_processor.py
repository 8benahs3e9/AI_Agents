#!/usr/bin/env python3
"""tranche_processor.py — Orchestrates the Full Tranche Lifecycle"""

import hashlib
import json
import os
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import List, Dict, Optional

from audit_chain import AuditLogger
from secret_scanner import SecretScanner
from state_manager import StateManager
from cache_manager import CacheManager
from metrics_collector import MetricsCollector

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML is required: pip install pyyaml")

class TrancheProcessor:
    MAX_RETRIES = 2
    DEFAULT_TRANCHE_SIZE = 10
    MIN_TRANCHE_SIZE = 1
    MAX_TRANCHE_SIZE = 50

    def __init__(self, plan_path: str, artifacts_dir: str, tranche_size: Optional[int] = None, enable_caching: bool = True, enable_metrics: bool = True, enable_parallel: bool = False):
        self.plan_path = plan_path
        self.artifacts_dir = artifacts_dir
        self.tranche_size = tranche_size or self.DEFAULT_TRANCHE_SIZE
        self.enable_caching = enable_caching
        self.enable_metrics = enable_metrics
        self.enable_parallel = enable_parallel

        os.makedirs(self.artifacts_dir, exist_ok=True)

        self.logger = AuditLogger(artifacts_dir)
        self.scanner = SecretScanner()
        self.state_mgr = StateManager(os.path.join(artifacts_dir, "STATE.md"))
        self.manifest_path = os.path.join(artifacts_dir, "change_manifest.json")
        self.cache = CacheManager() if enable_caching else None
        self.metrics = MetricsCollector() if enable_metrics else None

        self.backups_dir = os.path.join(artifacts_dir, "backups")

    def load_plan(self) -> Dict:
        with open(self.plan_path, "r") as fh:
            return json.load(fh)

    def calculate_adaptive_tranche_size(self, operations: List[Dict], remaining_quota: Optional[int] = None) -> int:
        """Calculate optimal tranche size based on operation complexity and resources."""
        base_size = self.tranche_size
        
        # Factor 1: Operation complexity
        complex_ops = ["apt_install", "service_restart", "delete"]
        complexity_factor = sum(1 for op in operations if op.get("op") in complex_ops)
        
        # Factor 2: File sizes
        total_file_size = 0
        for op in operations:
            path = op.get("path", "")
            if path and os.path.exists(path):
                try:
                    total_file_size += os.path.getsize(path)
                except OSError:
                    pass
        
        size_factor = 0
        if total_file_size > 50_000_000:  # 50MB
            size_factor = 5
        elif total_file_size > 10_000_000:  # 10MB
            size_factor = 2
        
        # Factor 3: Resource constraints
        resource_factor = 0
        try:
            disk_usage = shutil.disk_usage(self.artifacts_dir)
            if disk_usage.free < 2_000_000_000:  # Less than 2GB free
                resource_factor = 3
        except OSError:
            pass
        
        # Factor 4: Tool call budget
        quota_factor = 0
        if remaining_quota and remaining_quota < 20:
            quota_factor = 2
        
        # Calculate adjusted size
        adjusted = base_size - complexity_factor - size_factor - resource_factor - quota_factor
        
        # Clamp to valid range
        return max(self.MIN_TRANCHE_SIZE, min(adjusted, self.MAX_TRANCHE_SIZE))

    def check_resource_health(self) -> Dict:
        """Check system resource health before operations."""
        try:
            disk_usage = shutil.disk_usage(self.artifacts_dir)
            
            # Record resource usage if metrics enabled and psutil available
            memory_critical = False
            if self.metrics:
                try:
                    import psutil
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    memory_percent = psutil.virtual_memory().percent
                    memory_critical = memory_percent > 90
                    self.metrics.record_resource_usage(cpu_percent, memory_percent, disk_usage.free)
                except ImportError:
                    # psutil not available, skip memory/cpu metrics
                    pass
            
            return {
                "disk_critical": disk_usage.free < 1_000_000_000,  # 1GB threshold
                "disk_warning": disk_usage.free < 2_000_000_000,  # 2GB threshold
                "memory_critical": memory_critical,
                "can_proceed": disk_usage.free > 500_000_000 and not memory_critical
            }
        except OSError:
            return {"disk_critical": True, "can_proceed": False}

    @staticmethod
    def plan_hash(plan: Dict) -> str:
        canonical = json.dumps(plan, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def init_manifest(self, plan: Dict) -> Dict:
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, "r") as fh:
                return json.load(fh)

        manifest = {
            "manifest_id": f"manifest-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "inspection_id": plan.get("inspection_id"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "author": "agent",
            "plan_hash": self.plan_hash(plan),
            "changes": [],
            "approval": {"required": True, "approved_by": [], "approval_time": None, "approval_signature": None},
            "secrets_found": [],
        }
        self._write_manifest(manifest)
        return manifest

    def _write_manifest(self, manifest: Dict) -> None:
        tmp = self.manifest_path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(manifest, fh, indent=2)
        os.replace(tmp, self.manifest_path)

    def _read_manifest(self) -> Dict:
        with open(self.manifest_path, "r") as fh:
            return json.load(fh)

    def _append_change(self, change: Dict) -> None:
        manifest = self._read_manifest()
        manifest["changes"].append(change)
        self._write_manifest(manifest)

    def _append_secret_finding(self, finding: Dict) -> None:
        manifest = self._read_manifest()
        manifest["secrets_found"].append(finding)
        self._write_manifest(manifest)

    def _backup_file(self, filepath: str, tranche_num: int) -> str:
        tranche_backup_dir = os.path.join(self.backups_dir, f"tranche_{tranche_num}")
        os.makedirs(tranche_backup_dir, exist_ok=True)
        rel = os.path.relpath(filepath, "/")
        backup_path = os.path.join(tranche_backup_dir, rel.replace(os.sep, "_"))
        shutil.copy2(filepath, backup_path)
        return backup_path

    def _file_hash(self, filepath: str) -> str:
        if self.cache:
            cached_hash = self.cache.get_file_hash(filepath)
            if cached_hash:
                return cached_hash
        
        # Fallback to computation
        h = hashlib.sha256()
        with open(filepath, "rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                h.update(chunk)
        hash_value = h.hexdigest()
        
        # Cache the result
        if self.cache:
            self.cache.file_hashes[filepath] = hash_value
        
        return hash_value

    def _verify_checksum(self, filepath: str, expected: str) -> bool:
        actual = self._file_hash(filepath)
        return actual == expected

    @staticmethod
    def _verify_package(pkg: str) -> bool:
        try:
            result = subprocess.run(["dpkg", "-l", pkg], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    @staticmethod
    def _verify_service(svc: str) -> bool:
        try:
            result = subprocess.run(["systemctl", "is-active", "--quiet", svc], capture_output=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def rollback_tranche(self, tranche_num: int) -> Dict:
        manifest = self._read_manifest()
        tranche_changes = [c for c in manifest["changes"] if c.get("tranche_num") == tranche_num]

        results = []
        for change in tranche_changes:
            filepath = change["path"]
            backup_path = change.get("backup_path")
            before_hash = change.get("before_hash")

            if backup_path and os.path.exists(backup_path):
                shutil.copy2(backup_path, filepath)
                # Invalidate cache for restored file
                if self.cache:
                    self.cache.invalidate_file(filepath)
                current_hash = self._file_hash(filepath)
                verified = (current_hash == before_hash)
                change["rollback_verified"] = verified
                change["rollback_verified_at"] = datetime.now(timezone.utc).isoformat() if verified else None
                results.append({"file": filepath, "restored_from": backup_path, "hash_match": verified})
            else:
                change["rollback_verified"] = False
                change["rollback_verified_at"] = None
                results.append({"file": filepath, "restored_from": None, "hash_match": False, "error": "Backup not found"})

        self._write_manifest(manifest)

        report = {
            "rollback_type": "tranche",
            "tranche_num": tranche_num,
            "files_checked": len(results),
            "files_verified": sum(1 for r in results if r["hash_match"]),
            "files_mismatched": [r["file"] for r in results if not r["hash_match"]],
            "overall_status": ("verified" if all(r["hash_match"] for r in results) else "critical_failure" if not any(r["hash_match"] for r in results) else "partial_failure"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        report_path = os.path.join(self.artifacts_dir, "rollback_verification_report.json")
        with open(report_path, "w") as fh:
            json.dump(report, fh, indent=2)

        return report

    def execute(self) -> Dict:
        self.state_mgr.initialize()
        self.state_mgr.transition_wave("pre_flight")
        self.logger.log(wave="pre_flight", action="start", result="success")

        plan = self.load_plan()
        manifest = self.init_manifest(plan)
        self.logger.log(wave="pre_flight", action="init_manifest", result="success", target_path=self.manifest_path)

        # Check resource health
        resource_health = self.check_resource_health()
        if not resource_health["can_proceed"]:
            self.logger.log(wave="pre_flight", action="resource_check", result="failure", details=f"resource_health={resource_health}")
            return {"status": "aborted", "reason": "insufficient_resources", "resource_health": resource_health}

        from dry_runner import DryRunner
        dry = DryRunner(self.plan_path, self.artifacts_dir)
        dry_report = dry.run()
        self.logger.log(wave="pre_flight", action="dry_run", result="success" if dry_report["ready_for_approval"] else "failure", details=f"violations={len(dry_report['scope_violations'])} warnings={len(dry_report['warnings'])}")

        if not dry_report["ready_for_approval"]:
            self.state_mgr.transition_wave("failed")
            self.logger.log(wave="pre_flight", action="abort", result="failure", details="dry run failed")
            return {"status": "aborted", "reason": "dry_run_failed", "dry_run_report": dry_report}

        self.state_mgr.transition_wave("approval")
        self.logger.log(wave="approval", action="await_approval", result="success")

        approval = manifest.get("approval", {})
        approved = approval.get("approved_by") and approval.get("approval_time")

        if not approved and approval.get("required", True):
            self.logger.log(wave="approval", action="approval_check", result="failure", details="No approval recorded — halting.")
            return {"status": "awaiting_approval", "message": "Human approval required. Record approval in change_manifest.json approval block, then re-run."}

        self.logger.log(wave="approval", action="approval_confirmed", result="success")

        self.state_mgr.transition_wave("applying")
        self.logger.log(wave="applying", action="start_tranches", result="success")

        operations = plan.get("operations", [])
        total_ops = len(operations)
        state = self.state_mgr.read()
        start_index = state.get("next_index", 0)

        tranche_num = 0
        all_results = []

        # Use adaptive tranche sizing
        remaining_ops = operations[start_index:]
        adaptive_size = self.calculate_adaptive_tranche_size(remaining_ops)
        self.logger.log(wave="applying", action="adaptive_sizing", result="success", details=f"tranche_size={adaptive_size}")

        for i in range(start_index, total_ops, adaptive_size):
            tranche = operations[i:i + adaptive_size]
            tranche_num += 1

            result = self._process_tranche(tranche, tranche_num)
            all_results.append(result)

            if result["status"] == "failed":
                self.logger.log(wave="applying", action="tranche_failed", result="failure", target_path=str(tranche_num), details=result.get("error", ""))
                rollback_report = self.rollback_tranche(tranche_num)
                self.logger.log(wave="applying", action="tranche_rolled_back", result="success" if rollback_report["overall_status"] == "verified" else "failure", target_path=str(tranche_num))
                self.state_mgr.transition_wave("failed")
                return {"status": "failed", "failed_tranche": tranche_num, "rollback_report": rollback_report, "results": all_results}

        self.state_mgr.transition_wave("verification")
        self.logger.log(wave="verification", action="start", result="success")

        verification_results = self._run_verification_checks(plan)
        all_passed = all(v["passed"] for v in verification_results)

        self.logger.log(wave="verification", action="complete", result="success" if all_passed else "failure", details=f"{sum(1 for v in verification_results if v['passed'])}/{len(verification_results)} passed")

        if all_passed:
            self.state_mgr.transition_wave("done")
            self.logger.log(wave="done", action="complete", result="success")
        else:
            self.state_mgr.transition_wave("failed")
            self.logger.log(wave="verification", action="checks_failed", result="failure")

        # Export metrics if enabled
        metrics_export = None
        if self.metrics:
            metrics_export = self.metrics.export_metrics(os.path.join(self.artifacts_dir, "session_metrics.json"))

        return {"status": "done" if all_passed else "verification_failed", "tranches_processed": tranche_num, "total_operations": total_ops, "verification_results": verification_results, "results": all_results, "metrics_export": metrics_export}

    def _process_tranche(self, tranche: List[Dict], tranche_num: int) -> Dict:
        tranche_start = time.time()
        self.logger.log(wave="applying", action="tranche_start", result="success", target_path=str(tranche_num))
        processed_files = []

        if self.enable_parallel and len(tranche) > 1:
            # Use parallel processing for independent operations
            independent_groups = self._identify_independent_operations(tranche)
            
            for group in independent_groups:
                if len(group) == 1:
                    # Single operation, process normally
                    op_result = self._process_operation(group[0], tranche_num)
                    if not op_result["ok"]:
                        if self.metrics:
                            tranche_duration = time.time() - tranche_start
                            self.metrics.record_tranche(tranche_num, len(tranche), tranche_duration, False)
                        return {"status": "failed", "tranche_num": tranche_num, "operation": group[0], "error": op_result.get("error", "unknown"), "processed_files": processed_files}
                    processed_files.append(op_result.get("path"))
                else:
                    # Multiple independent operations, process in parallel
                    results = self._process_parallel_operations(group, tranche_num)
                    for result in results:
                        if not result["ok"]:
                            if self.metrics:
                                tranche_duration = time.time() - tranche_start
                                self.metrics.record_tranche(tranche_num, len(tranche), tranche_duration, False)
                            return {"status": "failed", "tranche_num": tranche_num, "error": result.get("error", "unknown"), "processed_files": processed_files}
                        processed_files.append(result.get("path"))
        else:
            # Sequential processing
            for op in tranche:
                op_result = self._process_operation(op, tranche_num)
                if not op_result["ok"]:
                    if self.metrics:
                        tranche_duration = time.time() - tranche_start
                        self.metrics.record_tranche(tranche_num, len(tranche), tranche_duration, False)
                    return {"status": "failed", "tranche_num": tranche_num, "operation": op, "error": op_result.get("error", "unknown"), "processed_files": processed_files}
                processed_files.append(op_result.get("path"))

        for pf in processed_files:
            self.state_mgr.record_processed(pf)

        tranche_duration = time.time() - tranche_start
        if self.metrics:
            self.metrics.record_tranche(tranche_num, len(tranche), tranche_duration, True)
            if self.cache:
                self.metrics.record_cache_stats(self.cache.get_cache_stats())

        self.logger.log(wave="applying", action="tranche_complete", result="success", target_path=str(tranche_num))
        return {"status": "success", "tranche_num": tranche_num, "processed_files": processed_files}

    def _process_operation(self, op: Dict, tranche_num: int) -> Dict:
        op_name = op.get("op", "unknown")
        op_path = op.get("path", "")
        params = op.get("params", {})
        max_attempts = self.MAX_RETRIES + 1
        op_start = time.time()

        for attempt in range(1, max_attempts + 1):
            try:
                before_hash = None
                backup_path = None

                if op_path and os.path.exists(op_path):
                    backup_path = self._backup_file(op_path, tranche_num)
                    before_hash = self._file_hash(op_path)
                else:
                    before_hash = None

                if op_name == "backup":
                    if backup_path:
                        after_hash = before_hash
                    else:
                        return {"ok": False, "error": f"File not found: {op_path}"}
                elif op_name == "apt_install":
                    packages = params.get("packages", [])
                    for pkg in packages:
                        result = subprocess.run(["apt-get", "install", "-y", pkg], capture_output=True, text=True, timeout=300)
                        if result.returncode != 0:
                            return {"ok": False, "error": f"apt install failed for {pkg}: {result.stderr}"}
                    after_hash = before_hash
                elif op_name == "update":
                    if op_path and os.path.exists(op_path):
                        after_hash = self._file_hash(op_path)
                    else:
                        after_hash = None
                elif op_name == "delete":
                    if op_path and os.path.exists(op_path):
                        os.remove(op_path)
                    after_hash = None
                elif op_name == "service_restart":
                    svc = params.get("service", "")
                    if svc:
                        result = subprocess.run(["systemctl", "restart", svc], capture_output=True, text=True, timeout=30)
                        if result.returncode != 0:
                            return {"ok": False, "error": f"Service restart failed: {svc}: {result.stderr}"}
                    after_hash = before_hash
                else:
                    return {"ok": False, "error": f"Unknown operation: {op_name}"}

                change = {
                    "type": op_name,
                    "path": op_path or "(none)",
                    "tranche_num": tranche_num,
                    "backup_path": backup_path,
                    "before_hash": before_hash,
                    "after_hash": after_hash,
                    "description": f"Operation: {op_name}",
                    "rollback_steps": f"Restore from {backup_path}" if backup_path else "No rollback needed",
                    "rollback_verified": None,
                    "rollback_verified_at": None,
                }
                self._append_change(change)

                if op_path and os.path.exists(op_path):
                    scan_report = self.scanner.scan_file(op_path)
                    if scan_report.get("secrets_found"):
                        for finding in scan_report["secrets_found"]:
                            self._append_secret_finding(finding)
                        self.logger.log(wave="applying", action="secret_detected", result="failure", target_path=op_path, details=f"{len(scan_report['secrets_found'])} secrets found")
                        return {"ok": False, "error": "Secrets detected in modified file — halting", "path": op_path}

                self.logger.log(wave="applying", action=op_name, result="success", target_path=op_path, details=f"attempt={attempt}")
                
                # Record operation metrics
                if self.metrics:
                    op_duration = time.time() - op_start
                    self.metrics.record_operation(op_name, op_duration, 1, success=True)
                
                return {"ok": True, "path": op_path or "(none)"}

            except Exception as exc:
                self.logger.log(wave="applying", action=op_name, result="failure", target_path=op_path, details=f"attempt={attempt} error={str(exc)}")
                
                # Record failed operation metrics
                if self.metrics:
                    op_duration = time.time() - op_start
                    self.metrics.record_operation(op_name, op_duration, 1, success=False)
                
                if attempt >= max_attempts:
                    self.state_mgr.record_failure(file_path=op_path, reason=str(exc), attempt_count=attempt, recovered=False)
                    return {"ok": False, "error": str(exc), "path": op_path}

        return {"ok": False, "error": "Max retries exceeded", "path": op_path}

    def _identify_independent_operations(self, operations: List[Dict]) -> List[List[Dict]]:
        """Group operations into independent batches that can be processed in parallel."""
        # Simple heuristic: operations on different paths are independent
        # More sophisticated dependency analysis could be added
        path_groups = {}
        
        for op in operations:
            path = op.get("path", "")
            if path not in path_groups:
                path_groups[path] = []
            path_groups[path].append(op)
        
        # Operations without paths (like apt_install) are independent per package
        no_path_ops = [op for op in operations if not op.get("path")]
        for op in no_path_ops:
            if "no_path" not in path_groups:
                path_groups["no_path"] = []
            path_groups["no_path"].append(op)
        
        # Return list of operation groups (each group can be processed sequentially, groups in parallel)
        return list(path_groups.values())

    def _process_parallel_operations(self, independent_ops: List[Dict], tranche_num: int) -> List[Dict]:
        """Process independent operations in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all operations
            future_to_op = {
                executor.submit(self._process_operation, op, tranche_num): op 
                for op in independent_ops
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_op):
                op = future_to_op[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    results.append({"ok": False, "error": str(exc), "path": op.get("path", "")})
        
        return results

    def _run_verification_checks(self, plan: Dict) -> List[Dict]:
        results = []
        for check in plan.get("verification", []):
            check_type = check.get("check", "")
            args = check.get("args", [])
            passed = False
            detail = ""

            try:
                if check_type == "sha256sum" and args:
                    filepath = args[0]
                    passed = os.path.exists(filepath)
                    if passed:
                        detail = f"hash={self._file_hash(filepath)}"
                    else:
                        detail = f"File not found: {filepath}"
                elif check_type == "dpkg_installed" and args:
                    passed = self._verify_package(args[0])
                    detail = f"package={args[0]} installed={passed}"
                elif check_type == "service_active" and args:
                    passed = self._verify_service(args[0])
                    detail = f"service={args[0]} active={passed}"
                elif check_type == "port_listening" and args:
                    port = args[0]
                    result = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True, timeout=10)
                    passed = f":{port}" in result.stdout
                    detail = f"port={port} listening={passed}"
                else:
                    detail = f"Unknown check type: {check_type}"
            except Exception as exc:
                detail = f"Exception: {str(exc)}"

            results.append({"check": check_type, "args": args, "passed": passed, "detail": detail})

        return results
