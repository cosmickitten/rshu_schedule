import redis
import os
import json

redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    decode_responses=True
)

def add_notification(telegram_id: str, message: str, file_data: bytes = None):
    notification = {
        "telegram_id": telegram_id,
        "message": message,
        "file_data": file_data.hex() if file_data else None
    }
    redis_client.rpush("notification_queue", json.dumps(notification))