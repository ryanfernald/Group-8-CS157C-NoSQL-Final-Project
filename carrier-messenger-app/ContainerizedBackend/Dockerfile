# Use a minimal Python 3.10 base image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory inside the container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project files into the container
COPY . .

# Expose the port the Flask app will listen on
EXPOSE 5000

# Run the Flask app using Gunicorn with logging to stdout
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "run:app"]
