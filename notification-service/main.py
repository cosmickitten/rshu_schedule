import asyncio
import aiohttp
from redis_client import get_notification
import os
from telegram import Bot
from telegram.error import TelegramError

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TELEGRAM_TOKEN)

async def send_telegram_message(chat_id: str, message: str, document: bytes = None):
    try:
        if document:
            await bot.send_document(
                chat_id=chat_id,
                document=document,
                caption=message
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=message
            )
        print(f"Message sent to {chat_id}")
    except TelegramError as e:
        print(f"Telegram error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

async def process_notifications():
    while True:
        notification = get_notification()
        if notification:
            try:
                file_data = bytes.fromhex(notification["file_data"]) if notification["file_data"] else None
                await send_telegram_message(
                    notification["telegram_id"],
                    notification["message"],
                    file_data
                )
            except Exception as e:
                print(f"Error processing notification: {e}")
        else:
            await asyncio.sleep(5)

async def main():
    print("Notification service started")
    await process_notifications()

if __name__ == "__main__":
    asyncio.run(main())