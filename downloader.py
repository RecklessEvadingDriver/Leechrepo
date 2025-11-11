import os
import time
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Callable
from tqdm import tqdm
from helpers import sanitize_filename

class DirectDownloader:
    """Handle direct URL downloads"""
    
    def __init__(self, download_dir: str):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    async def download(self, url: str, filename: Optional[str] = None, 
                      progress_callback: Optional[Callable] = None) -> str:
        """
        Download file from direct URL
        
        Args:
            url: Direct download URL
            filename: Optional custom filename
            progress_callback: Optional callback for progress updates
            
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
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(filepath, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size:
                            percentage = (downloaded / total_size) * 100
                            await progress_callback(downloaded, total_size, percentage)
        
        return str(filepath)


class TorrentDownloader:
    """Handle torrent and magnet link downloads using aria2"""
    
    def __init__(self, download_dir: str, aria2_host: str = 'localhost', 
                 aria2_port: int = 6800, aria2_secret: str = ''):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.aria2_host = aria2_host
        self.aria2_port = aria2_port
        self.aria2_secret = aria2_secret
        self.aria2 = None
        
    def connect(self):
        """Connect to aria2 RPC"""
        try:
            import aria2p
            self.aria2 = aria2p.API(
                aria2p.Client(
                    host=f"http://{self.aria2_host}",
                    port=self.aria2_port,
                    secret=self.aria2_secret
                )
            )
            # Test the connection
            self.aria2.client.get_version()
            return True
        except ImportError:
            raise ImportError(
                "aria2p library is not installed. "
                "Install it with: pip install aria2p"
            )
        except Exception as e:
            raise ConnectionError(
                f"Cannot connect to aria2 RPC at {self.aria2_host}:{self.aria2_port}. "
                f"Please ensure aria2c is running with RPC enabled. "
                f"Start it with: aria2c --enable-rpc --rpc-listen-port={self.aria2_port}\n"
                f"Error details: {str(e)}"
            )
    
    async def download_torrent(self, torrent_path: str, 
                               progress_callback: Optional[Callable] = None) -> str:
        """Download from torrent file"""
        if not self.aria2:
            self.connect()
        
        download = self.aria2.add_torrent(
            torrent_path,
            options={'dir': str(self.download_dir)}
        )
        
        return await self._monitor_download(download, progress_callback)
    
    async def download_magnet(self, magnet_uri: str,
                             progress_callback: Optional[Callable] = None) -> str:
        """Download from magnet link"""
        if not self.aria2:
            self.connect()
        
        download = self.aria2.add_magnet(
            magnet_uri,
            options={'dir': str(self.download_dir)}
        )
        
        return await self._monitor_download(download, progress_callback)
    
    async def _monitor_download(self, download, progress_callback: Optional[Callable] = None):
        """Monitor download progress"""
        while not download.is_complete:
            await asyncio.sleep(2)
            download.update()
            
            if progress_callback:
                total = download.total_length
                completed = download.completed_length
                percentage = (completed / total * 100) if total > 0 else 0
                speed = download.download_speed
                await progress_callback(completed, total, percentage, speed)
        
        # Get the downloaded file path
        if download.followed_by:
            download = download.followed_by[0]
            download.update()
        
        files = download.files
        if files:
            return files[0].path
        
        return str(self.download_dir / download.name)


class DownloadManager:
    """Unified download manager for all download types"""
    
    def __init__(self, download_dir: str, aria2_host: str = 'localhost',
                 aria2_port: int = 6800, aria2_secret: str = ''):
        self.direct_downloader = DirectDownloader(download_dir)
        self.torrent_downloader = TorrentDownloader(
            download_dir, aria2_host, aria2_port, aria2_secret
        )
        
    async def download(self, source: str, progress_callback: Optional[Callable] = None) -> str:
        """
        Universal download method
        
        Args:
            source: URL, magnet link, or torrent file path
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to downloaded file(s)
        """
        # Detect source type
        if source.startswith('magnet:'):
            return await self.torrent_downloader.download_magnet(source, progress_callback)
        elif source.endswith('.torrent') or os.path.exists(source):
            return await self.torrent_downloader.download_torrent(source, progress_callback)
        else:
            # Assume direct URL
            return await self.direct_downloader.download(source, progress_callback=progress_callback)
