import json
import logging

from redis.exceptions import RedisError

from app.core.redis_client import redis_client


logger = logging.getLogger(__name__)

AVAILABILITY_CACHE_TTL = 60


def get_availability_version(machine_id):
    version_key = f"availability:version:{machine_id}"

    try:
        version = redis_client.get(version_key)

        return int(version) if version is not None else 0

    except (RedisError, ValueError, TypeError):
        logger.exception("Failed to retrieve availability version")
        return None


def availability_cache_key(machine_id, slot_date, version):
    return f"availability:{machine_id}:{slot_date}:v{version}"


def get_cached_availability(key):
    try:
        cached = redis_client.get(key)

        if cached is not None:
            return json.loads(cached)

    except (RedisError, ValueError, TypeError):
        logger.exception("Availability cache read failed")

    return None


def set_cached_availability(key, data):
    try:
        redis_client.setex(
            key,
            AVAILABILITY_CACHE_TTL,
            json.dumps(data),
        )

    except (RedisError, ValueError, TypeError):
        logger.exception("Availability cache write failed")