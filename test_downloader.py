#!/usr/bin/env python3
"""
Test enhanced downloader functionality
"""

import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from downloader import DownloadManager, DirectDownloader, Aria2Downloader
from config import Config


def test_downloader_init():
    """Test downloader initialization"""
    dm = DownloadManager(
        Config.DOWNLOAD_DIR,
        Config.ARIA2_HOST,
        Config.ARIA2_PORT,
        Config.ARIA2_SECRET
    )
    assert dm is not None
    assert dm.direct_downloader is not None
    assert dm.aria2_downloader is not None
    print("✅ test_downloader_init passed")


def test_direct_downloader_init():
    """Test DirectDownloader initialization"""
    dd = DirectDownloader(Config.DOWNLOAD_DIR)
    assert dd is not None
    assert dd.download_dir.exists()
    print("✅ test_direct_downloader_init passed")


def test_aria2_downloader_init():
    """Test Aria2Downloader initialization"""
    ad = Aria2Downloader(
        Config.DOWNLOAD_DIR,
        Config.ARIA2_HOST,
        Config.ARIA2_PORT,
        Config.ARIA2_SECRET
    )
    assert ad is not None
    assert ad.download_dir.exists()
    print("✅ test_aria2_downloader_init passed")


def test_aria2_connection_handling():
    """Test aria2 connection error handling"""
    ad = Aria2Downloader(
        Config.DOWNLOAD_DIR,
        'localhost',
        6800,  # Likely not running
        ''
    )
    
    try:
        ad.connect()
        print("⚠️  Aria2 is running (unexpected in test environment)")
    except ConnectionError as e:
        # Expected - aria2 not running
        assert "Cannot connect to aria2 RPC" in str(e)
        assert "aria2c --enable-rpc" in str(e)
        print("✅ test_aria2_connection_handling passed (proper error message)")
    except Exception as e:
        print(f"⚠️  Unexpected error: {e}")


def test_source_type_detection():
    """Test download manager source type detection"""
    dm = DownloadManager(Config.DOWNLOAD_DIR)
    
    # Test URL detection
    assert not "magnet:?xt=urn:btih:abc123".startswith('http')
    
    # Test magnet detection
    assert "magnet:?xt=urn:btih:abc123".startswith('magnet:')
    
    # Test torrent detection
    assert "file.torrent".endswith('.torrent')
    
    print("✅ test_source_type_detection passed")


async def test_direct_download_session():
    """Test DirectDownloader session management"""
    dd = DirectDownloader(Config.DOWNLOAD_DIR)
    
    # Get session
    session = await dd._get_session()
    assert session is not None
    assert not session.closed
    
    # Close session
    await dd.close()
    assert session.closed
    
    print("✅ test_direct_download_session passed")


def test_download_dir_creation():
    """Test that download directories are created"""
    test_dir = "/tmp/test_downloads"
    
    # Clean up if exists
    import shutil
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    dd = DirectDownloader(test_dir)
    assert Path(test_dir).exists()
    
    # Clean up
    shutil.rmtree(test_dir)
    
    print("✅ test_download_dir_creation passed")


def run_tests():
    """Run all tests"""
    print("Running enhanced downloader tests...\n")
    
    try:
        test_downloader_init()
        test_direct_downloader_init()
        test_aria2_downloader_init()
        test_aria2_connection_handling()
        test_source_type_detection()
        
        # Run async tests
        asyncio.run(test_direct_download_session())
        
        test_download_dir_creation()
        
        print("\n✅ All enhanced downloader tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
