# telegram-service/bot.py
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start_command(update: Update, context):
    """Обработчик команды /start"""
    logger.info(f"Received /start from {update.effective_user.id}")
    await update.message.reply_text(
        "👋 Добро пожаловать в бот расписания РГГУ!\n\n"
        "Введите номер вашей группы (например: ИУ5-64Б):"
    )

async def handle_message(update: Update, context):
    """Обработчик текстовых сообщений"""
    text = update.message.text
    logger.info(f"Received message: {text} from {update.effective_user.id}")
    await update.message.reply_text(f"Вы сказали: {text}")

def create_bot():
    """Создание и настройка бота"""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return None
    
    try:
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        logger.info("Bot created successfully")
        return application
        
    except Exception as e:
        logger.error(f"Error creating bot: {e}")
        return None