"""Tiny in-memory cache with a time limit. Rankings scan every delivery, so cache them.
Cleared automatically after a scorecard upload. After running the CLI importer in a separate
process, the server's cache can be up to `ttl` seconds stale (restart the server to clear)."""
import time

_store = {}


def get_or_compute(key, compute, ttl=300):
    now = time.time()
    hit = _store.get(key)
    if hit and now - hit[0] < ttl:
        return hit[1]
    value = compute()
    _store[key] = (now, value)
    return value


def clear():
    _store.clear()
