#!/usr/bin/env python3
"""audit_chain.py — Tamper-Evident Audit Log with Hash-Chain Integrity"""

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Optional

class AuditLogger:
    AUDIT_FILENAME = "audit_log.jsonl"

    def __init__(self, artifacts_dir: str):
        self.artifacts_dir = artifacts_dir
        self.log_path = os.path.join(artifacts_dir, self.AUDIT_FILENAME)
        os.makedirs(artifacts_dir, exist_ok=True)
        if not os.path.exists(self.log_path):
            open(self.log_path, "w").close()

    @staticmethod
    def _compute_hash(seq: int, timestamp: str, wave: str, action: str,
                      target_path: Optional[str], result: str,
                      prev_hash: Optional[str]) -> str:
        raw = f"{seq}|{timestamp}|{wave}|{action}|{target_path}|{result}|{prev_hash}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _last_entry(self) -> Optional[dict]:
        last = None
        with open(self.log_path, "r") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    last = json.loads(line)
        return last

    def log(self, wave: str, action: str, result: str = "success",
            target_path: Optional[str] = None, manifest_ref: Optional[str] = None,
            details: str = "") -> dict:
        last = self._last_entry()
        seq = (last["seq"] + 1) if last else 1
        prev_hash = last["this_hash"] if last else None
        ts = datetime.now(timezone.utc).isoformat()

        this_hash = self._compute_hash(seq, ts, wave, action, target_path, result, prev_hash)

        entry = {
            "seq": seq,
            "timestamp": ts,
            "wave": wave,
            "action": action,
            "target_path": target_path,
            "result": result,
            "prev_hash": prev_hash,
            "this_hash": this_hash,
            "manifest_ref": manifest_ref,
            "details": details,
        }

        with open(self.log_path, "a") as fh:
            fh.write(json.dumps(entry, sort_keys=False) + "\n")

        return entry

    def verify_chain(self) -> bool:
        prev_hash: Optional[str] = None
        expected_seq = 1

        with open(self.log_path, "r") as fh:
            for lineno, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    print(f"[CHAIN] Malformed JSON at line {lineno}")
                    return False

                seq = entry["seq"]
                ts = entry["timestamp"]
                wave = entry["wave"]
                action = entry["action"]
                target = entry.get("target_path")
                result = entry["result"]
                stored_prev = entry.get("prev_hash")
                stored_hash = entry["this_hash"]

                if seq != expected_seq:
                    print(f"[CHAIN] Sequence gap at line {lineno}: expected seq={expected_seq}, got seq={seq}")
                    return False

                if prev_hash != stored_prev:
                    print(f"[CHAIN] prev_hash mismatch at line {lineno}: expected={prev_hash}, got={stored_prev}")
                    return False

                computed = self._compute_hash(seq, ts, wave, action, target, result, prev_hash)
                if computed != stored_hash:
                    print(f"[CHAIN] Hash mismatch at line {lineno}: expected={stored_hash}, computed={computed}")
                    return False

                prev_hash = stored_hash
                expected_seq += 1

        return True
