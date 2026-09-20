#!/usr/bin/env python3
"""dry_runner.py — Dry-Run Simulation for PLAN.json"""

import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class ScopeValidator:
    allowed_directories: List[str] = field(default_factory=list)
    blocked_directories: List[str] = field(default_factory=lambda: ["/bin", "/sbin", "/root", "/boot", "/proc", "/sys", "/usr/bin", "/usr/sbin"])
    allowed_packages: List[str] = field(default_factory=list)
    blocked_packages: List[str] = field(default_factory=lambda: ["ubuntu-minimal", "systemd"])

    def validate_path(self, path: str) -> Dict:
        try:
            real = os.path.realpath(path)
        except Exception:
            real = path

        for blocked in self.blocked_directories:
            if real.startswith(blocked.rstrip("/") + "/") or real == blocked:
                return {"ok": False, "reason": f"Path blocked: {real} matches {blocked}"}

        if self.allowed_directories:
            allowed = any(real.startswith(a.rstrip("/") + "/") or real == a for a in self.allowed_directories)
            if not allowed:
                return {"ok": False, "reason": f"Path not in allowlist: {real}"}

        return {"ok": True, "reason": ""}

    def validate_package(self, pkg: str) -> Dict:
        if pkg in self.blocked_packages:
            return {"ok": False, "reason": f"Package blocked: {pkg}"}
        if self.allowed_packages and pkg not in self.allowed_packages:
            return {"ok": False, "reason": f"Package not in allowlist: {pkg}"}
        return {"ok": True, "reason": ""}

class DryRunner:
    DEFAULT_ALLOWED_DIRS = ["/opt/", "/home/app/venv/", "/var/lib/application/", "/etc/application/"]
    DEFAULT_ALLOWED_PKGS = ["python3-pip", "git", "curl"]

    def __init__(self, plan_path: str, artifacts_dir: str, validator: Optional[ScopeValidator] = None):
        self.plan_path = plan_path
        self.artifacts_dir = artifacts_dir
        self.validator = validator or ScopeValidator(
            allowed_directories=self.DEFAULT_ALLOWED_DIRS,
            allowed_packages=self.DEFAULT_ALLOWED_PKGS,
        )

    def load_plan(self) -> Dict:
        with open(self.plan_path, "r") as fh:
            return json.load(fh)

    def plan_hash(self, plan: Dict) -> str:
        canonical = json.dumps(plan, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def simulate_apt_install(self, packages: List[str]) -> Dict:
        try:
            cmd = ["apt-get", "--simulate", "install", "-y"] + packages
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return {"ok": result.returncode == 0, "stdout": result.stdout[:2000], "stderr": result.stderr[:2000]}
        except FileNotFoundError:
            return {"ok": False, "stdout": "", "stderr": "apt-get not found"}
        except subprocess.TimeoutExpired:
            return {"ok": False, "stdout": "", "stderr": "apt-get simulate timed out"}

    def estimate_disk_usage(self, paths: List[str]) -> int:
        total = 0
        for p in paths:
            if os.path.isfile(p):
                total += os.path.getsize(p)
            elif os.path.isdir(p):
                for root, _, files in os.walk(p):
                    for f in files:
                        fp = os.path.join(root, f)
                        try:
                            total += os.path.getsize(fp)
                        except OSError:
                            pass
        return total

    def run(self) -> Dict:
        warnings: List[str] = []
        violations: List[str] = []
        operations_simulated = 0

        try:
            plan = self.load_plan()
        except Exception as exc:
            return {
                "plan_valid": False,
                "scope_violations": [],
                "estimated_disk_usage_bytes": 0,
                "operations_simulated": 0,
                "warnings": [f"Failed to load plan: {exc}"],
                "ready_for_approval": False,
            }

        if not plan.get("dry_run", False):
            warnings.append("PLAN.json dry_run is not set to true — force-enabling for simulation.")

        scope = plan.get("scope", {})
        include_paths = scope.get("include", [])

        for path in include_paths:
            clean = path.replace("/**/*", "").replace("/*", "")
            check = self.validator.validate_path(clean)
            if not check["ok"]:
                violations.append(check["reason"])

        for op in plan.get("operations", []):
            op_name = op.get("op", "unknown")
            op_path = op.get("path", "")

            if op_path:
                check = self.validator.validate_path(op_path)
                if not check["ok"]:
                    violations.append(f"op '{op_name}': {check['reason']}")

            if op_name == "apt_install":
                pkgs = op.get("params", {}).get("packages", [])
                for pkg in pkgs:
                    check = self.validator.validate_package(pkg)
                    if not check["ok"]:
                        violations.append(f"package '{pkg}': {check['reason']}")
                    else:
                        sim = self.simulate_apt_install([pkg])
                        if not sim["ok"]:
                            warnings.append(f"apt simulate failed for '{pkg}': {sim['stderr']}")

            operations_simulated += 1

        backup_targets = [op["path"] for op in plan.get("operations", []) if op.get("path")]
        disk_estimate = self.estimate_disk_usage(backup_targets)

        if backup_targets:
            first_path = backup_targets[0]
            try:
                usage = shutil.disk_usage(os.path.dirname(first_path) or "/")
                if disk_estimate > usage.free:
                    warnings.append(f"Insufficient disk: need ~{disk_estimate} bytes, have {usage.free} bytes free")
            except OSError:
                warnings.append("Could not check disk free space")

        plan_valid = len(violations) == 0
        ready = plan_valid and len(warnings) == 0

        report = {
            "plan_valid": plan_valid,
            "plan_hash": self.plan_hash(plan),
            "scope_violations": violations,
            "estimated_disk_usage_bytes": disk_estimate,
            "operations_simulated": operations_simulated,
            "warnings": warnings,
            "ready_for_approval": ready,
        }

        report_path = os.path.join(self.artifacts_dir, "dry_run_report.json")
        os.makedirs(self.artifacts_dir, exist_ok=True)
        with open(report_path, "w") as fh:
            json.dump(report, fh, indent=2)

        return report
