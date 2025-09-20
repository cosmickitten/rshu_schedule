from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio
import os
from handlers import start_command, handle_group_input, help_command

app = FastAPI()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Инициализация бота
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Добавление обработчиков
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_group_input))

@app.post("/webhook")
async def webhook(request: Request):
    update = Update.de_json(await request.json(), application.bot)
    await application.process_update(update)
    return {"status": "ok"}

@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.start()
    # Установка webhook (в продакшене)
    # await application.bot.set_webhook("https://your-domain.com/webhook")

@app.on_event("shutdown")
async def shutdown():
    await application.stop()
    await application.shutdown()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}