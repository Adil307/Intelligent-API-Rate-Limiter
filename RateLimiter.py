
from collections import deque
from math import ceil
from threading import Lock
from time import monotonic


class RateLimiter:

    def __init__(self, limit=100, window=60):
        if limit < 1 or window <= 0:
            raise ValueError("limit and window must be positive")

        self.limit = limit
        self.window = window
        self.requests = {}
        self._lock = Lock()

    def check_request(self, user_id, timestamp=None):
        with self._lock:
            now = monotonic() if timestamp is None else timestamp

            user_queue = self.requests.setdefault(
                user_id, deque()
            )

            # Remove expired timestamps
            while user_queue and user_queue[0] <= now - self.window:
                user_queue.popleft()

            # Reject when quota is full
            if len(user_queue) >= self.limit:
                retry_after = max(
                    1,
                    ceil(user_queue[0] + self.window - now)
                )
                return False, retry_after

            # Accept request
            user_queue.append(now)
            return True, 0

    def allow_request(self, user_id, timestamp=None):
        allowed, _ = self.check_request(user_id, timestamp)
        return allowed

    def cleanup_expired(self, current_time=None):
        with self._lock:
            now = monotonic() if current_time is None else current_time

            for user_id, user_queue in list(self.requests.items()):
                while user_queue and user_queue[0] <= now - self.window:
                    user_queue.popleft()

                if not user_queue:
                    del self.requests[user_id]

    def stored_users(self):
        with self._lock:
            return len(self.requests)


if __name__ == "__main__":
    limiter = RateLimiter(limit=3, window=10)

    tests = [
        ("A", 1),
        ("A", 3),
        ("A", 5),
        ("A", 7),
        ("B", 7),
        ("A", 15),
    ]

    for user, timestamp in tests:
        result = limiter.allow_request(user, timestamp)
        print(f"User {user}, Time {timestamp}: {result}")
