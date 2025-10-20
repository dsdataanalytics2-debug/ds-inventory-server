# Use Python 3.11 slim image
FROM python:3.11.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-minimal.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir --only-binary=all --prefer-binary -r requirements.txt

# Copy application code
COPY . .

# Run database migration
RUN python add_name_column.py || true

# Expose port
EXPOSE $PORT

# Start command with dynamic port
CMD uvicorn main:app --host 0.0.0.0 --port $PORT --no-reload
