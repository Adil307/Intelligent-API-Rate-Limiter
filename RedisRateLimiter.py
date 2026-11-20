from hashlib import sha256
from pathlib import Path
from uuid import uuid4
import redis
from redis.backoff import NoBackoff
from redis.retry import Retry


class RedisRateLimiter:
    def __init__(self, limit=100, window=60):
        if type(limit) is not int or limit < 1:
            raise ValueError('limit must be a positive integer')
        if type(window) is not int or not 1 <= window <= 86400:
            raise ValueError('window must be an integer from 1 to 86400 seconds')
        self.limit = limit
        self.window = window
        self.client = redis.Redis(
            host='127.0.0.1', port=6379, db=0,
            socket_connect_timeout=3, socket_timeout=3,
            retry=Retry(NoBackoff(), 0),
        )
        self.script = self.client.register_script(
            Path(__file__).with_name('sliding_window.lua').read_text(encoding='utf-8')
        )

    def check_request(self, user_id):
        digest = sha256(user_id.encode('utf-8')).hexdigest()
        key = f'week02:day06:v1:{self.limit}:{self.window}:{digest}'
        allowed, retry_after = self.script(
            keys=[key], args=[self.limit, self.window * 1000, uuid4().hex]
        )
        return bool(allowed), int(retry_after)
