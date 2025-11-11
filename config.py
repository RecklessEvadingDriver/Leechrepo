import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('config.env')

class Config:
    """Configuration class for the Telegram Leech Bot"""
    
    # Telegram Bot Configuration
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
    
    # Telegram User IDs allowed to use the bot (comma-separated)
    AUTHORIZED_USERS = os.environ.get('AUTHORIZED_USERS', '').split(',')
    AUTHORIZED_USERS = [int(user_id.strip()) for user_id in AUTHORIZED_USERS if user_id.strip()]
    
    # Download settings
    DOWNLOAD_DIR = os.environ.get('DOWNLOAD_DIR', './downloads')
    MAX_DOWNLOAD_SIZE = int(os.environ.get('MAX_DOWNLOAD_SIZE', 2147483648))  # 2GB default
    
    # Aria2 RPC Configuration
    ARIA2_HOST = os.environ.get('ARIA2_HOST', 'localhost')
    ARIA2_PORT = int(os.environ.get('ARIA2_PORT', 6800))
    ARIA2_SECRET = os.environ.get('ARIA2_SECRET', '')
    
    # Upload settings
    CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', 524288))  # 512KB chunks
    
    @staticmethod
    def validate():
        """Validate configuration"""
        if not Config.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required in config.env")
        
        # Create download directory if it doesn't exist
        os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)
        
        return True
