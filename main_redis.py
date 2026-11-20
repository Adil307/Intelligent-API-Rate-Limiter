from fastapi import FastAPI, Header, HTTPException
from redis.exceptions import RedisError
from RedisRateLimiter import RedisRateLimiter

app = FastAPI(title='Distributed API Rate Limiter', version='0.2.0')
limiter = RedisRateLimiter(limit=100, window=60)


@app.get('/')
def home():
    return {'message': 'Redis API Rate Limiter is running'}


@app.get('/health')
def health():
    try:
        if not limiter.client.ping():
            raise HTTPException(status_code=503, detail='Redis unavailable')
    except RedisError as exc:
        raise HTTPException(status_code=503, detail='Redis unavailable') from exc
    return {'status': 'ok', 'backend': 'redis'}


@app.get('/limiter-config')
def limiter_config():
    return {'limit': limiter.limit, 'window_seconds': limiter.window, 'backend': 'redis'}


@app.get('/api/data')
def get_data(x_demo_user: str = Header(default='demo-user', alias='X-Demo-User', min_length=1, max_length=128)):
    # Demo header only; production must use authenticated identity.
    try:
        allowed, retry_after = limiter.check_request(x_demo_user)
    except RedisError as exc:
        # Fail closed: never bypass quota when shared state is unavailable.
        raise HTTPException(status_code=503, detail='Rate limiter unavailable') from exc
    if not allowed:
        raise HTTPException(status_code=429, detail='Rate limit exceeded',
                            headers={'Retry-After': str(retry_after)})
    return {'message': 'Request allowed', 'user': x_demo_user, 'status': 200}
