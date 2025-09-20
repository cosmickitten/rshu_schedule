from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import asyncio
import os
from parser import ScheduleParser
from redis_client import add_notification
import models

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

async def parse_all_schedules():
    db = SessionLocal()
    try:
        parser = ScheduleParser(db)
        users = db.query(models.UserSettings).all()
        
        for user in users:
            await parse_user_schedule(parser, user)
            
    finally:
        db.close()

async def parse_user_schedule(parser, user):
    try:
        html = await parser.parse_page(user.schedule_settings["base_url"] + user.schedule_settings["schedule_url"])
        
        # Парсим расписание занятий
        schedule_link = parser.find_schedule_link(html, user.group_name)
        if schedule_link:
            await process_schedule(parser, user, schedule_link, "schedule")
        
        # Парсим расписание экзаменов
        exams_link = parser.find_schedule_link(html, f"{user.group_name} (зачеты экзамены)")
        if exams_link:
            await process_schedule(parser, user, exams_link, "exams")
            
    except Exception as e:
        print(f"Error parsing for user {user.telegram_id}: {e}")

async def process_schedule(parser, user, link, schedule_type):
    full_url = user.schedule_settings["base_url"] + link
    content, new_hash = await parser.download_file(full_url)
    old_hash = parser.get_saved_hash(user.telegram_id, schedule_type)
    
    if old_hash != new_hash:
        message = f"Обновлено расписание {schedule_type} для группы {user.group_name}"
        add_notification(user.telegram_id, message, content)

if __name__ == "__main__":
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        parse_all_schedules,
        IntervalTrigger(hours=1),
        id='parse_schedules'
    )
    scheduler.start()
    
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()