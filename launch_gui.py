#!/usr/bin/env python3
"""
Instagram Automation GUI Launcher - Local Version
Simple launcher for local Instagram automation
"""

import sys
import os
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'selenium',
        'tkinter'
    ]
    
    missing_packages = []
    
    # Check selenium
    try:
        import selenium
        print("✅ Selenium installed")
    except ImportError:
        missing_packages.append('selenium')
        print("❌ Selenium not found")
    
    # Check tkinter
    try:
        import tkinter
        print("✅ Tkinter available")
    except ImportError:
        missing_packages.append('python-tk')
        print("❌ Tkinter not found")
    
    # Check webdriver-manager (optional)
    try:
        import webdriver_manager
        print("✅ Webdriver-manager available")
    except ImportError:
        print("⚠️  Webdriver-manager not found (optional but recommended)")
        print("    Install with: pip install webdriver-manager")
    
    return missing_packages

def install_missing_packages(packages):
    """Install missing packages"""
    if not packages:
        return True
    
    print(f"\n📦 Installing missing packages: {', '.join(packages)}")
    
    try:
        for package in packages:
            if package == 'python-tk':
                print("⚠️  Please install tkinter manually:")
                print("   - Ubuntu/Debian: sudo apt-get install python3-tk")
                print("   - macOS: brew install python-tk")
                print("   - Windows: Usually included with Python")
                continue
                
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def setup_directories():
    """Create necessary directories for local operation"""
    directories = [
        'instagram_data',
        'logs', 
        'bot_data'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Directory ready: {directory}")

def check_chrome():
    """Check if Chrome is installed"""
    chrome_paths = [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS
        '/usr/bin/google-chrome',  # Linux
        'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',  # Windows
        'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'  # Windows 32-bit
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print("✅ Google Chrome found")
            return True
    
    print("⚠️  Google Chrome not found. Please install Google Chrome.")
    print("   Download from: https://www.google.com/chrome/")
    return False

def main():
    """Main launcher function"""
    print("🚀 Instagram Automation GUI Launcher")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('instagram_gui.py').exists():
        print("❌ instagram_gui.py not found!")
        print("   Please run this script from the Instagram automation directory")
        sys.exit(1)
    
    # Setup directories
    print("\n📁 Setting up directories...")
    setup_directories()
    
    # Check Chrome installation
    print("\n🌐 Checking Chrome installation...")
    if not check_chrome():
        print("⚠️  Chrome is required for automation")
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        response = input(f"\n❓ Install missing packages? (y/n): ")
        if response.lower() in ['y', 'yes']:
            if not install_missing_packages(missing):
                print("❌ Failed to install dependencies. Please install manually:")
                print(f"   pip install {' '.join(missing)}")
                sys.exit(1)
        else:
            print("⚠️  Some features may not work without required packages")
    
    # Launch GUI
    print("\n🎯 Launching Instagram Automation GUI...")
    try:
        from instagram_gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"❌ Failed to import GUI: {e}")
        print("   Please install missing dependencies")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 