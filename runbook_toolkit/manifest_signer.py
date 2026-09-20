#!/usr/bin/env python3
"""manifest_signer.py — Cryptographic Signing for change_manifest.json"""

import hashlib
import json
import os
import subprocess
import tempfile
from typing import Optional, Dict

class ManifestSigner:
    def __init__(self, artifacts_dir: str, gpg_key_id: Optional[str] = None, openssl_privkey: Optional[str] = None):
        self.artifacts_dir = artifacts_dir
        self.gpg_key_id = gpg_key_id
        self.openssl_privkey = openssl_privkey
        self.algorithm = "gpg" if gpg_key_id else ("openssl" if openssl_privkey else None)

    @staticmethod
    def canonical_digest(data: dict) -> str:
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _sign_gpg(self, file_path: str) -> str:
        sig_path = file_path + ".sig"
        cmd = ["gpg", "--detach-sign", "--armor"]
        if self.gpg_key_id:
            cmd.extend(["--local-user", self.gpg_key_id])
        cmd.extend(["--output", sig_path, file_path])

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"GPG signing failed: {result.stderr}")
        return sig_path

    def _verify_gpg(self, file_path: str, sig_path: str) -> bool:
        cmd = ["gpg", "--verify", sig_path, file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0

    def _sign_openssl(self, file_path: str) -> str:
        sig_path = file_path + ".sig"
        cmd = ["openssl", "dgst", "-sha256", "-sign", self.openssl_privkey, "-out", sig_path, file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"OpenSSL signing failed: {result.stderr}")
        return sig_path

    def _verify_openssl(self, file_path: str, sig_path: str, pubkey: str) -> bool:
        cmd = ["openssl", "dgst", "-sha256", "-verify", pubkey, "-signature", sig_path, file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0

    def sign(self, manifest_path: str) -> Dict:
        if not self.algorithm:
            raise RuntimeError("No signing method configured (need gpg_key_id or openssl_privkey)")

        with open(manifest_path, "r") as fh:
            manifest = json.load(fh)

        manifest_copy = dict(manifest)
        manifest_copy.pop("signature", None)
        digest = self.canonical_digest(manifest_copy)

        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(tmp_fd, "w") as fh:
                json.dump(manifest_copy, fh, sort_keys=True, separators=(",", ":"))

            if self.algorithm == "gpg":
                self._sign_gpg(tmp_path)
                sig_file = tmp_path + ".sig"
                with open(sig_file, "r") as fh:
                    sig_value = fh.read().strip()
                os.unlink(sig_file)
            else:
                self._sign_openssl(tmp_path)
                sig_file = tmp_path + ".sig"
                with open(sig_file, "rb") as fh:
                    import base64
                    sig_value = base64.b64encode(fh.read()).decode()
                os.unlink(sig_file)
        finally:
            os.unlink(tmp_path)

        sig_meta = {"algorithm": self.algorithm, "key_id": self.gpg_key_id or self.openssl_privkey or "", "digest": digest, "signed_at": None}
        manifest["signature"] = sig_meta

        with open(manifest_path, "w") as fh:
            json.dump(manifest, fh, indent=2)

        det_sig_path = manifest_path + ".sig"
        if self.algorithm == "gpg":
            self._sign_gpg(manifest_path)
        else:
            self._sign_openssl(manifest_path)

        return sig_meta

    def verify(self, manifest_path: str) -> bool:
        sig_path = manifest_path + ".sig"
        if not os.path.exists(sig_path):
            print(f"[VERIFY] No signature file found at {sig_path}")
            return False

        if self.algorithm == "gpg":
            return self._verify_gpg(manifest_path, sig_path)
        elif self.algorithm == "openssl" and self.openssl_privkey:
            privkey_dir = os.path.dirname(self.openssl_privkey)
            pubkey = os.path.join(privkey_dir, "pubkey.pem")
            if not os.path.exists(pubkey):
                print(f"[VERIFY] Public key not found at {pubkey}")
                return False
            return self._verify_openssl(manifest_path, sig_path, pubkey)
        else:
            return self._verify_gpg(manifest_path, sig_path)

    def verify_digest(self, manifest_path: str) -> bool:
        with open(manifest_path, "r") as fh:
            manifest = json.load(fh)

        stored_sig = manifest.get("signature")
        if not stored_sig:
            return False

        manifest_copy = dict(manifest)
        manifest_copy.pop("signature", None)
        computed = self.canonical_digest(manifest_copy)

        return computed == stored_sig.get("digest")
