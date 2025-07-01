#!/usr/bin/env python3
"""
Instagram Automation - Local Installation Script
Automatically sets up the environment for local operation
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("🔧 Installing Python Dependencies...")
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install main dependencies
    dependencies = [
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.0", 
        "requests>=2.31.0",
        "Pillow>=10.0.0"
    ]
    
    for dep in dependencies:
        if not run_command(f"{sys.executable} -m pip install '{dep}'", f"Installing {dep.split('>=')[0]}"):
            return False
    
    return True

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    directories = [
        'instagram_data',
        'logs',
        'bot_data'
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            print(f"✅ Created directory: {directory}/")
        except Exception as e:
            print(f"❌ Failed to create {directory}/: {e}")
            return False
    
    return True

def check_chrome():
    """Check if Chrome is installed"""
    print("\n🌐 Checking for Google Chrome...")
    chrome_paths = [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS
        '/usr/bin/google-chrome',  # Linux
        '/usr/bin/chromium-browser',  # Linux (Chromium)
        'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',  # Windows
        'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'  # Windows 32-bit
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Chrome found: {path}")
            return True
    
    print("⚠️  Google Chrome not found")
    print("   Please download and install from: https://www.google.com/chrome/")
    return False

def create_example_settings():
    """Create example settings file"""
    print("\n⚙️  Creating example settings...")
    
    example_settings = {
        "username": "",
        "password": "",
        "target_accounts": "deadmau5,skrillex,1001tracklists,housemusic.us",
        "accounts_per_day_min": 2,
        "accounts_per_day_max": 3,
        "users_per_account_min": 3,
        "users_per_account_max": 6,
        "daily_follow_limit": 20,
        "follow_time_start": "09:00",
        "follow_time_end": "11:00",
        "unfollow_time_start": "15:00",
        "unfollow_time_end": "17:00",
        "unfollow_hours_min": 48,
        "unfollow_hours_max": 72,
        "vary_schedule": True,
        "random_account_order": True,
        "skip_days": False,
        "skip_chance": 0.1,
        "use_proxy": False,
        "http_proxy": "",
        "proxy_username": "",
        "proxy_password": "",
        "enhanced_stealth": True,
        "show_browser": False
    }
    
    try:
        import json
        with open('example_settings.json', 'w') as f:
            json.dump(example_settings, f, indent=2)
        print("✅ Created example_settings.json")
        return True
    except Exception as e:
        print(f"⚠️  Could not create example settings: {e}")
        return False

def test_installation():
    """Test if installation was successful"""
    print("\n🧪 Testing installation...")
    
    try:
        import selenium
        print("✅ Selenium imported successfully")
    except ImportError:
        print("❌ Selenium import failed")
        return False
    
    try:
        import tkinter
        print("✅ Tkinter available")
    except ImportError:
        print("❌ Tkinter not available")
        return False
    
    try:
        from instagram_gui import main
        print("✅ Instagram GUI module ready")
        return True
    except ImportError as e:
        print(f"❌ GUI import failed: {e}")
        return False

def main():
    """Main installation function"""
    print("🚀 Instagram Automation - Local Installation")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Please upgrade Python.")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Run installation steps
    steps = [
        ("Install Dependencies", install_dependencies),
        ("Setup Directories", setup_directories),
        ("Check Chrome", check_chrome),
        ("Create Example Settings", create_example_settings),
        ("Test Installation", test_installation)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        if not step_func():
            failed_steps.append(step_name)
    
    print("\n" + "=" * 50)
    
    if not failed_steps:
        print("🎉 Installation completed successfully!")
        print("\n🚀 Ready to start:")
        print("   python launch_gui.py")
        print("\n📋 Quick setup:")
        print("   1. Enter your Instagram username/password")
        print("   2. Configure target accounts")  
        print("   3. Set randomization preferences")
        print("   4. Click 'Test Connection'")
        print("   5. Start automation!")
        print("\n📖 Documentation:")
        print("   - README.md - Complete usage guide")
        print("   - ANTI_DETECTION_GUIDE.md - Advanced features")
        print("   - example_settings.json - Sample configuration")
    else:
        print(f"⚠️  Installation completed with {len(failed_steps)} warnings:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\n🔧 Manual fixes may be needed:")
        print("   - Install Google Chrome if missing")
        print("   - Check Python version (3.8+ required)")
        print("   - Verify internet connection for downloads")

if __name__ == "__main__":
    main() 