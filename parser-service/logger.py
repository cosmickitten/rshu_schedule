# parser-service/logger.py
import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name: str) -> logging.Logger:
    """Настройка логгера с выводом в консоль и файл"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Консольный handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # File handler (ротация логов)
    file_handler = RotatingFileHandler(
        '/app/parser.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Добавляем handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Глобальный логгер
logger = setup_logger('parser-service')