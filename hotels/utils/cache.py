"""
File-based cache for Google Hotels searches to protect network/API quotas.
"""

import os
import json
import time
import hashlib
from typing import Optional, Dict, Any

CACHE_DIR = os.path.expanduser("~/.cache/google_hotels")
CACHE_FILE = os.path.join(CACHE_DIR, "hotel_cache.json")
DEFAULT_TTL_SECONDS = 7200  # 2 hours

def _ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)

def _get_cache_key(query: str, check_in: str, check_out: str, **kwargs) -> str:
    payload = {
        "q": query.lower().strip(),
        "in": check_in,
        "out": check_out,
        **{k: v for k, v in sorted(kwargs.items()) if v is not None}
    }
    raw = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def get_cached_result(cache_key: str, ttl: int = DEFAULT_TTL_SECONDS) -> Optional[Any]:
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            entry = data.get(cache_key)
            if not entry:
                return None
            if time.time() - entry.get("timestamp", 0) < ttl:
                return entry.get("data")
    except Exception:
        return None
    return None

def set_cached_result(cache_key: str, data: Any):
    _ensure_cache_dir()
    cache_data = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
        except Exception:
            cache_data = {}
            
    cache_data[cache_key] = {
        "timestamp": time.time(),
        "data": data
    }
    
    # Prune stale entries if cache gets too large (>200 items)
    if len(cache_data) > 200:
        now = time.time()
        cache_data = {k: v for k, v in cache_data.items() if now - v.get("timestamp", 0) < 86400}
        
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
