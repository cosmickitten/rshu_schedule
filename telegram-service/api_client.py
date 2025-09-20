# telegram-service/api_client.py
import aiohttp
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class AuthServiceClient:
    def __init__(self):
        self.base_url = "http://auth-service:8000"
    
    async def save_user_settings(self, telegram_id: str, group_name: str) -> bool:
        """Сохраняет настройки пользователя в auth-service"""
        try:
            async with aiohttp.ClientSession() as session:
                # Теперь отправляем только необходимые поля
                payload = {
                    "telegram_id": telegram_id,
                    "group_name": group_name
                    # schedule_settings больше не отправляем, сервер использует дефолтные
                }
                
                logger.info(f"Saving user settings: {payload}")
                
                async with session.post(
                    f"{self.base_url}/settings/",
                    json=payload,
                    timeout=10
                ) as response:
                    
                    if response.status == 200:
                        logger.info(f"Successfully saved settings for user {telegram_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Auth service error: {response.status} - {error_text}")
                        return False
                        
        except aiohttp.ClientError as e:
            logger.error(f"Network error connecting to auth-service: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False

# Глобальный экземпляр клиента
auth_client = AuthServiceClient()