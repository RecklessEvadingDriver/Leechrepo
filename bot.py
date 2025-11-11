#!/usr/bin/env python3
"""
Telegram Leech Bot

A bot that can download/leech from:
- Direct URLs (including MP4 and other video files)
- Magnet links
- Torrent files

And then upload the files to Telegram
"""

import os
import asyncio
import logging
from pathlib import Path
from functools import wraps
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ParseMode

from config import Config
from downloader import DownloadManager
from helpers import (
    upload_file_to_telegram,
    upload_folder_to_telegram,
    format_bytes,
    format_speed,
    format_time,
    is_url,
    is_magnet,
    is_torrent_file,
)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Authorization decorator
def authorized_only(func):
    """Decorator to check if user is authorized"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        # If no authorized users specified, allow all
        if not Config.AUTHORIZED_USERS:
            return await func(update, context)
        
        if user_id not in Config.AUTHORIZED_USERS:
            await update.message.reply_text(
                "⛔ You are not authorized to use this bot."
            )
            return
        
        return await func(update, context)
    return wrapper


# Command handlers
@authorized_only
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """
🤖 **Telegram Leech Bot**

Welcome! I can download and upload files from:
• 🔗 Direct URLs (MP4, MKV, and other files)
• 🧲 Magnet links
• 📦 Torrent files

**Commands:**
/start - Show this message
/help - Show help information
/leech <url/magnet> - Download and upload to Telegram
/stats - Show bot statistics

**Usage:**
Simply send me a direct URL, magnet link, or torrent file, and I'll download and upload it for you!
"""
    await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)


@authorized_only
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📖 **Help & Usage**

**Supported Sources:**
1️⃣ Direct URLs:
   `https://example.com/video.mp4`
   
2️⃣ Magnet Links:
   `magnet:?xt=urn:btih:...`
   
3️⃣ Torrent Files:
   Just send the .torrent file

**Commands:**
• `/leech <url>` - Download from URL/magnet
• `/cancel` - Cancel current download
• `/stats` - View statistics

**Examples:**
`/leech https://example.com/file.mp4`
`/leech magnet:?xt=urn:btih:abc123...`

Or just send the link directly!
"""
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


@authorized_only
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    download_dir = Path(Config.DOWNLOAD_DIR)
    
    if download_dir.exists():
        files = list(download_dir.rglob('*'))
        files = [f for f in files if f.is_file()]
        total_size = sum(f.stat().st_size for f in files)
        
        stats_text = f"""
📊 **Bot Statistics**

📁 Download Directory: `{Config.DOWNLOAD_DIR}`
📦 Files: {len(files)}
💾 Total Size: {format_bytes(total_size)}
"""
    else:
        stats_text = "📊 No statistics available yet."
    
    await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)


@authorized_only
async def leech_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /leech command"""
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a URL or magnet link.\n"
            "Usage: `/leech <url/magnet>`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    source = ' '.join(context.args)
    await process_download(update, source)


async def process_download(update: Update, source: str):
    """Process download from any source"""
    # Send initial message
    status_message = await update.message.reply_text("⏳ Starting download...")
    
    try:
        # Create download manager
        download_manager = DownloadManager(
            Config.DOWNLOAD_DIR,
            Config.ARIA2_HOST,
            Config.ARIA2_PORT,
            Config.ARIA2_SECRET
        )
        
        # Progress callback
        last_update = [0]  # Use list to allow modification in nested function
        
        async def progress_callback(downloaded, total, percentage, speed=0):
            """Update progress"""
            import time
            current_time = time.time()
            
            # Update every 5 seconds to avoid rate limits
            if current_time - last_update[0] < 5:
                return
            
            last_update[0] = current_time
            
            progress_text = f"""
📥 **Downloading...**

📊 Progress: {percentage:.1f}%
💾 Downloaded: {format_bytes(downloaded)} / {format_bytes(total)}
"""
            if speed > 0:
                progress_text += f"⚡ Speed: {format_speed(speed)}\n"
            
            try:
                await status_message.edit_text(progress_text, parse_mode=ParseMode.MARKDOWN)
            except Exception:
                pass  # Ignore rate limit errors
        
        # Download the file
        await status_message.edit_text("📥 Downloading... Please wait.")
        filepath = await download_manager.download(source, progress_callback)
        
        await status_message.edit_text("✅ Download complete! Starting upload...")
        
        # Upload to Telegram
        path = Path(filepath)
        if path.is_file():
            await upload_file_to_telegram(update, filepath)
        elif path.is_dir():
            await upload_folder_to_telegram(update, filepath)
        else:
            await update.message.reply_text(f"❌ Downloaded path not found: {filepath}")
        
        # Clean up
        try:
            await status_message.delete()
        except Exception:
            pass
        
    except Exception as e:
        logger.error(f"Download error: {e}", exc_info=True)
        await status_message.edit_text(f"❌ Error: {str(e)}")


@authorized_only
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle direct messages (URLs, magnets, etc.)"""
    text = update.message.text.strip()
    
    # Check if it's a URL or magnet link
    if is_url(text) or is_magnet(text):
        await process_download(update, text)
    else:
        await update.message.reply_text(
            "❌ Please send a valid URL or magnet link, or use /help for more info."
        )


@authorized_only
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document uploads (torrent files)"""
    document = update.message.document
    
    if document.file_name.endswith('.torrent'):
        # Download the torrent file
        file = await context.bot.get_file(document.file_id)
        
        torrent_path = Path(Config.DOWNLOAD_DIR) / document.file_name
        torrent_path.parent.mkdir(parents=True, exist_ok=True)
        
        await file.download_to_drive(torrent_path)
        
        # Process the torrent
        await process_download(update, str(torrent_path))
    else:
        await update.message.reply_text("❌ Please send a .torrent file.")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            f"❌ An error occurred: {str(context.error)}"
        )


def main():
    """Start the bot"""
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease create a 'config.env' file with the following variables:")
        print("BOT_TOKEN=your_bot_token_here")
        print("AUTHORIZED_USERS=123456789,987654321  # Optional, comma-separated user IDs")
        print("DOWNLOAD_DIR=./downloads  # Optional")
        return
    
    # Create application
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("leech", leech_command))
    
    # Add message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting bot...")
    print("\n✅ Bot is running! Press Ctrl+C to stop.\n")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
