from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database import get_db, engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class UserSettingsCreate(BaseModel):
    telegram_id: str
    group_name: str
    schedule_settings: dict = None

class UserSettingsResponse(BaseModel):
    id: int
    telegram_id: str
    group_name: str
    schedule_settings: dict

@app.post("/settings/", response_model=UserSettingsResponse)
async def create_settings(settings: UserSettingsCreate, db: Session = Depends(get_db)):
    db_settings = models.UserSettings(**settings.dict())
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings

@app.get("/settings/{telegram_id}", response_model=UserSettingsResponse)
async def get_settings(telegram_id: str, db: Session = Depends(get_db)):
    settings = db.query(models.UserSettings).filter(models.UserSettings.telegram_id == telegram_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

@app.get("/settings/", response_model=List[UserSettingsResponse])
async def get_all_settings(db: Session = Depends(get_db)):
    return db.query(models.UserSettings).all()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}