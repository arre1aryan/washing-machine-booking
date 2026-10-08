import concurrent.futures
import os

import httpx


URL = "http://localhost:8002/bookings"

# Use a fresh, unbooked slot.
SLOT_ID = os.environ["TEST_SLOT_ID"]

# Never hardcode or commit JWTs.
TOKEN = os.environ["TEST_JWT"]


def book():
    try:
        response = httpx.post(
            URL,
            json={
                "slot_id": SLOT_ID,
            },
            headers={
                "Authorization": f"Bearer {TOKEN}",
            },
            timeout=15,
        )

        return response.status_code, response.json()

    except httpx.RequestError as exc:
        return "ERROR", str(exc)


with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(lambda _: book(), range(10)))

for result in results:
    print(result)

success = sum(status == 201 for status, _ in results)
conflicts = sum(status == 409 for status, _ in results)

print("\nConcurrency Test Results")
print("Successful bookings:", success)
print("Conflicts:", conflicts)

assert success == 1, f"Expected 1 success, got {success}"
assert conflicts == 9, f"Expected 9 conflicts, got {conflicts}"

print("PASS: Duplicate booking prevented!")