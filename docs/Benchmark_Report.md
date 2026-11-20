# Local experiment report

Evidence is transcribed from the project author's reported terminal output during the seven-day challenge; these are not independent CI runs. Environment: Windows, FastAPI on localhost, Ubuntu WSL2 Redis 8.0.5; Redis client 8.1.0. Hardware and exact FastAPI version were not recorded in the logs.

## Day 04

The sequential script sent 101 requests. Printed observations: requests 1, 2, 99 and 100 returned HTTP 200; request 101 returned HTTP 429; Retry-After was 60 seconds. The script printed selected statuses rather than a full response histogram.

## Day 05

150 request tasks, 20 client threads, one in-memory API process. HTTP 200 = 100; HTTP 429 = 50; errors = 0; Retry-After headers present = 50. Total 0.555 s; mean 59.41 ms; P95 126.25 ms; throughput 270.34 responses/s.

Isolation: A sent 110 (100 accepted, 10 rejected); B sent 10 (10 accepted, 0 rejected). Boundary checks at timestamps 1, 2, 3, 4, 10, 11 produced allow, allow, allow, reject, reject, allow. Rejected requests were not stored; cleanup and the two invalid configuration cases passed.

## Day 06

Two independent in-memory instances: 60 accepted each; 120 total, 20 beyond global quota; 0.417 s. Redis-backed sequential repeat: A 60/0 and B 40/20 (HTTP 200/429), 100 accepted, 20 rejected, 0 unexpected, 20 valid Retry-After values, 0.867 s.

Redis-backed concurrent test: 200 tasks, 20 workers, two instances. A 51/49 and B 49/51. Combined HTTP 200 = 100, HTTP 429 = 100, unexpected responses = 0, valid Retry-After headers = 100. Total 0.401 s; mean 34.16 ms; P95 43.80 ms; throughput 498.82 responses/s.

## Day 07

| Phase | Port 8000 | Port 8001 |
|---|---:|---:|
| Healthy | 200 | 200 |
| Redis stopped | 503 | 503 |
| Redis restarted | 200 | 200 |

All six status checks passed. Redis CLI reported connection refused when stopped and PONG after restart.

## Interpretation

The reported throughput counts all completed HTTP responses (accepted and rejected), using total workload divided by elapsed time. Client-observed latency includes HTTP and client scheduling overhead. The reported P95 uses the nearest-rank sample statistic. One run per setup does not establish sustainable capacity. Day 05 and Day 06 differ in process count, total requests and response mix, so the numbers cannot establish a Redis-specific speedup. No production load, multi-host network, persistence, long-duration, or failover benchmark is claimed.
