import logging
import os

import httpx
import redis
from redis.exceptions import RedisError

from app.core.config import settings


logger = logging.getLogger(__name__)

redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)


def invalidate_slot_availability(slot_id):
    try:
        response = httpx.get(
            f"{settings.machine_service_url}/slots/{slot_id}",
            timeout=5.0,
        )
        response.raise_for_status()

        slot = response.json()

        machine_id = slot["machine_id"]

        version_key = f"availability:version:{machine_id}"

        new_version = redis_client.incr(version_key)

        logger.info(
            "Advanced availability version for machine %s to %s",
            machine_id,
            new_version,
        )

    except (
        httpx.HTTPError,
        RedisError,
        KeyError,
        TypeError,
        ValueError,
    ):
        logger.exception(
            "Failed to invalidate availability for slot %s",
            slot_id,
        )