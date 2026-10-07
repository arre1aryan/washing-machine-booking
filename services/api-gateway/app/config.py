import os

from dotenv import load_dotenv

load_dotenv()


MACHINE_SERVICE_URL = os.getenv(
    "MACHINE_SERVICE_URL",
    "http://localhost:8001",
)

BOOKING_SERVICE_URL = os.getenv(
    "BOOKING_SERVICE_URL",
    "http://localhost:8002",
)

AUTH_SERVICE_URL = os.getenv(
    "AUTH_SERVICE_URL",
    "http://localhost:8003",
)