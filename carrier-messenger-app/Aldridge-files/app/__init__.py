# File: your_chat_project/app/__init__.py

import os
import redis
import logging # Import logging
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from .config import Config

# Configure basic logging for debugging startup
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


db = SQLAlchemy()
migrate = Migrate()
scheduler = APScheduler()
redis_client = None

def create_app(config_class=Config):
    log.info("create_app called...") # Log entry into factory
    global redis_client
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Set Flask logger level (optional, good for seeing Flask logs too)
    app.logger.setLevel(logging.INFO)

    # Initialize extensions
    log.info("Initializing extensions...")
    db.init_app(app)
    migrate.init_app(app, db)
    log.info("DB and Migrate initialized.")

    # --- Redis Connection ---
    try:
        redis_client = redis.from_url(app.config['REDIS_URL'], decode_responses=True)
        redis_client.ping()
        app.logger.info("Successfully connected to Redis.")
    except redis.exceptions.ConnectionError as e:
        redis_client = None
        app.logger.error(f"Could not connect to Redis: {e}")

    # --- MySQL Connection Test ---
    with app.app_context():
        try:
            with db.session.begin():
                db.session.execute(db.text('SELECT 1'))
            app.logger.info("Successfully connected to MySQL database.")
        except Exception as e:
            app.logger.error(f"Could not connect to MySQL database: {e}")

    # --- Import models ---
    from . import models
    log.info("Models imported.")

    # --- Register Blueprints ---
    from .api.routes_auth import auth_bp
    app.register_blueprint(auth_bp)
    from .api.routes_chats import chats_bp
    app.register_blueprint(chats_bp)
    log.info("Blueprints registered.")

    # --- Configure and Start APScheduler ---
    # Removed the state check for debugging purposes
    log.info("Attempting to initialize and start APScheduler...")
    try:
        scheduler.init_app(app)
        log.info("APScheduler initialized.")

        # Import the task function
        from .services import flush_service
        log.info("Imported flush_service.")

        # Check if job already exists before adding (optional, good practice)
        if not scheduler.get_job('flush_redis_to_mysql'):
             scheduler.add_job(id='flush_redis_to_mysql', func=flush_service.flush_job, trigger='interval', minutes=1)
             log.info("Added APScheduler job 'flush_redis_to_mysql'.")
        else:
             log.info("APScheduler job 'flush_redis_to_mysql' already exists.")

        scheduler.start()
        log.info("APScheduler started successfully.") # Log success
    except Exception as e:
        log.error(f"APScheduler failed to initialize or start: {e}", exc_info=True)


    # --- Simple Routes for Testing ---
    @app.route('/ping')
    def ping():
        return jsonify(message="Flask app is alive!")

    @app.route('/test-connections')
    def test_connections():
        results = {}
        if redis_client:
            try:
                redis_client.ping()
                results['redis'] = 'Connected'
            except redis.exceptions.ConnectionError:
                results['redis'] = 'Connection Failed'
        else:
            results['redis'] = 'Client Not Initialized'
        try:
            with db.session.begin():
                db.session.execute(db.text('SELECT 1'))
            results['mysql'] = 'Connected'
        except Exception as e:
            results['mysql'] = f'Connection Failed: {e}'
        return jsonify(results)

    log.info("create_app finished.") # Log exit from factory
    return app

