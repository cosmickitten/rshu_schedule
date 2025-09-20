# parser-service/wait_for_services.py
import asyncio
import aiohttp
import os
import time

async def wait_for_service(url: str, timeout: int = 300):
    """Ожидание запуска сервиса"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status < 500:
                        print(f"Service {url} is ready!")
                        return True
        except Exception:
            pass
        
        print(f"Waiting for {url}...")
        await asyncio.sleep(5)
    
    print(f"Timeout waiting for {url}")
    return False