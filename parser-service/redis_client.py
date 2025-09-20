# parser-service/redis_client.py
import redis
import os
import json
from logger import logger

# Подключаемся к Redis
try:
    redis_client = redis.Redis.from_url(
        os.getenv("REDIS_URL", "redis://redis:6379"),
        decode_responses=False,
        socket_timeout=5,
        retry_on_timeout=True
    )
    # Тестируем подключение
    redis_client.ping()
    logger.info("✅ Redis connection established")
except Exception as e:
    logger.error(f"❌ Redis connection failed: {e}")
    redis_client = None

def add_notification(telegram_id: str, message: str, file_data: bytes = None):
    """Добавление уведомления в очередь Redis"""
    if not redis_client:
        logger.error("Redis client not available")
        return False
        
    try:
        notification = {
            "telegram_id": telegram_id,
            "message": message,
            "file_data": file_data.hex() if file_data else None
        }
        
        result = redis_client.rpush("notification_queue", json.dumps(notification))
        logger.info(f"Notification added to Redis queue for {telegram_id}, queue length: {result}")
        return True
        
    except redis.RedisError as e:
        logger.error(f"Redis error adding notification: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error adding notification: {e}")
        return False