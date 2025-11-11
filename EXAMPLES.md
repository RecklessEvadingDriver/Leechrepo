# Usage Examples

This document provides detailed examples of how to use the Telegram Leech Bot.

## Basic Examples

### 1. Download from Direct URL

Simply send the URL to the bot:

```
https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4
```

Or use the command:

```
/leech https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4
```

The bot will:
1. Download the file
2. Show progress updates
3. Upload to Telegram as a video (automatically detects MP4)

### 2. Download from Magnet Link

Send a magnet link:

```
magnet:?xt=urn:btih:c12fe1c06bba254a9dc9f519b335aa7c1367a88a
```

Or:

```
/leech magnet:?xt=urn:btih:c12fe1c06bba254a9dc9f519b335aa7c1367a88a
```

The bot will:
1. Start downloading via aria2
2. Show progress with speed and ETA
3. Upload files to Telegram when complete

### 3. Download from Torrent File

Just send the `.torrent` file to the bot as a document. The bot will automatically:
1. Download the torrent file
2. Start downloading the content
3. Upload to Telegram

## Advanced Examples

### Multiple File Downloads

For torrents with multiple files, the bot will:
- Upload each file separately
- Show progress for each file
- Organize files in the correct format

### Large Files

For files larger than 2GB:
- Bot will notify you about the size
- Premium Telegram accounts support up to 4GB
- Consider splitting large files

## File Type Detection

The bot automatically detects and uploads files in the appropriate format:

| File Extension | Upload Type | Example |
|---------------|-------------|---------|
| `.mp4`, `.mkv`, `.avi` | Video | Supports streaming |
| `.mp3`, `.m4a`, `.flac` | Audio | With metadata |
| `.jpg`, `.png`, `.gif` | Photo | Compressed |
| `.zip`, `.rar`, `.pdf` | Document | As-is |

## Bot Commands Reference

### /start
Shows welcome message and bot capabilities

```
/start
```

### /help
Displays detailed help and usage instructions

```
/help
```

### /leech
Download from URL or magnet link

```
/leech https://example.com/file.mp4
/leech magnet:?xt=urn:btih:...
```

### /stats
View bot statistics

```
/stats
```

Output includes:
- Download directory path
- Number of files
- Total size used

## Tips and Best Practices

### 1. Direct URLs
- Use direct download links (not preview pages)
- Ensure the URL points directly to the file
- Check if the file is publicly accessible

### 2. Magnet Links
- Ensure aria2 is running
- Wait for metadata to be fetched (may take time)
- Popular torrents download faster

### 3. Large Downloads
- Be patient with large files
- Don't send multiple large downloads simultaneously
- Monitor disk space

### 4. Security
- Only use the bot in private chats
- Don't share your bot token
- Set AUTHORIZED_USERS to restrict access

## Troubleshooting Examples

### Issue: Bot doesn't respond
**Solution:**
```bash
# Check if bot is running
ps aux | grep bot.py

# Check logs
tail -f /var/log/leechbot.log
```

### Issue: Download fails
**Possible causes:**
- Invalid URL
- File not accessible
- aria2 not running
- Network issues

**Check:**
```bash
# Test URL manually
curl -I https://example.com/file.mp4

# Check aria2 status
ps aux | grep aria2
```

### Issue: Upload fails
**Common reasons:**
- File too large (>2GB)
- Network timeout
- Bot token expired

## Integration Examples

### Using with Systemd (Linux)

Create `/etc/systemd/system/leechbot.service`:

```ini
[Unit]
Description=Telegram Leech Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/Leechrepo
ExecStart=/usr/bin/python3 /path/to/Leechrepo/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable leechbot
sudo systemctl start leechbot
sudo systemctl status leechbot
```

### Using with Screen (Quick deployment)

```bash
# Start in screen session
screen -S leechbot
cd /path/to/Leechrepo
./start.sh

# Detach: Ctrl+A, then D
# Reattach: screen -r leechbot
```

### Using with Docker

```bash
# Build the image
docker build -t telegram-leech-bot .

# Run the container
docker run -d \
  --name leechbot \
  --env-file config.env \
  -v $(pwd)/downloads:/app/downloads \
  telegram-leech-bot
```

## API Examples (For Developers)

If you want to extend the bot:

### Adding a Custom Command

```python
@authorized_only
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /custom command"""
    await update.message.reply_text("Custom response")

# Add to main():
application.add_handler(CommandHandler("custom", custom_command))
```

### Custom Progress Callback

```python
async def my_progress_callback(downloaded, total, percentage, speed=0):
    print(f"Downloaded: {percentage:.1f}%")
```

## More Examples

For more examples and community contributions, check:
- GitHub Issues
- Discussions
- Wiki (if available)
