
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from uuid import uuid4

SERVERS = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001"
]

PHASES = {
    "healthy": 200,
    "failure": 503,
    "recovery": 200
}

if len(sys.argv) != 2 or sys.argv[1] not in PHASES:
    print("Usage:")
    print("python test_failure_recovery.py healthy")
    print("python test_failure_recovery.py failure")
    print("python test_failure_recovery.py recovery")
    sys.exit(1)

phase = sys.argv[1]
expected = PHASES[phase]

USER_ID = f"day07-{uuid4().hex}"

print("--- Day 07: Failure and Recovery Test ---")
print("Phase:", phase.upper())
print("Expected HTTP status:", expected)

passed = 0

for server in SERVERS:

    request = Request(
        server + "/api/data",
        headers={"X-Demo-User": USER_ID}
    )

    try:
        with urlopen(request, timeout=15) as response:
            status = response.status

    except HTTPError as error:
        status = error.code
        error.close()

    except (URLError, TimeoutError, OSError) as error:
        status = "CONNECTION ERROR"
        print("Error:", error)

    print(f"\nServer: {server}")
    print("Actual response:", status)

    if status == expected:
        print("PASS")
        passed += 1
    else:
        print("FAIL")

print("\n--- Final Result ---")
print(f"Passed: {passed}/{len(SERVERS)}")

if passed == len(SERVERS):
    print(f"PASS: {phase.upper()} verification")
else:
    print(f"FAIL: {phase.upper()} verification")
    sys.exit(1)
