# File: your_chat_project/run.py

# Import the factory function from our 'app' package
from app import create_app
import os

# Load environment variables using dotenv, especially useful if running
# locally *without* docker-compose (which uses env_file)
# Keep this commented out if you only run via docker-compose
# from dotenv import load_dotenv
# load_dotenv()

# Create the Flask app instance using the factory
app = create_app()

# The block below is typically for running the Flask development server directly
# (e.g., `python run.py`). Gunicorn (used in Dockerfile) doesn't use this block.
# Keep it commented out or remove if you only run via Docker.
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)

