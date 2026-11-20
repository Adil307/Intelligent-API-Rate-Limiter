# Architecture

## Policy

For server time `t`, consider accepted requests in `(t - 60 seconds, t]`. Accept a new request if fewer than 100 remain; otherwise reject and report the time until the oldest accepted timestamp expires (rounded up to seconds, at least one second).

## Original process-local design

`main.py` -> `RateLimiter.py` -> dictionary of per-user deques. An in-process lock groups expiry removal, quota check and insertion. Timestamps use monotonic time except for explicit ordered tests. Idle user cleanup is an explicit sweep, not an automatic background job.

Two independently running processes maintain different dictionaries and locks. The same demo user received 60 successful responses per process (120 overall) in the two-instance baseline experiment.

## Redis-backed design

`main_redis.py` -> `RedisRateLimiter.py` -> `sliding_window.lua` -> one Redis instance. Both application processes use the same key namespace and policy. A SHA-256 digest of the demo user ID is included in the key; this does not authenticate or anonymize the original identity. Unique request IDs avoid overwriting members with identical timestamps.

The script uses Redis TIME in microseconds; removes expired members with ZREMRANGEBYSCORE; counts with ZCARD; rejects full windows with computed Retry-After; otherwise inserts via ZADD and sets PEXPIRE. Script execution is atomic with respect to other Redis commands on the server. TTL reclaims idle keys; exact expiry still occurs inside the script. Client retries are disabled in the supplied Redis client configuration to avoid silently repeating ambiguous operations.

## Failure semantics

- HTTP 200: allowed request.
- HTTP 429: quota reached, with Retry-After.
- HTTP 503: shared backend unavailable; no permissive fallback.

Two instances were tested on one Windows machine with Redis in Ubuntu WSL2. The restart experiment verifies fresh-request recovery, not durability or multi-machine availability.
