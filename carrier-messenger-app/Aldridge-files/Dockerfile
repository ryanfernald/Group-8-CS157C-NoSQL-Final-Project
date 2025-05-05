# Dockerfile
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
# Consider using --no-cache-dir if you don't need caching within the build stage
RUN pip install -r requirements.txt

COPY . .

# Expose the port Gunicorn will run on
EXPOSE 5000

# Command to run the app using Gunicorn
# Added --access-logfile - to log HTTP requests to standard output
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "run:app"]
