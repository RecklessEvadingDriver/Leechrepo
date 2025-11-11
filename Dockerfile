FROM python:3.11-slim

# Install aria2
RUN apt-get update && \
    apt-get install -y aria2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY bot.py .
COPY config.py .
COPY downloader.py .
COPY helpers.py .

# Create downloads directory
RUN mkdir -p /app/downloads

# Start aria2 and the bot
CMD aria2c --enable-rpc --rpc-listen-all=true --rpc-listen-port=6800 -D && \
    python bot.py
