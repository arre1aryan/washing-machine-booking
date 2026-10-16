import logging
import os

import redis
from redis.exceptions import RedisError


logger = logging.getLogger(__name__)

redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)


def invalidate_machine_availability(machine_id):
    version_key = f"availability:version:{machine_id}"

    try:
        new_version = redis_client.incr(version_key)

        logger.info(
            "Advanced availability version for machine %s to %s",
            machine_id,
            new_version,
        )

    except RedisError:
        logger.exception(
            "Failed to advance availability version for machine %s",
            machine_id,
        )