# File: your_chat_project/app/config.py
import os
from dotenv import load_dotenv

# Determine the base directory of the project
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Load environment variables from .env file located in the base directory
# This ensures variables are loaded even if not running via docker-compose
load_dotenv(os.path.join(basedir, '.env'))

class Config: # <--- MAKE SURE THIS LINE EXISTS AND IS SPELLED CORRECTLY
    """Base configuration settings."""
    # Secret key for session management, CSRF protection, etc.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-should-really-change-this'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') # No default needed if always running in Docker
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis configuration
    REDIS_URL = os.environ.get('REDIS_URL')

    # Add other configurations as needed

    