
from urllib.request import Request, urlopen
from urllib.error import HTTPError

URL = "http://127.0.0.1:8000/api/data"

print("--- Week 02 Day 04: HTTP Rate Limit Test ---")

for i in range(1, 102):

    request = Request(
        URL,
        headers={"X-Demo-User": "test-user-101"}
    )

    try:
        with urlopen(request, timeout=5) as response:
            status = response.status
            retry_after = None

    except HTTPError as error:
        status = error.code
        retry_after = error.headers.get("Retry-After")

    if i in [1, 2, 99, 100, 101]:
        print(f"Request {i}: HTTP {status}")

        if retry_after is not None:
            print(f"Retry-After: {retry_after} seconds")
