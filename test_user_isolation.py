
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from collections import Counter
from uuid import uuid4

URL = "http://127.0.0.1:8000/api/data"
run_id = uuid4().hex

users = (
    [(f"A-{run_id}", "A")] * 110
    + [(f"B-{run_id}", "B")] * 10
)

def send_request(item):
    user_id, label = item

    request = Request(
        URL,
        headers={"X-Demo-User": user_id}
    )

    try:
        with urlopen(request, timeout=10) as response:
            return label, response.status

    except HTTPError as error:
        return label, error.code

with ThreadPoolExecutor(max_workers=20) as executor:
    results = list(executor.map(send_request, users))

counts = Counter(results)

print("--- User Isolation Test ---")
print("User A - HTTP 200:", counts[("A", 200)])
print("User A - HTTP 429:", counts[("A", 429)])
print("User B - HTTP 200:", counts[("B", 200)])
print("User B - HTTP 429:", counts[("B", 429)])

expected = {
    ("A", 200): 100,
    ("A", 429): 10,
    ("B", 200): 10,
    ("B", 429): 0
}

if counts == Counter(expected):
    print("PASS: Independent user quotas")
else:
    print("FAIL: Review user isolation")
