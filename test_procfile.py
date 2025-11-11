#!/usr/bin/env python3
"""
Test Procfile configuration
"""

import subprocess
import sys


def test_procfile_exists():
    """Test that Procfile exists"""
    try:
        with open('Procfile', 'r') as f:
            content = f.read()
        assert content.strip() != "", "Procfile should not be empty"
        print("✅ Procfile exists and is not empty")
        return True
    except FileNotFoundError:
        print("❌ Procfile not found")
        return False


def test_procfile_web_command():
    """Test that Procfile has a web command"""
    try:
        with open('Procfile', 'r') as f:
            content = f.read()
        assert content.startswith('web:'), "Procfile should start with 'web:'"
        print("✅ Procfile has web command")
        return True
    except AssertionError as e:
        print(f"❌ {e}")
        return False


def test_procfile_includes_python():
    """Test that Procfile includes python3 bot.py"""
    try:
        with open('Procfile', 'r') as f:
            content = f.read()
        assert 'python3 bot.py' in content, "Procfile should include 'python3 bot.py'"
        print("✅ Procfile includes python3 bot.py")
        return True
    except AssertionError as e:
        print(f"❌ {e}")
        return False


def test_procfile_path_setup():
    """Test that Procfile sets up PATH for apt buildpack"""
    try:
        with open('Procfile', 'r') as f:
            content = f.read()
        assert '/app/.apt/usr/bin' in content, "Procfile should include apt buildpack PATH"
        print("✅ Procfile sets up apt buildpack PATH")
        return True
    except AssertionError as e:
        print(f"❌ {e}")
        return False


def test_procfile_aria2c_conditional():
    """Test that Procfile has conditional aria2c startup"""
    try:
        with open('Procfile', 'r') as f:
            content = f.read()
        # Check for conditional logic
        assert 'command -v aria2c' in content or 'if' in content, \
            "Procfile should check for aria2c availability"
        print("✅ Procfile has conditional aria2c startup")
        return True
    except AssertionError as e:
        print(f"❌ {e}")
        return False


def test_procfile_command_syntax():
    """Test that the Procfile command has valid bash syntax"""
    try:
        with open('Procfile', 'r') as f:
            content = f.read().strip()
        
        # Extract the command after 'web:'
        if content.startswith('web:'):
            command = content[4:].strip()
            
            # Test bash syntax by running bash -n (syntax check only)
            result = subprocess.run(
                ['bash', '-n', '-c', command],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Bash syntax error: {result.stderr}")
                return False
            
            print("✅ Procfile command has valid bash syntax")
            return True
        else:
            print("❌ Procfile doesn't start with 'web:'")
            return False
    except Exception as e:
        print(f"❌ Error checking bash syntax: {e}")
        return False


def run_tests():
    """Run all Procfile tests"""
    print("Testing Procfile configuration...\n")
    
    tests = [
        test_procfile_exists,
        test_procfile_web_command,
        test_procfile_includes_python,
        test_procfile_path_setup,
        test_procfile_aria2c_conditional,
        test_procfile_command_syntax,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print()
    if all(results):
        print("✅ All Procfile tests passed!")
        return 0
    else:
        print("❌ Some Procfile tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
