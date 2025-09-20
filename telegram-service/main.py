# telegram-service/main.py
from fastapi import FastAPI
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio
import os
import logging
from handlers import start_command, handle_group_input  # Убираем status_command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
bot_application = None

@app.on_event("startup")
async def startup():
    """Запуск бота при старте сервиса"""
    global bot_application
    
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return
    
    try:
        # Создаем и настраиваем бота
        bot_application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Добавляем обработчики - только существующие функции
        bot_application.add_handler(CommandHandler("start", start_command))
        bot_application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_group_input))
        
        # Запускаем
        await bot_application.initialize()
        await bot_application.start()
        
        # Запускаем поллинг в фоне
        asyncio.create_task(run_polling())
        
        logger.info("✅ Telegram bot started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error starting bot: {e}")

async def run_polling():
    """Запуск поллинга"""
    try:
        logger.info("🔄 Starting polling...")
        await bot_application.updater.start_polling()
        logger.info("✅ Polling started successfully!")
        
        # Бесконечный цикл
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"❌ Polling error: {e}")

@app.on_event("shutdown")
async def shutdown():
    """Остановка бота"""
    if bot_application:
        await bot_application.stop()
        await bot_application.shutdown()

@app.get("/health")
async def health():
    return {"status": "healthy", "bot_running": bot_application is not None}