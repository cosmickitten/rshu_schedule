# auth-service/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import List
from database import get_db, engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class UserSettingsCreate(BaseModel):
    telegram_id: str
    group_name: str

class UserSettingsResponse(BaseModel):
    id: int
    telegram_id: str
    group_name: str
    schedule_settings: dict

@app.post("/settings/", response_model=UserSettingsResponse)
async def create_settings(settings: UserSettingsCreate, db: Session = Depends(get_db)):
    try:
        # Сначала проверяем существует ли пользователь
        existing_user = db.query(models.UserSettings).filter(
            models.UserSettings.telegram_id == settings.telegram_id
        ).first()
        
        if existing_user:
            # Обновляем существующего пользователя
            existing_user.group_name = settings.group_name
            db.commit()
            db.refresh(existing_user)
            return existing_user
        else:
            # Создаем нового пользователя
            db_settings = models.UserSettings(
                telegram_id=settings.telegram_id,
                group_name=settings.group_name,
                schedule_settings=models.DEFAULT_SETTINGS
            )
            db.add(db_settings)
            db.commit()
            db.refresh(db_settings)
            return db_settings
            
    except IntegrityError:
        # Если вдруг возникла конкуренция, пробуем обновить
        db.rollback()
        existing_user = db.query(models.UserSettings).filter(
            models.UserSettings.telegram_id == settings.telegram_id
        ).first()
        if existing_user:
            existing_user.group_name = settings.group_name
            db.commit()
            db.refresh(existing_user)
            return existing_user
        else:
            raise HTTPException(status_code=400, detail="Error saving settings")

@app.get("/settings/{telegram_id}", response_model=UserSettingsResponse)
async def get_settings(telegram_id: str, db: Session = Depends(get_db)):
    settings = db.query(models.UserSettings).filter(models.UserSettings.telegram_id == telegram_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    
    if settings.schedule_settings is None:
        settings.schedule_settings = models.DEFAULT_SETTINGS
        db.commit()
    
    return settings

@app.get("/settings/", response_model=List[UserSettingsResponse])
async def get_all_settings(db: Session = Depends(get_db)):
    settings = db.query(models.UserSettings).all()
    
    for setting in settings:
        if setting.schedule_settings is None:
            setting.schedule_settings = models.DEFAULT_SETTINGS
    
    db.commit()
    return settings

@app.get("/health")
async def health_check():
    return {"status": "healthy"}