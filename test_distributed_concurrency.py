
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from collections import Counter
from time import perf_counter
from statistics import mean
from uuid import uuid4
import json
import math

SERVERS = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001"
]

TOTAL_REQUESTS = 200
WORKERS = 20
USER_ID = f"distributed-{uuid4().hex}"

# Verify both servers use Redis.
for server in SERVERS:
    with urlopen(server + "/health", timeout=5) as response:
        health = json.load(response)

        if health.get("backend") != "redis":
            raise SystemExit(
                f"Wrong backend: {server}"
            )

    print("Redis backend ready:", server)


def send_request(index):

    # Alternate requests between both servers.
    server = SERVERS[index % 2]

    request = Request(
        server + "/api/data",
        headers={"X-Demo-User": USER_ID}
    )

    start = perf_counter()
    retry_after = None

    try:
        with urlopen(request, timeout=10) as response:
            status = response.status

    except HTTPError as error:
        status = error.code
        retry_after = error.headers.get("Retry-After")
        error.close()

    except (URLError, TimeoutError, OSError):
        status = "ERROR"

    latency = (perf_counter() - start) * 1000

    return server, status, retry_after, latency


print("\n--- Distributed Concurrency Test ---")
print("Requests:", TOTAL_REQUESTS)
print("Workers:", WORKERS)
print("Servers:", len(SERVERS))

start = perf_counter()

with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    results = list(
        executor.map(
            send_request,
            range(TOTAL_REQUESTS)
        )
    )

elapsed = perf_counter() - start

counts = Counter(row[1] for row in results)

server_counts = Counter(
    (row[0], row[1]) for row in results
)

latencies = sorted(row[3] for row in results)

p95 = latencies[
    math.ceil(len(latencies) * 0.95) - 1
]

valid_retry = sum(
    1 for _, status, retry, _ in results
    if status == 429
    and retry is not None
    and retry.isdigit()
    and 1 <= int(retry) <= 60
)

print("\n--- Individual Server Results ---")

for server in SERVERS:
    print("\n", server)
    print("HTTP 200:", server_counts[(server, 200)])
    print("HTTP 429:", server_counts[(server, 429)])

errors = TOTAL_REQUESTS - counts[200] - counts[429]

print("\n--- Global Results ---")
print("HTTP 200:", counts[200])
print("HTTP 429:", counts[429])
print("Unexpected responses:", errors)
print("Valid Retry-After headers:", valid_retry)

print("\n--- Performance ---")
print(f"Total time: {elapsed:.3f} seconds")
print(f"Average latency: {mean(latencies):.2f} ms")
print(f"P95 latency: {p95:.2f} ms")
print(f"Throughput: {TOTAL_REQUESTS / elapsed:.2f} req/s")

print("\n--- Correctness Check ---")

if elapsed >= 60:
    print("INCONCLUSIVE: Window exceeded")

elif (
    counts[200] == 100
    and counts[429] == 100
    and errors == 0
    and valid_retry == 100
):
    print("PASS: Distributed concurrent quota enforced")

else:
    print("FAIL: Distributed quota verification")

