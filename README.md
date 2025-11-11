# Telegram Leech Bot 🤖

A powerful Telegram bot that can download (leech) and mirror files from various sources:
- 🔗 **Direct URLs** - Download any direct file URL (MP4, MKV, ZIP, etc.)
- 🧲 **Magnet Links** - Download from magnet URIs
- 📦 **Torrent Files** - Download from .torrent files

The bot downloads the files and automatically uploads them to Telegram for easy access!

## ✨ Features

- ✅ Download from direct URLs (including video files like MP4)
- ✅ Download from magnet links
- ✅ Download from torrent files
- ✅ Automatic file type detection and appropriate upload (video, audio, photo, document)
- ✅ Progress tracking during downloads
- ✅ User authorization system
- ✅ Clean and intuitive interface
- ✅ Support for large files (up to 2GB)

## 📋 Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- aria2c installed (for torrent/magnet support)

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/RecklessEvadingDriver/Leechrepo.git
cd Leechrepo
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install aria2 (for torrent/magnet support)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install aria2
```

**macOS:**
```bash
brew install aria2
```

**Windows:**
Download from [aria2 releases](https://github.com/aria2/aria2/releases)

### 4. Configure the bot

Copy the example configuration file and edit it:

```bash
cp config.env.example config.env
```

Edit `config.env` and add your bot token:

```env
BOT_TOKEN=your_bot_token_from_botfather
AUTHORIZED_USERS=your_telegram_user_id  # Optional, leave empty to allow all users
```

To get your Telegram User ID, you can use [@userinfobot](https://t.me/userinfobot)

## 🎮 Usage

### Start the bot

```bash
python bot.py
```

### Using aria2 RPC for torrents/magnets

For better torrent and magnet link support, start aria2 with RPC enabled:

```bash
aria2c --enable-rpc --rpc-listen-all=false --rpc-listen-port=6800
```

Or run it in the background:

```bash
aria2c --enable-rpc --rpc-listen-all=false --rpc-listen-port=6800 -D
```

### Bot Commands

- `/start` - Show welcome message and bot information
- `/help` - Display help and usage instructions
- `/leech <url/magnet>` - Download from URL or magnet link
- `/stats` - View bot statistics

### Quick Examples

**Download from direct URL:**
```
/leech https://example.com/video.mp4
```

Or simply send the URL:
```
https://example.com/video.mp4
```

**Download from magnet link:**
```
/leech magnet:?xt=urn:btih:...
```

**Download from torrent file:**
Just send the .torrent file to the bot!

## 📁 Project Structure

```
Leechrepo/
├── bot.py              # Main bot application
├── config.py           # Configuration management
├── downloader.py       # Download handlers (direct, torrent, magnet)
├── helpers.py          # Helper functions (upload, formatting, etc.)
├── requirements.txt    # Python dependencies
├── config.env.example  # Example configuration file
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## ⚙️ Configuration Options

All configuration is done via the `config.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Your Telegram bot token (required) | - |
| `AUTHORIZED_USERS` | Comma-separated user IDs allowed to use bot | All users |
| `DOWNLOAD_DIR` | Directory to store downloads | `./downloads` |
| `MAX_DOWNLOAD_SIZE` | Maximum download size in bytes | `2147483648` (2GB) |
| `ARIA2_HOST` | Aria2 RPC host | `localhost` |
| `ARIA2_PORT` | Aria2 RPC port | `6800` |
| `ARIA2_SECRET` | Aria2 RPC secret token | - |
| `CHUNK_SIZE` | Upload chunk size in bytes | `524288` (512KB) |

## 🔒 Security

- **User Authorization**: You can restrict bot access to specific Telegram users by setting `AUTHORIZED_USERS` in `config.env`
- **File Size Limits**: Maximum file size is configurable (default 2GB)
- **Private Downloads**: All downloads are stored locally and only accessible to authorized users

## 🐛 Troubleshooting

### Bot doesn't respond
- Make sure your `BOT_TOKEN` is correct in `config.env`
- Check if the bot is running without errors
- Verify your user ID is in `AUTHORIZED_USERS` (if set)

### Torrent/Magnet downloads don't work
- Make sure aria2c is installed and running
- Start aria2 with RPC: `aria2c --enable-rpc`
- Check aria2 configuration in `config.env`

### Upload fails
- Check if the file size is within Telegram limits (2GB for bots)
- Ensure you have enough disk space
- Check bot permissions in the chat

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📧 Support

If you have any questions or need help, please open an issue on GitHub.

## ⭐ Show your support

Give a ⭐️ if this project helped you!