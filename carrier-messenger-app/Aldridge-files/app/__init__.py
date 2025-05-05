# File: your_chat_project/app/__init__.py

import os
import redis
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate # Import Migrate
from .config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate() # Initialize Migrate instance
redis_client = None

def create_app(config_class=Config):
    """Application Factory"""
    global redis_client

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions with the app
    db.init_app(app)
    migrate.init_app(app, db) # Initialize Migrate with app and db

    # --- Redis Connection ---
    # (Keep the existing Redis connection logic here...)
    try:
        redis_client = redis.from_url(app.config['REDIS_URL'], decode_responses=True)
        redis_client.ping()
        app.logger.info("Successfully connected to Redis.")
    except redis.exceptions.ConnectionError as e:
        redis_client = None
        app.logger.error(f"Could not connect to Redis: {e}")

    # --- MySQL Connection Test (via SQLAlchemy) ---
    # (Keep the existing MySQL connection test logic here...)
    with app.app_context():
        try:
            db.session.execute(db.text('SELECT 1'))
            app.logger.info("Successfully connected to MySQL database.")
        except Exception as e:
            app.logger.error(f"Could not connect to MySQL database: {e}")


    # --- Simple Routes for Testing ---
    # (Keep the existing routes here...)
    @app.route('/ping')
    def ping():
        return jsonify(message="Flask app is alive!")

    @app.route('/test-connections')
    def test_connections():
        results = {}
        # Test Redis
        if redis_client:
            try:
                redis_client.ping()
                results['redis'] = 'Connected'
            except redis.exceptions.ConnectionError:
                results['redis'] = 'Connection Failed'
        else:
             results['redis'] = 'Client Not Initialized'

        # Test MySQL
        try:
            # Use a try-with-resources pattern for session management
            with db.session.begin():
                 db.session.execute(db.text('SELECT 1'))
            results['mysql'] = 'Connected'
        except Exception as e:
            results['mysql'] = f'Connection Failed: {e}'
            # No need for explicit remove() when using context manager

        return jsonify(results)

    # --- Import models AFTER db is initialized and within app context scope if needed ---
    # It's often safer to import models inside functions or blueprints where they are used,
    # or ensure db is fully initialized before model definitions are processed.
    # For Flask-Migrate, importing them globally after db init is usually fine.
    from . import models # Import models so Flask-Migrate can see them

    # Register Blueprints later
    # from .api import routes_auth, routes_messages
    # app.register_blueprint(routes_auth.bp, url_prefix='/auth')
    # app.register_blueprint(routes_messages.bp, url_prefix='/')

    return app

