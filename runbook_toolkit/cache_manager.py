#!/usr/bin/env python3
"""cache_manager.py — Smart Caching for Tool Call Optimization"""

import hashlib
import json
import os
from typing import Dict, Optional, Any
from datetime import datetime, timezone

class CacheManager:
    """Intelligent caching layer to reduce redundant file operations and computations."""
    
    def __init__(self, cache_dir: Optional[str] = None, max_size_mb: int = 100):
        self.cache_dir = cache_dir or os.path.join(os.path.expanduser("~"), ".runbook_cache")
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.file_hashes: Dict[str, str] = {}
        self.file_contents: Dict[str, str] = {}
        self.validation_results: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        
        os.makedirs(self.cache_dir, exist_ok=True)
        self._load_metadata()
    
    def _get_cache_path(self, key: str) -> str:
        """Generate cache file path from key."""
        safe_key = hashlib.sha256(key.encode()).hexdigest()[:16]
        return os.path.join(self.cache_dir, f"cache_{safe_key}.json")
    
    def _load_metadata(self):
        """Load cache metadata from disk."""
        meta_path = os.path.join(self.cache_dir, "metadata.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r") as fh:
                    self.metadata = json.load(fh)
            except (json.JSONDecodeError, IOError):
                self.metadata = {}
    
    def _save_metadata(self):
        """Save cache metadata to disk."""
        meta_path = os.path.join(self.cache_dir, "metadata.json")
        with open(meta_path, "w") as fh:
            json.dump(self.metadata, fh, indent=2)
    
    def _cleanup_if_needed(self):
        """Clean up old cache entries if size limit exceeded."""
        total_size = sum(
            os.path.getsize(os.path.join(self.cache_dir, f))
            for f in os.listdir(self.cache_dir)
            if f.startswith("cache_")
        )
        
        if total_size > self.max_size_bytes:
            # Remove oldest entries
            entries = []
            for f in os.listdir(self.cache_dir):
                if f.startswith("cache_"):
                    path = os.path.join(self.cache_dir, f)
                    entries.append((os.path.getmtime(path), path))
            
            entries.sort()  # Oldest first
            for _, path in entries:
                try:
                    os.remove(path)
                    total_size -= os.path.getsize(path)
                    if total_size <= self.max_size_bytes * 0.8:  # 80% threshold
                        break
                except OSError:
                    pass
    
    def get_file_hash(self, filepath: str) -> Optional[str]:
        """Get cached file hash or compute and cache it."""
        cache_key = f"hash:{filepath}"
        
        # Check in-memory cache first
        if filepath in self.file_hashes:
            return self.file_hashes[filepath]
        
        # Check disk cache
        cache_path = self._get_cache_path(cache_key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as fh:
                    data = json.load(fh)
                    if self._is_cache_valid(data):
                        self.file_hashes[filepath] = data["value"]
                        return data["value"]
            except (json.JSONDecodeError, IOError):
                pass
        
        # Compute and cache
        if not os.path.exists(filepath):
            return None
        
        try:
            hasher = hashlib.sha256()
            with open(filepath, "rb") as fh:
                for chunk in iter(lambda: fh.read(8192), b""):
                    hasher.update(chunk)
            hash_value = hasher.hexdigest()
            
            self.file_hashes[filepath] = hash_value
            self._cache_value(cache_key, hash_value)
            return hash_value
        except OSError:
            return None
    
    def get_file_content(self, filepath: str) -> Optional[str]:
        """Get cached file content or read and cache it."""
        cache_key = f"content:{filepath}"
        
        # Check in-memory cache first
        if filepath in self.file_contents:
            return self.file_contents[filepath]
        
        # Check disk cache
        cache_path = self._get_cache_path(cache_key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as fh:
                    data = json.load(fh)
                    if self._is_cache_valid(data):
                        self.file_contents[filepath] = data["value"]
                        return data["value"]
            except (json.JSONDecodeError, IOError):
                pass
        
        # Read and cache
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
            
            self.file_contents[filepath] = content
            self._cache_value(cache_key, content)
            return content
        except OSError:
            return None
    
    def get_validation_result(self, validation_key: str) -> Optional[Any]:
        """Get cached validation result."""
        cache_key = f"validation:{validation_key}"
        
        # Check in-memory cache
        if validation_key in self.validation_results:
            return self.validation_results[validation_key]
        
        # Check disk cache
        cache_path = self._get_cache_path(cache_key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as fh:
                    data = json.load(fh)
                    if self._is_cache_valid(data):
                        self.validation_results[validation_key] = data["value"]
                        return data["value"]
            except (json.JSONDecodeError, IOError):
                pass
        
        return None
    
    def cache_validation_result(self, validation_key: str, result: Any, ttl_seconds: int = 3600):
        """Cache validation result with TTL."""
        cache_key = f"validation:{validation_key}"
        self.validation_results[validation_key] = result
        self._cache_value(cache_key, result, ttl_seconds)
    
    def _cache_value(self, cache_key: str, value: Any, ttl_seconds: int = 7200):
        """Cache a value to disk with TTL."""
        cache_path = self._get_cache_path(cache_key)
        data = {
            "value": value,
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "ttl_seconds": ttl_seconds
        }
        
        with open(cache_path, "w") as fh:
            json.dump(data, fh)
        
        self._cleanup_if_needed()
        self._save_metadata()
    
    def _is_cache_valid(self, cache_data: Dict) -> bool:
        """Check if cached data is still valid based on TTL."""
        if "cached_at" not in cache_data or "ttl_seconds" not in cache_data:
            return False
        
        cached_at = datetime.fromisoformat(cache_data["cached_at"])
        ttl = cache_data["ttl_seconds"]
        age = (datetime.now(timezone.utc) - cached_at).total_seconds()
        
        return age < ttl
    
    def invalidate_file(self, filepath: str):
        """Invalidate all cache entries for a specific file."""
        if filepath in self.file_hashes:
            del self.file_hashes[filepath]
        if filepath in self.file_contents:
            del self.file_contents[filepath]
        
        # Remove disk cache entries
        for cache_type in ["hash", "content"]:
            cache_key = f"{cache_type}:{filepath}"
            cache_path = self._get_cache_path(cache_key)
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                except OSError:
                    pass
    
    def clear_all(self):
        """Clear all cache entries."""
        self.file_hashes.clear()
        self.file_contents.clear()
        self.validation_results.clear()
        
        for f in os.listdir(self.cache_dir):
            if f.startswith("cache_"):
                try:
                    os.remove(os.path.join(self.cache_dir, f))
                except OSError:
                    pass
        
        self._save_metadata()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        cache_files = [f for f in os.listdir(self.cache_dir) if f.startswith("cache_")]
        total_size = sum(
            os.path.getsize(os.path.join(self.cache_dir, f))
            for f in cache_files
        )
        
        return {
            "entries": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "in_memory_hashes": len(self.file_hashes),
            "in_memory_contents": len(self.file_contents),
            "in_memory_validations": len(self.validation_results),
            "cache_dir": self.cache_dir
        }