#!/usr/bin/env python3
import aiohttp
import asyncio
import hashlib
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from typing import Optional, List, Dict, Tuple

class AsyncScheduleParser:
    """Асинхронный парсер расписаний университета"""
    
    def __init__(self):
        self.load_config()
        self.session: Optional[aiohttp.ClientSession] = None
        self.BUF_SIZE = 65536

    def load_config(self):
        """Загружает конфигурацию из .env"""
        load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
        self.config = {
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

    async def __aenter__(self):
        """Инициализация сессии при входе в контекст"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Закрытие сессии при выходе из контекста"""
        if self.session:
            await self.session.close()

    async def fetch_page(self, url: str) -> Optional[str]:
        """Асинхронная загрузка страницы"""
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Page fetch error: {e}")
            return None

    def parse_link(self, html: str, target_text: str) -> Optional[str]:
        """Парсинг ссылки из HTML"""
        soup = BeautifulSoup(html, 'lxml')
        for a in soup.find_all('a'):
            if a.text.strip() == target_text:
                return a.get('href')
        return None

    async def download_file(self, url: str) -> Optional[bytes]:
        """Асинхронная загрузка файла"""
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.read()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"File download error: {e}")
            return None

    def calculate_hash(self, data: bytes) -> str:
        """Вычисление хеша файла"""
        return hashlib.sha256(data).hexdigest()

    def read_hash(self, hash_file: str) -> Optional[str]:
        """Чтение сохраненного хеша"""
        try:
            with open(hash_file, 'r') as f:
                return f.read().strip()
        except IOError:
            return None

    def save_hash(self, hash_value: str, hash_file: str):
        """Сохранение хеша в файл"""
        with open(hash_file, 'w') as f:
            f.write(hash_value)

    async def send_to_telegram(self, file_data: bytes, file_name: str, caption: str):
        """Асинхронная отправка в Telegram"""
        form_data = aiohttp.FormData()
        form_data.add_field('chat_id', self.config['chat_ids'][0])
        form_data.add_field('document', file_data, filename=file_name)
        form_data.add_field('caption', caption)

        try:
            async with self.session.post(
                f'https://api.telegram.org/bot{self.config["telegram_token"]}/sendDocument',
                data=form_data
            ) as response:
                response.raise_for_status()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Telegram send error: {e}")

    async def process_schedule(self, schedule_type: str, target_text: str):
        """Основной процесс обработки расписания"""
        print(f"\nProcessing {schedule_type} schedule...")
        
        conf = self.config['files'][schedule_type]
        html = await self.fetch_page(self.config['schedule_url'])
        if not html:
            return

        file_url = self.parse_link(html, target_text)
        if not file_url:
            return

        full_url = f"{self.config['base_url']}{file_url}" if self.config['base_url'] else file_url
        file_data = await self.download_file(full_url)
        if not file_data:
            return

        current_hash = self.calculate_hash(file_data)
        old_hash = self.read_hash(conf['hash'])

        if old_hash != current_hash:
            print(f"New {schedule_type} schedule detected!")
            self.save_hash(current_hash, conf['hash'])
            await self.send_to_telegram(
                file_data,
                conf['output'],
                f"New {schedule_type} schedule"
            )
        else:
            print(f"No changes in {schedule_type} schedule")

async def main():
    """Точка входа в приложение"""
    async with AsyncScheduleParser() as parser:
        # Обрабатываем обычное расписание
        await parser.process_schedule(
            'schedule',
            parser.config['group_name']
        )
        
        # Обрабатываем расписание экзаменов
        await parser.process_schedule(
            'exams',
            f"{parser.config['group_name']} (зачёты, экзамены)"
        )

if __name__ == "__main__":
    asyncio.run(main())