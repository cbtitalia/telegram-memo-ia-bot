FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (smbclient)
RUN apt-get update && apt-get install -y --no-install-recommends \
    smbclient \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .

# Create logs directory
RUN mkdir -p /app/logs

# Run bot
CMD ["python", "main.py"]
