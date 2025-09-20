# telegram-service/handlers.py
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
import logging
from api_client import auth_client

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    try:
        logger.info(f"Start command from user: {update.effective_user.id}")
        await update.message.reply_text(
            "👋 Добро пожаловать в бот расписания РГГУ!\n\n"
            "Введите номер вашей группы (например: ИУ5-64Б):",
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        logger.error(f"Error in start_command: {e}")

async def handle_group_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ввода группы"""
    try:
        group_name = update.message.text.strip()
        telegram_id = str(update.effective_user.id)
        
        logger.info(f"Group input from {telegram_id}: {group_name}")
        
        # Сохраняем в auth-service
        success = await auth_client.save_user_settings(telegram_id, group_name)
        
        if success:
            await update.message.reply_text(
                f"✅ Группа {group_name} успешно сохранена!\n"
                f"Теперь вы будете получать уведомления о новых расписаниях.",
                reply_markup=ReplyKeyboardRemove()
            )
            logger.info(f"Successfully processed group {group_name} for user {telegram_id}")
        else:
            await update.message.reply_text(
                "❌ Ошибка при сохранении настроек. Попробуйте позже."
            )
            logger.error(f"Failed to save settings for user {telegram_id}")
            
    except Exception as e:
        logger.error(f"Error in handle_group_input: {e}")
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте снова.")