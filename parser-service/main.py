# parser-service/main.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
import os
import aiohttp
from redis_client import add_notification
from bs4 import BeautifulSoup
import hashlib
from logger import logger

class ParserService:
    def __init__(self):
        self.auth_service_url = "http://auth-service:8000"
        self.parse_interval = int(os.getenv("PARSE_INTERVAL_MINUTES", 30))
        logger.info(f"Parser service initialized with {self.parse_interval} minutes interval")
        
    async def get_users_from_auth_service(self):
        """Получаем пользователей из auth-service"""
        try:
            logger.info("Fetching users from auth-service")
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.auth_service_url}/settings/',
                    timeout=10
                ) as response:
                    
                    if response.status == 200:
                        users = await response.json()
                        logger.info(f"Successfully fetched {len(users)} users from auth-service")
                        return users
                    else:
                        logger.error(f"Auth service returned status: {response.status}")
                        return []
                        
        except aiohttp.ClientError as e:
            logger.error(f"Network error connecting to auth-service: {e}")
            return []
        except asyncio.TimeoutError:
            logger.error("Timeout connecting to auth-service")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in get_users_from_auth_service: {e}")
            return []
    
    async def parse_all_schedules(self):
        """Основная функция парсинга"""
        try:
            logger.info("Starting scheduled parsing cycle")
            users = await self.get_users_from_auth_service()
            
            if not users:
                logger.warning("No users found for parsing")
                return
            
            logger.info(f"Processing {len(users)} users")
            
            # Парсим для каждого пользователя
            for user_data in users:
                user_id = user_data.get('telegram_id', 'unknown')
                group_name = user_data.get('group_name', 'unknown')
                logger.info(f"Processing user {user_id}, group: {group_name}")
                await self.parse_user_schedule(user_data)
                
            logger.info("Scheduled parsing cycle completed")
                
        except Exception as e:
            logger.error(f"Critical error in parse_all_schedules: {e}", exc_info=True)
    
    async def parse_user_schedule(self, user_data):
        """Парсинг для конкретного пользователя"""
        try:
            settings = user_data.get('schedule_settings', {})
            base_url = settings.get("base_url", "https://rshu.ru")
            schedule_url = settings.get("schedule_url", "/schedule")
            full_url = base_url + schedule_url
            
            logger.debug(f"Parsing URL: {full_url}")
            html = await self.parse_page(full_url)
            
            if not html:
                logger.warning(f"No HTML content for {full_url}")
                return
            
            # Парсим расписание занятий
            group_name = user_data['group_name']
            schedule_link = self.find_schedule_link(html, group_name)
            if schedule_link:
                logger.info(f"Found schedule link for {group_name}: {schedule_link}")
                await self.process_schedule(user_data, schedule_link, "schedule")
            else:
                logger.warning(f"No schedule link found for {group_name}")
            
            # Парсим расписание экзаменов
            exams_text = f"{group_name} (зачеты экзамены)"
            exams_link = self.find_schedule_link(html, exams_text)
            if exams_link:
                logger.info(f"Found exams link for {group_name}: {exams_link}")
                await self.process_schedule(user_data, exams_link, "exams")
            else:
                logger.debug(f"No exams link found for {group_name}")
                
        except Exception as e:
            logger.error(f"Error parsing user schedule: {e}", exc_info=True)
    
    async def parse_page(self, url: str):
        """Парсинг HTML страницы"""
        try:
            logger.debug(f"Downloading page: {url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as response:
                    response.raise_for_status()
                    html = await response.text()
                    logger.debug(f"Successfully downloaded page: {url}")
                    return html
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error parsing page {url}: {e}")
            return None
        except asyncio.TimeoutError:
            logger.error(f"Timeout parsing page {url}")
            return None
        except Exception as e:
            logger.error(f"Error parsing page {url}: {e}")
            return None
    
    def find_schedule_link(self, html: str, target_text: str):
        """Поиск ссылки на расписание"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            for a in soup.find_all('a'):
                if a.text.strip() == target_text:
                    link = a.get('href')
                    logger.debug(f"Found link for '{target_text}': {link}")
                    return link
            logger.debug(f"No link found for text: '{target_text}'")
            return None
        except Exception as e:
            logger.error(f"Error finding link for '{target_text}': {e}")
            return None
    
    async def download_file(self, url: str):
        """Скачивание файла"""
        try:
            logger.debug(f"Downloading file: {url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=20) as response:
                    response.raise_for_status()
                    content = await response.read()
                    file_hash = hashlib.sha256(content).hexdigest()
                    logger.debug(f"Successfully downloaded file: {url}, size: {len(content)} bytes")
                    return content, file_hash
        except Exception as e:
            logger.error(f"Error downloading file {url}: {e}")
            return None, None
    
    async def process_schedule(self, user_data, link, schedule_type):
        """Обработка конкретного расписания"""
        try:
            settings = user_data.get('schedule_settings', {})
            base_url = settings.get("base_url", "https://rshu.ru")
            full_url = base_url + link
            
            logger.info(f"Processing {schedule_type} schedule: {full_url}")
            content, new_hash = await self.download_file(full_url)
            
            if not content:
                logger.warning(f"No content for {schedule_type} schedule")
                return
            
            # Здесь должна быть логика проверки хеша
            # Пока всегда отправляем уведомление для теста
            message = f"📅 Новое расписание {schedule_type} для группы {user_data['group_name']}"
            add_notification(user_data['telegram_id'], message, content)
            logger.info(f"Notification added for user {user_data['telegram_id']}")
            
        except Exception as e:
            logger.error(f"Error processing {schedule_type} schedule: {e}", exc_info=True)

async def main():
    """Основная асинхронная функция"""
    try:
        logger.info("🚀 Starting parser service")
        
        parser = ParserService()
        
        # Запускаем сразу при старте
        logger.info("Running initial parsing")
        await parser.parse_all_schedules()
        
        # Настраиваем планировщик
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            parser.parse_all_schedules,
            IntervalTrigger(minutes=parser.parse_interval),
            id='parse_schedules'
        )
        scheduler.start()
        
        logger.info(f"✅ Scheduler started. Parsing every {parser.parse_interval} minutes.")
        
        # Бесконечный цикл с обработкой прерываний
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
    finally:
        if 'scheduler' in locals():
            scheduler.shutdown()
        logger.info("Parser service stopped")

if __name__ == "__main__":
    asyncio.run(main())