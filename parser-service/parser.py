import aiohttp
import hashlib
from bs4 import BeautifulSoup
import asyncio

class ScheduleParser:
    def __init__(self, db_session):
        self.db = db_session
    
    async def parse_page(self, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()
    
    def find_schedule_link(self, html: str, target_text: str):
        soup = BeautifulSoup(html, 'lxml')
        for a in soup.find_all('a'):
            if a.text.strip() == target_text:
                return a.get('href')
        return None
    
    async def download_file(self, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.read()
                file_hash = hashlib.sha256(content).hexdigest()
                return content, file_hash
    
    def get_saved_hash(self, user_id: str, schedule_type: str):
        # Здесь будет логика получения хеша из БД
        return None