from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from database import Base

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=False)
    group_name = Column(String, nullable=False)
    schedule_settings = Column(JSON, default={
        "base_url": "https://rshu.ru",
        "schedule_url": "/schedule",
        "files": {
            "schedule": {"output": "schedule.pdf", "hash": "schedule_hash.txt"},
            "exams": {"output": "exams.pdf", "hash": "exams_hash.txt"}
        }
    })
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())