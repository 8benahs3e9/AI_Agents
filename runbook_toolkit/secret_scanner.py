#!/usr/bin/env python3
"""secret_scanner.py — Secret Detection and Redaction Engine"""

import os
import re
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class SecretPattern:
    name: str
    regex: re.Pattern
    replacement: str

    def match_at(self, text: str) -> List[Dict]:
        results = []
        for m in self.regex.finditer(text):
            results.append({
                "offset_start": m.start(),
                "pattern_matched": self.name,
                "matched_length": m.end() - m.start(),
            })
        return results

class SecretScanner:
    PATTERNS: List[SecretPattern] = [
        SecretPattern("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED:aws_access_key]"),
        SecretPattern("aws_secret_key", re.compile(r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*\S+"), "[REDACTED:aws_secret_key]"),
        SecretPattern("api_key", re.compile(r"(?i)api[_-]?key\s*[=:]\s*\S+"), "[REDACTED:api_key]"),
        SecretPattern("token", re.compile(r"(?i)(auth[_-]?)?token\s*[=:]\s*\S+"), "[REDACTED:token]"),
        SecretPattern("bearer_token", re.compile(r"(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*"), "[REDACTED:bearer_token]"),
        SecretPattern("jwt", re.compile(r"eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]*"), "[REDACTED:jwt]"),
        SecretPattern("pem_private_key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----[\s\S]*?-----END \1PRIVATE KEY-----"), "[REDACTED:pem_private_key]"),
        SecretPattern("gcp_private_key", re.compile(r'"private_key"\s*:\s*"[^"]+"'), '"private_key": "[REDACTED:gcp_private_key]"'),
        SecretPattern("azure_account_key", re.compile(r"(?i)AccountKey\s*[=:]\s*[A-Za-z0-9+/=]+"), "[REDACTED:azure_account_key]"),
        SecretPattern("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"), "[REDACTED:github_token]"),
        SecretPattern("slack_token", re.compile(r"xox[baprs]-[A-Za-z0-9-]+"), "[REDACTED:slack_token]"),
        SecretPattern("db_connection_string", re.compile(r"(?i)(postgres|mysql|mongodb)(\+srv)?://[^:]+:[^@]+@"), "[REDACTED:db_connection_string]"),
    ]

    def scan_text(self, text: str) -> List[Dict]:
        findings: List[Dict] = []
        for pat in self.PATTERNS:
            for hit in pat.match_at(text):
                findings.append(hit)
        findings.sort(key=lambda f: f["offset_start"])
        return findings

    def scan_file(self, filepath: str) -> Dict:
        if not os.path.isfile(filepath):
            return {"file": filepath, "secrets_found": [], "error": "file not found"}

        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except PermissionError:
            return {"file": filepath, "secrets_found": [], "error": "permission denied"}

        findings = self.scan_text(content)

        return {
            "file": filepath,
            "secrets_found": [
                {"file": filepath, "offset_start": f["offset_start"], "pattern_matched": f["pattern_matched"], "matched_length": f["matched_length"], "redacted": False}
                for f in findings
            ],
            "total_secrets": len(findings),
        }

    def scan_directory(self, dirpath: str) -> List[Dict]:
        results: List[Dict] = []
        for root, dirs, files in os.walk(dirpath):
            for fname in files:
                fpath = os.path.join(root, fname)
                report = self.scan_file(fpath)
                if report.get("secrets_found"):
                    results.append(report)
        return results

    def redact_text(self, text: str) -> tuple:
        findings = []
        for pat in self.PATTERNS:
            for m in pat.regex.finditer(text):
                findings.append({"offset_start": m.start(), "pattern_matched": pat.name, "matched_length": m.end() - m.start(), "redacted": True})
            text = pat.regex.sub(pat.replacement, text)
        findings.sort(key=lambda f: f["offset_start"])
        return text, findings

    def redact_file(self, filepath: str, report: Dict) -> Dict:
        if not report.get("secrets_found"):
            return report

        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read()

        redacted_text, _ = self.redact_text(content)

        tmp_path = filepath + ".redacted.tmp"
        with open(tmp_path, "w", encoding="utf-8") as fh:
            fh.write(redacted_text)
        os.replace(tmp_path, filepath)

        for s in report["secrets_found"]:
            s["redacted"] = True

        return report

    @classmethod
    def list_patterns(cls) -> List[str]:
        return [p.name for p in cls.PATTERNS]
