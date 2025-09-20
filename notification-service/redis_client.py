import redis
import os
import json

redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    decode_responses=False
)

def get_notification():
    result = redis_client.blpop("notification_queue", timeout=30)
    if result:
        return json.loads(result[1])
    return None