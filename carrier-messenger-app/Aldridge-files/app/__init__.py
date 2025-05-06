# File: your_chat_project/app/__init__.py

import os
import redis
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
redis_client = None

def create_app(config_class=Config):
    global redis_client
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

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
    from . import models # Import models so Flask-Migrate can see them

    # --- Register Blueprints ---
    from .api.routes_auth import auth_bp # <-- Make sure this line is NOT commented out
    app.register_blueprint(auth_bp) # <-- Make sure this line is NOT commented out
    from .api.routes_chats import chats_bp # <-- Check this import
    app.register_blueprint(chats_bp)      # <-- Check this registration
    # Register other blueprints later (e.g., for messages)
    # from .api.routes_messages import messages_bp
    # app.register_blueprint(messages_bp)


    # --- Simple Routes for Testing (can be removed later) ---
    @app.route('/ping')
    def ping():
        return jsonify(message="Flask app is alive!")

    @app.route('/test-connections')
    def test_connections():
        # (Keep existing connection test logic)
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

    return app
