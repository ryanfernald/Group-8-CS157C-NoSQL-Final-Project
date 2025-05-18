import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, '.env'))

# Defines application-wide configuration variables, loaded from environment
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-should-really-change-this'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get('REDIS_URL')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=300)
