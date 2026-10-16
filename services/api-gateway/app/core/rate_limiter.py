import logging

from fastapi import HTTPException, status
from redis.exceptions import RedisError

from app.core.redis_client import redis_client


logger = logging.getLogger(__name__)

BOOKING_RATE_LIMIT = 10
BOOKING_RATE_WINDOW = 60


RATE_LIMIT_SCRIPT = """
local count = redis.call("INCR", KEYS[1])

if count == 1 then
    redis.call("EXPIRE", KEYS[1], ARGV[1])
end

local ttl = redis.call("TTL", KEYS[1])

return {count, ttl}
"""


def check_booking_rate_limit(user_id):
    key = f"rate_limit:booking:{user_id}"

    try:
        count, ttl = redis_client.eval(
            RATE_LIMIT_SCRIPT,
            1,
            key,
            BOOKING_RATE_WINDOW,
        )

    except RedisError:
        logger.exception(
            "Redis unavailable: allowing booking request"
        )
        return

    if count > BOOKING_RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many booking attempts. Try again later.",
            headers={
                "Retry-After": str(max(ttl, 1)),
            },
        )