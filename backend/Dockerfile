FROM python:3.10-slim-bullseye

WORKDIR /app

# Install system dependencies and Docker CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    docker.io \
    gcc \
    python3-dev \
    libpango1.0-dev \
    libharfbuzz-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose application port
EXPOSE 8000

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]