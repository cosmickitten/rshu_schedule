#!/usr/bin/env python3
import aiohttp
import asyncio
import hashlib
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from typing import Optional, Tuple, List

class FileHasher:
    """Класс для потокового хеширования"""
    def __init__(self, buf_size: int = 65536):
        self.BUF_SIZE = buf_size
    
    async def hash_bytes(self, data: bytes) -> str:
        """Хеширование данных"""
        return hashlib.sha256(data).hexdigest()

class ScheduleDownloader:
    """Класс для загрузки расписаний"""
    def __init__(self):
        self.config = self.load_config()
        self.hasher = FileHasher(int(os.getenv("BUF_SIZE", 65536)))
    
    def load_config(self) -> dict:
        """Загрузка конфигурации"""
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        print(dotenv_path)
        load_dotenv(dotenv_path)
        return {
            'base_url': os.getenv("BASE_URL"),
            'schedule_url': os.getenv("SCHEDULE_URL"),
            'telegram_token': os.getenv("TELEGRAM_TOKEN"),
            'chat_ids': os.getenv("CHAT_IDS").split(','),
            'group_name': os.getenv("GROUP_NAME"),
            'files': {
                'schedule': {
                    'output': os.getenv("SCHEDULE_FILENAME", "schedule.pdf"),
                    'hash': os.getenv("SCHEDULE_HASHFILE", "schedule_hash.txt")
                },
                'exams': {
                    'output': os.getenv("EXAMS_FILENAME", "exams.pdf"),
                    'hash': os.getenv("EXAMS_HASHFILE", "exams_hash.txt")
                }
            }
        }

    async def get_schedule_link(self, session: aiohttp.ClientSession, target_text: str) -> Optional[str]:
        """Поиск ссылки на расписание"""
        async with session.get(self.config['schedule_url']) as response:
            print(target_text)
            html = await response.text()
            soup = BeautifulSoup(html, 'lxml')
            for a in soup.find_all('a'):
                if a.text.strip() == target_text:
                    return a.get('href')
            return None

    async def download_file(self, session: aiohttp.ClientSession, url: str) -> Tuple[bytes, str]:
        """Загрузка файла с вычислением хеша"""
        async with session.get(url) as response:
            content = await response.read()
            file_hash = await self.hasher.hash_bytes(content)
            return content, file_hash

    def get_saved_hash(self, hash_file: str) -> Optional[str]:
        """Получение сохраненного хеша"""
        if os.path.exists(hash_file):
            with open(hash_file, 'r') as f:
                return f.read().strip()
        return None

    async def send_to_telegram(self, session: aiohttp.ClientSession, file_data: bytes, file_name: str):
        """Отправка файла в Telegram"""
        form_data = aiohttp.FormData()
        form_data.add_field('chat_id', self.config['chat_ids'][0])
        form_data.add_field('document', file_data, filename=file_name)
        
        async with session.post(
            f'https://api.telegram.org/bot{self.config["telegram_token"]}/sendDocument',
            data=form_data
        ) as response:
            response.raise_for_status()

    async def process_in_memory(self, session: aiohttp.ClientSession, 
                             schedule_type: str, target_text: str):
        """Основной метод обработки расписания"""
        conf = self.config['files'][schedule_type]
        
        link = await self.get_schedule_link(session, target_text)
        if not link:
            print(f"Ссылка для {schedule_type} не найдена")
            return
            
        file_url = f"{self.config['base_url']}{link}" if self.config['base_url'] else link
        try:
            file_data, new_hash = await self.download_file(session, file_url)
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return

        old_hash = self.get_saved_hash(conf['hash'])
        
        if old_hash != new_hash:
            with open(conf['output'], 'wb') as f:
                f.write(file_data)
            with open(conf['hash'], 'w') as f:
                f.write(new_hash)
            await self.send_to_telegram(session, file_data, conf['output'])
            print(f"Обновлено {schedule_type} расписание")
        else:
            print(f"Изменений в {schedule_type} нет")

async def main():
    downloader = ScheduleDownloader()
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            downloader.process_in_memory(session, 'schedule', downloader.config['group_name']),
            downloader.process_in_memory(session, 'exams', f"{downloader.config['group_name']} (зачеты, экзамены)")
        ]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())