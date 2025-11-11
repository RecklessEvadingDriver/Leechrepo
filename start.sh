#!/bin/bash
# Startup script for Telegram Leech Bot

echo "🚀 Starting Telegram Leech Bot..."

# Check if aria2c is installed
if command -v aria2c &> /dev/null; then
    echo "✅ aria2c found"
    
    # Check if aria2 is already running
    if pgrep -x "aria2c" > /dev/null; then
        echo "⚠️  aria2c is already running"
    else
        echo "🔄 Starting aria2c with RPC..."
        aria2c --enable-rpc --rpc-listen-all=false --rpc-listen-port=6800 -D
        sleep 2
        echo "✅ aria2c started"
    fi
else
    echo "⚠️  aria2c not found. Torrent/magnet downloads will not work."
    echo "   Install aria2: sudo apt-get install aria2 (Ubuntu/Debian)"
    echo "                  brew install aria2 (macOS)"
fi

# Check if config.env exists
if [ ! -f "config.env" ]; then
    echo "❌ config.env not found!"
    echo "   Please copy config.env.example to config.env and configure it:"
    echo "   cp config.env.example config.env"
    exit 1
fi

# Check if Python dependencies are installed
echo "🔍 Checking Python dependencies..."
if ! python3 -c "import telegram" &> /dev/null; then
    echo "⚠️  Dependencies not installed. Installing..."
    pip install -r requirements.txt
fi

# Start the bot
echo "✅ Starting bot..."
python3 bot.py
