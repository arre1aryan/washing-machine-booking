import concurrent.futures
import threading
import os

import httpx


URL = "http://localhost:8002/bookings"

TOKEN = os.environ["TEST_JWT"]

# Two fresh, consecutive, available slots
SLOT_A = os.environ["TEST_SLOT_A"]
SLOT_B = os.environ["TEST_SLOT_B"]

barrier = threading.Barrier(2)


def book(slot_id):
    barrier.wait()

    try:
        response = httpx.post(
            URL,
            json={
                "slot_id": slot_id,
            },
            headers={
                "Authorization": f"Bearer {TOKEN}",
            },
            timeout=20,
        )

        return slot_id, response.status_code, response.json()

    except httpx.RequestError as exc:
        return slot_id, "ERROR", str(exc)


with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    results = list(executor.map(book, [SLOT_A, SLOT_B]))

for result in results:
    print(result)

success = sum(status == 201 for _, status, _ in results)
conflicts = sum(status == 409 for _, status, _ in results)

print("\nConsecutive Booking Concurrency Results")
print("Successful bookings:", success)
print("Conflicts:", conflicts)

assert success == 1, f"Expected 1 success, got {success}"
assert conflicts == 1, f"Expected 1 conflict, got {conflicts}"

print("PASS: Consecutive bookings prevented!")