# Quick Start Guide

## Prerequisites

1. **Python 3.8+** installed
2. **aria2** installed (for torrent/magnet support)
3. **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)

## Step-by-Step Setup

### 1. Get Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the prompts to create your bot
4. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Get Your User ID (Optional but recommended)

1. Search for [@userinfobot](https://t.me/userinfobot) on Telegram
2. Start the bot
3. It will show your user ID (e.g., `123456789`)

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install aria2
# Ubuntu/Debian:
sudo apt-get install aria2

# macOS:
brew install aria2

# Windows: Download from https://github.com/aria2/aria2/releases
```

### 4. Configure the Bot

```bash
# Copy the example config
cp config.env.example config.env

# Edit config.env and add your bot token
nano config.env  # or use any text editor
```

**Minimal config.env:**
```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
AUTHORIZED_USERS=123456789
```

### 5. Run the Bot

**Option 1: Using the start script (Recommended)**
```bash
chmod +x start.sh
./start.sh
```

**Option 2: Manual start**
```bash
# Start aria2 RPC (in a separate terminal)
aria2c --enable-rpc --rpc-listen-all=false --rpc-listen-port=6800

# Start the bot
python3 bot.py
```

**Option 3: Using Docker**
```bash
# Build and run with docker-compose
docker-compose up -d
```

## Testing the Bot

1. Open Telegram and search for your bot (use the bot username you created)
2. Start a chat and send `/start`
3. Try downloading a file:
   - Send a direct URL: `https://example.com/video.mp4`
   - Or use command: `/leech https://example.com/video.mp4`

## Common Commands

- `/start` - Show welcome message
- `/help` - Show help information
- `/leech <url>` - Download from URL or magnet
- `/stats` - View bot statistics

## Troubleshooting

### Bot doesn't respond
- Check if the bot is running
- Verify BOT_TOKEN in config.env is correct
- Make sure your user ID is in AUTHORIZED_USERS (if set)

### Torrent/Magnet downloads fail
- Make sure aria2 is installed
- Check if aria2 RPC is running
- Verify ARIA2_HOST and ARIA2_PORT in config.env

### File upload fails
- Check if file size is within Telegram limits (2GB)
- Ensure you have enough disk space
- Check bot permissions in the chat

## Next Steps

- Check [README.md](README.md) for detailed documentation
- Configure additional settings in config.env
- Set up the bot to run automatically on system startup

## Support

If you encounter any issues:
1. Check the logs for error messages
2. Verify your configuration
3. Open an issue on GitHub with details
