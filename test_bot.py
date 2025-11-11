#!/usr/bin/env python3
"""
Simple tests for the Telegram Leech Bot
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from helpers import format_bytes, format_speed, format_time, is_url, is_magnet, is_torrent_file


def test_format_bytes():
    """Test byte formatting"""
    assert format_bytes(0) == "0.00 B"
    assert format_bytes(1024) == "1.00 KB"
    assert format_bytes(1024 * 1024) == "1.00 MB"
    assert format_bytes(1024 * 1024 * 1024) == "1.00 GB"
    print("✅ test_format_bytes passed")


def test_format_speed():
    """Test speed formatting"""
    assert format_speed(1024) == "1.00 KB/s"
    assert format_speed(1024 * 1024) == "1.00 MB/s"
    print("✅ test_format_speed passed")


def test_format_time():
    """Test time formatting"""
    assert format_time(30) == "30s"
    assert format_time(90) == "1m 30s"
    assert format_time(3661) == "1h 1m"
    print("✅ test_format_time passed")


def test_is_url():
    """Test URL detection"""
    assert is_url("http://example.com/file.mp4") == True
    assert is_url("https://example.com/file.mp4") == True
    assert is_url("magnet:?xt=urn:btih:123") == False
    assert is_url("not a url") == False
    print("✅ test_is_url passed")


def test_is_magnet():
    """Test magnet link detection"""
    assert is_magnet("magnet:?xt=urn:btih:123") == True
    assert is_magnet("http://example.com") == False
    print("✅ test_is_magnet passed")


def test_is_torrent_file():
    """Test torrent file detection"""
    assert is_torrent_file("file.torrent") == True
    assert is_torrent_file("file.mp4") == False
    print("✅ test_is_torrent_file passed")


def run_tests():
    """Run all tests"""
    print("Running tests...\n")
    
    try:
        test_format_bytes()
        test_format_speed()
        test_format_time()
        test_is_url()
        test_is_magnet()
        test_is_torrent_file()
        
        print("\n✅ All tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
