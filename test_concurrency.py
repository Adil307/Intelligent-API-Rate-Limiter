
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from collections import Counter
from statistics import mean
from time import perf_counter
from uuid import uuid4
import math

URL = "http://127.0.0.1:8000/api/data"

TOTAL_REQUESTS = 150
CONCURRENT_WORKERS = 20

# Unique user to avoid consuming previous test quota
TEST_USER = f"day05-test-{uuid4().hex}"


def send_request(_):
    request = Request(
        URL,
        headers={"X-Demo-User": TEST_USER}
    )

    start = perf_counter()

    try:
        with urlopen(request, timeout=10) as response:
            status = response.status
            retry_after = None

    except HTTPError as error:
        status = error.code
        retry_after = error.headers.get("Retry-After")
        error.close()

    except URLError as error:
        status = "ERROR"
        retry_after = None
        print("Connection error:", error)

    latency_ms = (perf_counter() - start) * 1000

    return status, retry_after, latency_ms


print("--- Day 05: Concurrent HTTP Test ---")
print("Requests:", TOTAL_REQUESTS)
print("Workers:", CONCURRENT_WORKERS)

start = perf_counter()

with ThreadPoolExecutor(
    max_workers=CONCURRENT_WORKERS
) as executor:
    results = list(
        executor.map(
            send_request,
            range(TOTAL_REQUESTS)
        )
    )

elapsed = perf_counter() - start

statuses = Counter(result[0] for result in results)

latencies = sorted(result[2] for result in results)

def percentile(values, p):
    index = max(0, math.ceil(len(values) * p) - 1)
    return values[index]


print("\n--- HTTP Results ---")
print("HTTP 200:", statuses[200])
print("HTTP 429:", statuses[429])
print("Errors:", TOTAL_REQUESTS - statuses[200] - statuses[429])

print("\n--- Performance ---")
print(f"Total time: {elapsed:.3f} seconds")
print(f"Average latency: {mean(latencies):.2f} ms")
print(f"P95 latency: {percentile(latencies, 0.95):.2f} ms")
print(f"Throughput: {TOTAL_REQUESTS / elapsed:.2f} requests/sec")

retry_values = [
    int(retry)
    for status, retry, _ in results
    if status == 429 and retry is not None
]

print("\nRetry-After headers found:", len(retry_values))

print("\n--- Correctness Check ---")

if elapsed < 60:
    if (
        statuses[200] == 100
        and statuses[429] == 50
        and len(retry_values) == 50
    ):
        print("PASS: Rate limit correctly enforced")
    else:
        print("FAIL: Review concurrency or response errors")
else:
    print("INCONCLUSIVE: Test crossed the 60-second window")
