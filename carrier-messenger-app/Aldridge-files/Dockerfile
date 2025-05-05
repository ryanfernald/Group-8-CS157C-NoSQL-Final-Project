# Dockerfile
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port Gunicorn will run on
EXPOSE 5000

# Command to run the app using Gunicorn
# It looks for a 'create_app' function in the 'run.py' module/file
# If your factory is in app/__init__.py, use "app:create_app()"
# For now, assuming run.py will create the app instance
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]