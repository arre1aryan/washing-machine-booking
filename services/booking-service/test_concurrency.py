import concurrent.futures

import requests


URL = "http://localhost:8002/bookings"

USER_ID = "1b2cd49b-90fa-44f5-baf9-fc18d27b751e"
SLOT_ID = "42100172-8a51-48a4-a5c4-38990aaebca3"


def book():
    response = requests.post(
        URL,
        json={
            "user_id": USER_ID,
            "slot_id": SLOT_ID,
        },
    )

    return response.status_code, response.json()


with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    results = list(executor.map(lambda _: book(), range(2)))

for result in results:
    print(result)