FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code ensuring 'server' package structure
# We copy current directory (.) into /app/server
COPY . server/

# Add /app to PYTHONPATH so 'server.main' imports work
ENV PYTHONPATH=/app

EXPOSE 8000

# Run Gunicorn with 4 Uvicorn workers
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "server.main:app"]
