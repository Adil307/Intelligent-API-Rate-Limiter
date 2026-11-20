
from RateLimiter import RateLimiter

limiter = RateLimiter(limit=3, window=10)

print("--- Day 05: Edge-Case Testing ---")

tests = [
    (1, True),
    (2, True),
    (3, True),
    (4, False),
    (10, False),
    (11, True),
]

for timestamp, expected in tests:
    actual = limiter.allow_request("A", timestamp)

    assert actual == expected, (
        f"FAIL at timestamp {timestamp}: "
        f"Expected {expected}, got {actual}"
    )

    print(
        f"Time {timestamp}: "
        f"{'Allowed' if actual else 'Rejected'}"
    )

print("\n--- Rejected Requests Check ---")

# At t=11, the request at t=1 expires.
# A rejected request must not occupy a slot.
assert list(limiter.requests["A"]) == [2, 3, 11]

print("PASS: Rejected requests were not stored")

print("\n--- Memory Cleanup Check ---")

limiter.cleanup_expired(current_time=22)

assert limiter.stored_users() == 0

print("PASS: Expired user data removed")

print("\n--- Configuration Validation ---")

for limit, window in [(0, 10), (3, 0)]:
    try:
        RateLimiter(limit=limit, window=window)
    except ValueError:
        print("PASS: Invalid configuration rejected")
    else:
        raise AssertionError("Invalid configuration was accepted")

print("\nALL EDGE-CASE TESTS PASSED")
