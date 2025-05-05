# File: your_chat_project/app/config.py
import os
from dotenv import load_dotenv
from datetime import timedelta
# Determine the base directory of the project
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Load environment variables from .env file located in the base directory
# This ensures variables are loaded even if not running via docker-compose
load_dotenv(os.path.join(basedir, '.env'))
class Config:
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-should-really-change-this'
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        REDIS_URL = os.environ.get('REDIS_URL')

        # Token Settings
        # Example: Token valid for 1 day
        JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=10) # Or hours=1, minutes=30 etc.

    

    # Add other configurations as needed

    