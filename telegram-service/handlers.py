from telegram import Update
from telegram.ext import ContextTypes
import aiohttp
import os

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Добро пожаловать в бот расписания РГГУ!\n\n"
        "Введите номер вашей группы (например: ИУ5-64Б):"
    )

async def handle_group_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_name = update.message.text.strip()
    telegram_id = str(update.effective_user.id)
    
    # Сохраняем настройки через Auth Service
    async with aiohttp.ClientSession() as session:
        payload = {
            "telegram_id": telegram_id,
            "group_name": group_name
        }
        async with session.post(
            "http://auth-service:8000/settings/",
            json=payload
        ) as response:
            if response.status == 200:
                await update.message.reply_text(
                    f"✅ Группа {group_name} успешно сохранена!\n"
                    f"Теперь вы будете получать уведомления о новых расписаниях."
                )
            else:
                await update.message.reply_text(
                    "❌ Ошибка сохранения. Попробуйте позже."
                )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Доступные команды:\n"
        "/start - начать работу\n"
        "/help - помощь\n"
        "Просто введите номер группы для настройки"
    )