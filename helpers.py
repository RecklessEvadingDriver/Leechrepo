import os
import asyncio
from pathlib import Path
from typing import Optional, Callable
from telegram import Update
from telegram.constants import ParseMode

async def upload_file_to_telegram(update: Update, filepath: str, 
                                  progress_callback: Optional[Callable] = None):
    """
    Upload file to Telegram
    
    Args:
        update: Telegram update object
        filepath: Path to file to upload
        progress_callback: Optional callback for progress updates
    """
    path = Path(filepath)
    
    if not path.exists():
        await update.message.reply_text(f"File not found: {filepath}")
        return
    
    file_size = path.stat().st_size
    
    # Telegram file size limits
    # 50MB for non-premium, 2GB for premium (we'll use 2GB as default)
    MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
    
    if file_size > MAX_FILE_SIZE:
        await update.message.reply_text(
            f"⚠️ File is too large ({format_bytes(file_size)}). "
            f"Maximum supported size is {format_bytes(MAX_FILE_SIZE)}"
        )
        return
    
    # Determine file type based on extension
    extension = path.suffix.lower()
    
    try:
        if extension in ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm']:
            # Upload as video
            await update.message.reply_video(
                video=open(filepath, 'rb'),
                caption=f"📹 {path.name}\n💾 Size: {format_bytes(file_size)}",
                supports_streaming=True,
                read_timeout=300,
                write_timeout=300
            )
        elif extension in ['.mp3', '.m4a', '.wav', '.flac', '.ogg', '.aac']:
            # Upload as audio
            await update.message.reply_audio(
                audio=open(filepath, 'rb'),
                caption=f"🎵 {path.name}\n💾 Size: {format_bytes(file_size)}",
                read_timeout=300,
                write_timeout=300
            )
        elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
            # Upload as photo
            await update.message.reply_photo(
                photo=open(filepath, 'rb'),
                caption=f"🖼️ {path.name}\n💾 Size: {format_bytes(file_size)}",
                read_timeout=300,
                write_timeout=300
            )
        else:
            # Upload as document
            await update.message.reply_document(
                document=open(filepath, 'rb'),
                caption=f"📄 {path.name}\n💾 Size: {format_bytes(file_size)}",
                read_timeout=300,
                write_timeout=300
            )
        
        await update.message.reply_text("✅ Upload completed!")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Upload failed: {str(e)}")


async def upload_folder_to_telegram(update: Update, folder_path: str):
    """
    Upload all files in a folder to Telegram
    
    Args:
        update: Telegram update object
        folder_path: Path to folder
    """
    path = Path(folder_path)
    
    if not path.exists() or not path.is_dir():
        await update.message.reply_text(f"Folder not found: {folder_path}")
        return
    
    files = list(path.rglob('*'))
    files = [f for f in files if f.is_file()]
    
    if not files:
        await update.message.reply_text("No files found in the folder")
        return
    
    await update.message.reply_text(f"📦 Found {len(files)} file(s). Starting upload...")
    
    for i, file in enumerate(files, 1):
        await update.message.reply_text(f"Uploading {i}/{len(files)}: {file.name}")
        await upload_file_to_telegram(update, str(file))
        await asyncio.sleep(1)  # Small delay between uploads


def format_bytes(bytes_num: int) -> str:
    """Format bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_num < 1024.0:
            return f"{bytes_num:.2f} {unit}"
        bytes_num /= 1024.0
    return f"{bytes_num:.2f} PB"


def format_speed(bytes_per_sec: int) -> str:
    """Format speed to human-readable format"""
    return f"{format_bytes(bytes_per_sec)}/s"


def format_time(seconds: int) -> str:
    """Format seconds to human-readable time"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def is_url(text: str) -> bool:
    """Check if text is a URL"""
    return text.startswith(('http://', 'https://'))


def is_magnet(text: str) -> bool:
    """Check if text is a magnet link"""
    return text.startswith('magnet:')


def is_torrent_file(text: str) -> bool:
    """Check if text is a torrent file path"""
    return text.endswith('.torrent')


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize and truncate filename to filesystem limits
    
    Args:
        filename: Original filename
        max_length: Maximum filename length (default 255 for most filesystems)
        
    Returns:
        Sanitized filename with proper length and safe characters
    """
    import re
    
    # Remove or replace invalid characters for filesystems
    # Keep alphanumeric, dots, hyphens, underscores, and spaces
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    # If filename is empty after sanitization, use a default
    if not filename:
        filename = 'download'
    
    # Split filename and extension
    if '.' in filename:
        name_parts = filename.rsplit('.', 1)
        name = name_parts[0]
        ext = '.' + name_parts[1]
    else:
        name = filename
        ext = ''
    
    # Calculate maximum length for name part
    # Reserve space for extension
    max_name_length = max_length - len(ext)
    
    # Truncate name if necessary
    if len(name) > max_name_length:
        name = name[:max_name_length]
    
    # Reconstruct filename
    sanitized = name + ext
    
    # Final check to ensure total length is within limit
    if len(sanitized) > max_length:
        # If still too long, truncate more aggressively
        sanitized = sanitized[:max_length]
    
    return sanitized
