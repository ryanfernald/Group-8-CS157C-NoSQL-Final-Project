# File: your_chat_project/app/__init__.py

import os
import redis # Import the redis library
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy
from .config import Config # Import the Config class

# Initialize extensions - but don't associate them with an app yet
db = SQLAlchemy()
redis_client = None # Placeholder for our Redis client instance

def create_app(config_class=Config):
    """Application Factory"""
    global redis_client # Allow modification of the global variable

    app = Flask(__name__)
    app.config.from_object(config_class) # Load configuration from the Config object

    # Initialize Flask extensions with the app
    db.init_app(app)

    # --- Redis Connection ---
    try:
        # Create the Redis client instance using the URL from config
        # decode_responses=True makes redis-py return strings instead of bytes
        redis_client = redis.from_url(app.config['REDIS_URL'], decode_responses=True)
        # Test the connection
        redis_client.ping()
        app.logger.info("Successfully connected to Redis.")
    except redis.exceptions.ConnectionError as e:
        redis_client = None # Ensure client is None if connection failed
        # Log the error - crucial for debugging in Docker
        app.logger.error(f"Could not connect to Redis: {e}")
        # Depending on your app's needs, you might want to exit or handle this
        # For now, we just log it.

    # --- MySQL Connection Test (via SQLAlchemy) ---
    # SQLAlchemy connects lazily, so we perform a simple query inside the app context
    # to force a connection attempt during startup or first request.
    # A more explicit startup check:
    with app.app_context():
        try:
            # db.engine.connect() # This attempts to connect immediately
            # Or execute a simple query
            db.session.execute(db.text('SELECT 1'))
            app.logger.info("Successfully connected to MySQL database.")
        except Exception as e:
            app.logger.error(f"Could not connect to MySQL database: {e}")
            # Handle error as needed for your application

    # --- Simple Routes for Testing ---
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
            db.session.execute(db.text('SELECT 1'))
            db.session.commit() # Or rollback() if just testing
            results['mysql'] = 'Connected'
        except Exception as e:
            results['mysql'] = f'Connection Failed: {e}'
        finally:
            db.session.remove() # Good practice to close session after request

        return jsonify(results)


    # Register Blueprints later (when you create api/routes_*.py)
    # from .api import routes_auth, routes_messages
    # app.register_blueprint(routes_auth.bp, url_prefix='/auth')
    # app.register_blueprint(routes_messages.bp, url_prefix='/')

    return app

