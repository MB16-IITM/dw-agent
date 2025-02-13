# src/utils/cache.py
import hashlib
import json
from pathlib import Path

CACHE_DIR = Path("/data/cache")  # Changed from /app/cache


def get_cache_key(task: str, params: dict) -> str:
    unique_str = f"{task}-{json.dumps(params, sort_keys=True)}"
    return hashlib.sha256(unique_str.encode()).hexdigest()[:32]

def save_response(task: str, params: dict, response: dict):
    CACHE_DIR.mkdir(exist_ok=True)
    key = get_cache_key(task, params)
    (CACHE_DIR / f"{key}.json").write_text(json.dumps({
        "function": response['tool_calls'][0]['function']['name'],
        "params": params
    }))

def load_response(task: str, params: dict) -> dict | None:
    key = get_cache_key(task, params)
    cache_file = CACHE_DIR / f"{key}.json"
    return json.loads(cache_file.read_text()) if cache_file.exists() else None
