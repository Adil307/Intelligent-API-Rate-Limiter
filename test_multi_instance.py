
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from collections import Counter
from time import perf_counter
from uuid import uuid4

SERVERS = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001"
]

# Both servers receive requests for the SAME user.
# Unique ID keeps this run separate from earlier tests.
USER_ID = f"day06-{uuid4().hex}"
REQUESTS_PER_SERVER = 60


def send_request(server, endpoint, user_id=None):
    headers = {}

    if user_id is not None:
        headers["X-Demo-User"] = user_id

    request = Request(
        f"{server}{endpoint}",
        headers=headers
    )

    try:
        with urlopen(request, timeout=5) as response:
            return response.status

    except HTTPError as error:
        status = error.code
        error.close()
        return status

    except URLError as error:
        raise SystemExit(
            f"Server unavailable: {server}\n{error}"
        )


print("--- Day 06: Multi-Instance Rate Limit Test ---")

# Check that BOTH servers are available.
for server in SERVERS:
    status = send_request(server, "/health")

    if status != 200:
        raise SystemExit(f"Health check failed: {server}")

    print(f"Server ready: {server}")


results = Counter()
start = perf_counter()

# Send 60 requests to each independent server.
for server in SERVERS:

    for _ in range(REQUESTS_PER_SERVER):
        status = send_request(
            server,
            "/api/data",
            USER_ID
        )

        results[(server, status)] += 1


elapsed = perf_counter() - start

print("\n--- Server Results ---")

for server in SERVERS:
    print(f"\n{server}")
    print("HTTP 200:", results[(server, 200)])
    print("HTTP 429:", results[(server, 429)])


total_allowed = sum(
    results[(server, 200)]
    for server in SERVERS
)

print("\n--- Global Results ---")
print("Total accepted:", total_allowed)
print("Global quota:", 100)
print(f"Elapsed time: {elapsed:.3f} seconds")


if elapsed >= 60:
    print("INCONCLUSIVE: Test crossed the 60-second window")

elif total_allowed > 100:
    print("REPRODUCED: Global limit exceeded!")
    print("Each instance has independent memory.")

else:
    print("Global quota was not exceeded in this run.")
