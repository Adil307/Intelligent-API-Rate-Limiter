from collections import Counter
from time import perf_counter
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from uuid import uuid4
import json

SERVERS = ['http://127.0.0.1:8000', 'http://127.0.0.1:8001']
USER = f'day06-{uuid4().hex}'


def request(server, path):
    req = Request(server + path, headers={'X-Demo-User': USER})
    try:
        with urlopen(req, timeout=10) as response:
            return response.status, response.headers.get('Retry-After'), json.load(response)
    except HTTPError as error:
        with error:
            return error.code, error.headers.get('Retry-After'), None
    except (URLError, TimeoutError, OSError) as error:
        raise SystemExit(f'Connection failed: {server}: {error}')


print('--- Day 06: Redis Distributed Rate Limit Test ---')
for server in SERVERS:
    status, _, body = request(server, '/health')
    if status != 200 or body.get('backend') != 'redis':
        raise SystemExit(f'Not a healthy Redis API: {server}')
    status, _, body = request(server, '/limiter-config')
    if status != 200 or body.get('limit') != 100 or body.get('window_seconds') != 60:
        raise SystemExit(f'Unexpected rate-limit configuration: {server}')
    print('Redis backend ready:', server)

counts = Counter()
valid_retry = 0
start = perf_counter()
for server in SERVERS:
    for _ in range(60):
        status, retry, _ = request(server, '/api/data')
        counts[server, status] += 1
        if status == 429 and retry and retry.isdigit() and 1 <= int(retry) <= 60:
            valid_retry += 1
elapsed = perf_counter() - start
for server in SERVERS:
    print(f'\n{server}')
    print('HTTP 200:', counts[server, 200])
    print('HTTP 429:', counts[server, 429])
accepted = sum(counts[s, 200] for s in SERVERS)
rejected = sum(counts[s, 429] for s in SERVERS)
errors = 120 - accepted - rejected
print('\n--- Global Results ---')
print('Total accepted:', accepted)
print('Total rejected:', rejected)
print('Unexpected responses:', errors)
print('Valid Retry-After headers:', valid_retry)
print(f'Elapsed time: {elapsed:.3f} seconds')
if elapsed >= 60:
    raise SystemExit('INCONCLUSIVE: test crossed the 60-second window')
if (accepted, rejected, errors, valid_retry) != (100, 20, 0, 20):
    raise SystemExit('FAIL: global quota or response behavior incorrect')
if counts[SERVERS[0], 200] != 60 or counts[SERVERS[1], 200] != 40:
    raise SystemExit('FAIL: unexpected sequential server results')
print('PASS: One global quota enforced across both instances')
