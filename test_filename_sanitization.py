#!/usr/bin/env python3
"""
Test filename sanitization functionality
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from helpers import sanitize_filename


def test_normal_filename():
    """Test normal filename remains unchanged"""
    assert sanitize_filename("video.mp4") == "video.mp4"
    assert sanitize_filename("document.pdf") == "document.pdf"
    print("✅ test_normal_filename passed")


def test_long_filename():
    """Test that long filenames are truncated"""
    # Create a filename longer than 255 characters
    long_name = "A" * 300 + ".mp4"
    result = sanitize_filename(long_name)
    
    # Result should be exactly 255 characters or less
    assert len(result) <= 255
    # Should preserve the extension
    assert result.endswith(".mp4")
    print(f"✅ test_long_filename passed (truncated {len(long_name)} to {len(result)})")


def test_invalid_characters():
    """Test that invalid characters are replaced"""
    filename = 'test<>:"/\\|?*file.mp4'
    result = sanitize_filename(filename)
    
    # Should not contain any invalid characters
    assert not any(c in result for c in '<>:"/\\|?*')
    # Should still have the extension
    assert result.endswith(".mp4")
    print("✅ test_invalid_characters passed")


def test_very_long_filename_with_extension():
    """Test very long filename preserves extension"""
    # This is similar to the error in the problem statement
    long_name = "ADGPM2kuMy28ExdHLWRhI59t17ig3UlmAx14wtRisttuXQ22QTJYInSPwg4mOwBZPGxfmWmhGJ1ckqJiOWvQ-cxFGaZfiBMRIgoQNvgks1wIxOLSOiZEUKkY3iIQxn2efmSwPmp5JbPSyxSrNzRKEOXcS91JONPjMwNx0CJdg1-obpfn4PE8apaKpOa8xko4EgmttID8rwpja6qDblODnklA9XhVx5snjUWbF4SPn_rkGxrJUQoCF-l6uotFzkp42IVkmB6lsPQD.mp4"
    result = sanitize_filename(long_name)
    
    assert len(result) <= 255
    assert result.endswith(".mp4")
    assert len(result.split('.')[-1]) == 3  # Extension should be 3 chars (mp4)
    print(f"✅ test_very_long_filename_with_extension passed (truncated {len(long_name)} to {len(result)})")


def test_filename_without_extension():
    """Test filename without extension"""
    long_name = "A" * 300
    result = sanitize_filename(long_name)
    
    assert len(result) <= 255
    print("✅ test_filename_without_extension passed")


def test_empty_filename():
    """Test empty filename gets a default"""
    result = sanitize_filename("")
    assert result == "download"
    print("✅ test_empty_filename passed")


def test_filename_with_spaces_and_dots():
    """Test filename with leading/trailing spaces and dots"""
    result = sanitize_filename("  .test.mp4.  ")
    assert not result.startswith(" ")
    assert not result.startswith(".")
    assert not result.endswith(" ")
    assert not result.endswith(".")
    print("✅ test_filename_with_spaces_and_dots passed")


def test_filename_with_multiple_extensions():
    """Test filename with multiple dots"""
    result = sanitize_filename("video.part1.rar.mp4")
    # Should preserve the last extension
    assert result.endswith(".mp4")
    assert len(result) <= 255
    print("✅ test_filename_with_multiple_extensions passed")


def test_special_url_characters():
    """Test filename extracted from URL with query parameters"""
    # Common case: URL query parameters should be removed before calling sanitize
    filename = "video.mp4?token=abc123&expires=999999"
    # In practice, the URL parsing should remove query params,
    # but sanitize_filename should handle it gracefully
    result = sanitize_filename(filename.split('?')[0])
    assert result == "video.mp4"
    print("✅ test_special_url_characters passed")


def test_custom_max_length():
    """Test custom max length parameter"""
    long_name = "A" * 100 + ".mp4"
    result = sanitize_filename(long_name, max_length=50)
    
    assert len(result) <= 50
    assert result.endswith(".mp4")
    print("✅ test_custom_max_length passed")


def run_tests():
    """Run all tests"""
    print("Running filename sanitization tests...\n")
    
    try:
        test_normal_filename()
        test_long_filename()
        test_invalid_characters()
        test_very_long_filename_with_extension()
        test_filename_without_extension()
        test_empty_filename()
        test_filename_with_spaces_and_dots()
        test_filename_with_multiple_extensions()
        test_special_url_characters()
        test_custom_max_length()
        
        print("\n✅ All filename sanitization tests passed!")
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
