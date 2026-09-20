#!/usr/bin/env python3
"""state_manager.py — Atomic STATE.md Reader/Writer"""

import os
import tempfile
from datetime import datetime, timezone
from typing import Dict, Any, Optional

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML is required: pip install pyyaml")

class StateManager:
    DEFAULT_STATE: Dict[str, Any] = {
        "runbook_version": "2.0",
        "plan_version": "2.0",
        "inspection_id": None,
        "wave": "pre_flight",
        "next_index": 0,
        "processed_files": [],
        "processed_count": 0,
        "failures": [],
        "rolled_back": False,
        "last_updated": None,
        "artifacts": [],
        "manifest_signature": None,
    }

    def __init__(self, state_path: str):
        self.state_path = state_path
        self._dir = os.path.dirname(state_path)

    def initialize(self) -> Dict:
        if not os.path.exists(self.state_path):
            state = dict(self.DEFAULT_STATE)
            state["last_updated"] = datetime.now(timezone.utc).isoformat()
            self.write_atomic(state)
        return self.read()

    def read(self) -> Dict:
        if not os.path.exists(self.state_path):
            return dict(self.DEFAULT_STATE)
        with open(self.state_path, "r") as fh:
            data = yaml.safe_load(fh) or {}
        merged = dict(self.DEFAULT_STATE)
        merged.update(data)
        return merged

    def write_atomic(self, state: Dict) -> None:
        os.makedirs(self._dir, exist_ok=True)
        state["last_updated"] = datetime.now(timezone.utc).isoformat()
        content = yaml.dump(state, default_flow_style=False, sort_keys=True)

        tmp_fd, tmp_path = tempfile.mkstemp(dir=self._dir, prefix=".STATE.", suffix=".tmp")

        try:
            with os.fdopen(tmp_fd, "w") as fh:
                fh.write(content)
                fh.flush()
                os.fsync(fh.fileno())

            os.replace(tmp_path, self.state_path)

            dir_fd = os.open(self._dir, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def transition_wave(self, new_wave: str) -> Dict:
        state = self.read()
        old_wave = state.get("wave")
        state["wave"] = new_wave
        self.write_atomic(state)
        return {"old_wave": old_wave, "new_wave": new_wave}

    def record_failure(self, file_path: str, reason: str, attempt_count: int, recovered: bool = False) -> Dict:
        state = self.read()
        failure = {"file": file_path, "reason": reason, "attempt_count": attempt_count, "recovered": recovered}
        state["failures"].append(failure)
        self.write_atomic(state)
        return failure

    def record_processed(self, file_path: str) -> Dict:
        state = self.read()
        state["processed_files"].append(file_path)
        state["processed_count"] = len(state["processed_files"])
        state["next_index"] += 1
        self.write_atomic(state)
        return state
