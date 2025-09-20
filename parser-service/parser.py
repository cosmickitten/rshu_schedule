# parser-service/main.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
import os
import aiohttp
from redis_client import add_notification
from bs4 import BeautifulSoup
import hashlib
import signal

class ParserService:
    def __init__(self):
        self.auth_service_url = "http://auth-service:8000"
        self.parse_interval = int(os.getenv("PARSE_INTERVAL_MINUTES", 30))
        print(f"Parser configured with {self.parse_interval} minutes interval")
        
    async def get_users_from_auth_service(self):
        """Получаем пользователей из auth-service"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.auth_service_url}/settings/') as response:
                    if response.status == 200:
                        users = await response.json()
                        print(f"Received {len(users)} users from auth-service")
                        return users
                    print(f"Auth service error: {response.status}")
                    return []
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    async def parse_all_schedules(self):
        """Основная функция парсинга"""
        try:
            print("Starting scheduled parsing...")
            users = await self.get_users_from_auth_service()
            print(f"Found {len(users)} users to parse")
            
            if not users:
                print("No users found")
                return
            
            for user_data in users:
                print(f"Processing user: {user_data.get('telegram_id')}")
                await self.parse_user_schedule(user_data)
                
            print("Scheduled parsing completed")
                
        except Exception as e:
            print(f"Error in parse_all_schedules: {e}")
    
    # ... остальные методы без изменений ...

async def main():
    """Основная асинхронная функция"""
    print("Parser service starting...")
    
    parser = ParserService()
    
    # Запускаем сразу при старте
    print("Running initial parse...")
    await parser.parse_all_schedules()
    
    # Настраиваем планировщик
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        parser.parse_all_schedules,
        IntervalTrigger(minutes=parser.parse_interval),
        id='parse_schedules'
    )
    scheduler.start()
    print(f"✅ Scheduler started. Parsing every {parser.parse_interval} minutes.")
    
    # Бесконечный цикл без блокировки
    try:
        while True:
            await asyncio.sleep(1)  # Короткие интервалы для responsiveness
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down scheduler...")
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())