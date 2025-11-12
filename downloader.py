import os
import time
import asyncio
import aiohttp
import logging
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from tqdm import tqdm
from helpers import sanitize_filename

# Set up logging
logger = logging.getLogger(__name__)


class DirectDownloader:
    """Handle direct URL downloads with improved error handling"""
    
    def __init__(self, download_dir: str):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self._session = None
        
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=None, connect=60, sock_read=60)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
        
    async def close(self):
        """Close the session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def download(self, url: str, filename: Optional[str] = None, 
                      progress_callback: Optional[Callable] = None,
                      headers: Optional[Dict[str, str]] = None) -> str:
        """
        Download file from direct URL with retry logic
        
        Args:
            url: Direct download URL
            filename: Optional custom filename
            progress_callback: Optional callback for progress updates
            headers: Optional custom headers for the request
            
        Returns:
            Path to downloaded file
        """
        if not filename:
            # Extract filename from URL
            filename = url.split('/')[-1].split('?')[0]
            if not filename:
                filename = f"download_{int(time.time())}"
        
        # Sanitize filename to prevent filesystem errors
        filename = sanitize_filename(filename)
        
        filepath = self.download_dir / filename
        
        # Set default headers if not provided
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        
        session = await self._get_session()
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    chunk_size = 1024 * 1024  # 1MB chunks
                    
                    with open(filepath, 'wb') as f:
                        async for chunk in response.content.iter_chunked(chunk_size):
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if progress_callback and total_size:
                                percentage = (downloaded / total_size) * 100
                                speed = 0  # Can be calculated if needed
                                await progress_callback(downloaded, total_size, percentage, speed)
                
                logger.info(f"Successfully downloaded: {filename}")
                return str(filepath)
                
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"Failed to download {url} after {max_retries} retries: {e}")
                    raise Exception(f"Download failed after {max_retries} retries: {str(e)}")
                
                logger.warning(f"Download attempt {retry_count} failed, retrying... Error: {e}")
                await asyncio.sleep(2 * retry_count)  # Exponential backoff


class Aria2Downloader:
    """Handle downloads using aria2c with improved error handling and retry logic"""
    
    def __init__(self, download_dir: str, aria2_host: str = 'localhost', 
                 aria2_port: int = 6800, aria2_secret: str = ''):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.aria2_host = aria2_host
        self.aria2_port = aria2_port
        self.aria2_secret = aria2_secret
        self.aria2 = None
        self._connected = False
        
    def connect(self, max_retries=3, initial_wait=1):
        """Connect to aria2 RPC with retry logic and better error messages
        
        Args:
            max_retries: Maximum number of connection attempts (default: 3)
            initial_wait: Initial wait time in seconds before first retry (default: 1)
        """
        if self._connected and self.aria2:
            return True
            
        try:
            import aria2p
            
            retry_count = 0
            last_error = None
            
            while retry_count < max_retries:
                try:
                    # Create aria2p client
                    client = aria2p.Client(
                        host=f"http://{self.aria2_host}",
                        port=self.aria2_port,
                        secret=self.aria2_secret
                    )
                    
                    self.aria2 = aria2p.API(client)
                    
                    # Test the connection
                    self.aria2.client.get_version()
                    self._connected = True
                    logger.info(f"Successfully connected to aria2 RPC at {self.aria2_host}:{self.aria2_port}")
                    return True
                    
                except Exception as e:
                    last_error = e
                    retry_count += 1
                    
                    if retry_count < max_retries:
                        wait_time = initial_wait * (2 ** (retry_count - 1))  # Exponential backoff
                        logger.warning(
                            f"Failed to connect to aria2 RPC (attempt {retry_count}/{max_retries}). "
                            f"Retrying in {wait_time}s... Error: {str(e)}"
                        )
                        time.sleep(wait_time)
                    else:
                        # All retries exhausted
                        raise ConnectionError(
                            f"Cannot connect to aria2 RPC at {self.aria2_host}:{self.aria2_port} "
                            f"after {max_retries} attempts. "
                            f"Please ensure aria2c is running with RPC enabled.\n"
                            f"Start it with: aria2c --enable-rpc --rpc-listen-port={self.aria2_port}\n"
                            f"Error: {str(last_error)}"
                        )
                
        except ImportError:
            raise ImportError(
                "aria2p library is not installed. "
                "Install it with: pip install aria2p"
            )
    
    async def download_uri(self, uri: str, filename: Optional[str] = None,
                          progress_callback: Optional[Callable] = None,
                          options: Optional[Dict[str, Any]] = None) -> str:
        """
        Download from URI (direct URL, magnet, or torrent) using aria2
        
        Args:
            uri: URI to download (URL, magnet link, or torrent file path)
            filename: Optional output filename
            progress_callback: Optional callback for progress updates
            options: Optional aria2 options
            
        Returns:
            Path to downloaded file(s)
        """
        if not self.aria2:
            self.connect()
        
        # Prepare aria2 options
        a2c_opt = options or {}
        a2c_opt['dir'] = str(self.download_dir)
        
        if filename:
            # Sanitize the filename
            filename = sanitize_filename(filename)
            a2c_opt['out'] = filename
        
        # Disable following torrents/metalinks in URI mode
        a2c_opt['follow-torrent'] = 'false'
        a2c_opt['follow-metalink'] = 'false'
        
        try:
            # Add download based on URI type
            if uri.startswith('magnet:'):
                download = self.aria2.add_magnet(uri, options=a2c_opt)
                logger.info(f"Added magnet download: {download.gid}")
            elif uri.endswith('.torrent') or os.path.exists(uri):
                download = self.aria2.add_torrent(uri, options=a2c_opt)
                logger.info(f"Added torrent download: {download.gid}")
            else:
                # Direct URL
                download = self.aria2.add_uris([uri], options=a2c_opt)
                logger.info(f"Added URI download: {download.gid}")
            
            return await self._monitor_download(download, progress_callback)
            
        except Exception as e:
            logger.error(f"Failed to add download: {e}")
            raise Exception(f"Failed to start aria2 download: {str(e)}")
    
    async def download_torrent(self, torrent_path: str, 
                               progress_callback: Optional[Callable] = None) -> str:
        """Download from torrent file"""
        if not self.aria2:
            self.connect()
        
        options = {'dir': str(self.download_dir)}
        download = self.aria2.add_torrent(torrent_path, options=options)
        logger.info(f"Added torrent download: {download.gid}")
        
        return await self._monitor_download(download, progress_callback)
    
    async def download_magnet(self, magnet_uri: str,
                             progress_callback: Optional[Callable] = None) -> str:
        """Download from magnet link"""
        if not self.aria2:
            self.connect()
        
        options = {'dir': str(self.download_dir)}
        download = self.aria2.add_magnet(magnet_uri, options=options)
        logger.info(f"Added magnet download: {download.gid}")
        
        return await self._monitor_download(download, progress_callback)
    
    async def _monitor_download(self, download, progress_callback: Optional[Callable] = None):
        """Monitor download progress with error handling"""
        try:
            while not download.is_complete:
                await asyncio.sleep(2)
                download.update()
                
                # Check for errors
                if download.error_message:
                    error_msg = str(download.error_message).replace("<", " ").replace(">", " ")
                    logger.error(f"Aria2 download error: {error_msg}")
                    raise Exception(f"Download error: {error_msg}")
                
                # Progress callback
                if progress_callback:
                    total = download.total_length
                    completed = download.completed_length
                    percentage = (completed / total * 100) if total > 0 else 0
                    speed = download.download_speed
                    await progress_callback(completed, total, percentage, speed)
            
            # Download complete, get the file path
            download.update()
            
            # Handle followed downloads (for torrents)
            if download.followed_by:
                download = download.followed_by[0]
                download.update()
            
            files = download.files
            if files:
                # Return the first file path (or directory for multi-file torrents)
                first_file_path = Path(files[0].path)
                if len(files) > 1:
                    # Multi-file download, return the parent directory
                    return str(first_file_path.parent)
                return str(first_file_path)
            
            # Fallback to download name
            result_path = self.download_dir / download.name
            return str(result_path)
            
        except Exception as e:
            logger.error(f"Download monitoring error: {e}")
            raise


# Backward compatibility alias
TorrentDownloader = Aria2Downloader


class DownloadManager:
    """Unified download manager for all download types with WZML-X inspired logic"""
    
    def __init__(self, download_dir: str, aria2_host: str = 'localhost',
                 aria2_port: int = 6800, aria2_secret: str = ''):
        self.download_dir = download_dir
        self.direct_downloader = DirectDownloader(download_dir)
        self.aria2_downloader = Aria2Downloader(
            download_dir, aria2_host, aria2_port, aria2_secret
        )
        self._aria2_available = None
        
    def _is_aria2_available(self) -> bool:
        """Check if aria2 is available"""
        if self._aria2_available is not None:
            return self._aria2_available
            
        try:
            self.aria2_downloader.connect()
            self._aria2_available = True
            return True
        except (ImportError, ConnectionError) as e:
            logger.warning(f"aria2 not available: {e}")
            self._aria2_available = False
            return False
    
    async def download(self, source: str, filename: Optional[str] = None,
                      progress_callback: Optional[Callable] = None,
                      use_aria2: bool = True) -> str:
        """
        Universal download method with automatic fallback
        
        Args:
            source: URL, magnet link, or torrent file path
            filename: Optional custom filename
            progress_callback: Optional callback for progress updates
            use_aria2: Whether to prefer aria2 for downloads (default True)
            
        Returns:
            Path to downloaded file(s)
        """
        # Detect source type
        is_magnet = source.startswith('magnet:')
        is_torrent = source.endswith('.torrent') or (os.path.exists(source) and source.endswith('.torrent'))
        
        # Torrents and magnets REQUIRE aria2
        if is_magnet or is_torrent:
            if not self._is_aria2_available():
                raise ConnectionError(
                    "Torrent/Magnet downloads require aria2. "
                    "Please ensure aria2c is running with RPC enabled.\n"
                    f"Start it with: aria2c --enable-rpc --rpc-listen-port={self.aria2_downloader.aria2_port}"
                )
            
            if is_magnet:
                return await self.aria2_downloader.download_magnet(source, progress_callback)
            else:
                return await self.aria2_downloader.download_torrent(source, progress_callback)
        
        # Direct URLs - try aria2 first if available and requested, fallback to direct
        if use_aria2 and self._is_aria2_available():
            try:
                logger.info(f"Attempting download with aria2: {source}")
                return await self.aria2_downloader.download_uri(
                    source, filename, progress_callback
                )
            except Exception as e:
                logger.warning(f"aria2 download failed, falling back to direct download: {e}")
                # Fall through to direct download
        
        # Direct download
        logger.info(f"Using direct download: {source}")
        return await self.direct_downloader.download(source, filename, progress_callback)
    
    async def close(self):
        """Clean up resources"""
        await self.direct_downloader.close()
