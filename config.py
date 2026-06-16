import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///telegram_helper.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_ID = int(os.getenv('API_ID', '0'))
    API_HASH = os.getenv('API_HASH', '')
    SESSIONS_DIR = os.getenv('SESSIONS_DIR', 'sessions')
