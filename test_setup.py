#!/usr/bin/env python3
"""
Local Setup Verification Test
Checks if all dependencies and components are working for local operation
"""

import sys
import os
from pathlib import Path

def test_python_version():
    """Test Python version compatibility"""
    print("🐍 Testing Python Version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\n📦 Testing Dependencies...")
    dependencies = {
        'selenium': 'Selenium WebDriver',
        'tkinter': 'GUI Framework',
        'requests': 'HTTP Library',
        'json': 'JSON Support',
        'threading': 'Threading Support',
        'pathlib': 'Path Handling',
        'datetime': 'Date/Time Support',
        'random': 'Randomization',
        'logging': 'Logging Support'
    }
    
    passed = 0
    total = len(dependencies)
    
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {module:<12} - {description}")
            passed += 1
        except ImportError:
            print(f"❌ {module:<12} - {description} (MISSING)")
    
    # Test optional dependencies
    optional = {
        'webdriver_manager': 'Chrome Driver Manager',
        'PIL': 'Image Processing (Pillow)'
    }
    
    print("\n📦 Optional Dependencies...")
    for module, description in optional.items():
        try:
            __import__(module)
            print(f"✅ {module:<18} - {description}")
        except ImportError:
            print(f"⚠️  {module:<18} - {description} (Optional)")
    
    return passed == total

def test_chrome():
    """Test Chrome browser availability"""
    print("\n🌐 Testing Chrome Browser...")
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
    
    print("❌ Chrome not found. Please install Google Chrome.")
    print("   Download: https://www.google.com/chrome/")
    return False

def test_files():
    """Test required files exist"""
    print("\n📁 Testing Required Files...")
    required_files = [
        'instagram_gui.py',
        'launch_gui.py',
        'requirements.txt',
        'README.md',
        'ANTI_DETECTION_GUIDE.md'
    ]
    
    missing = []
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing.append(file)
    
    return len(missing) == 0

def test_directories():
    """Test and create required directories"""
    print("\n📂 Testing Directories...")
    directories = [
        'instagram_data',
        'logs',
        'bot_data'
    ]
    
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"✅ {directory}/ - Exists")
        else:
            try:
                path.mkdir(exist_ok=True)
                print(f"✅ {directory}/ - Created")
            except Exception as e:
                print(f"❌ {directory}/ - Failed to create: {e}")
                return False
    
    return True

def test_gui_import():
    """Test GUI module import"""
    print("\n🖥️  Testing GUI Import...")
    try:
        import instagram_gui
        print("✅ Instagram GUI module imports successfully")
        return True
    except ImportError as e:
        print(f"❌ GUI import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️  GUI import warning: {e}")
        return True

def main():
    """Run all tests"""
    print("🧪 Instagram Automation - Local Setup Test")
    print("=" * 50)
    
    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_dependencies), 
        ("Chrome Browser", test_chrome),
        ("Required Files", test_files),
        ("Directories", test_directories),
        ("GUI Import", test_gui_import)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ {test_name} - Error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Your setup is ready for local automation.")
        print("\n🚀 Next steps:")
        print("   1. Run: python launch_gui.py")
        print("   2. Configure your Instagram credentials")
        print("   3. Set your target accounts and preferences")
        print("   4. Click 'Test Connection' to verify")
        print("   5. Start automation!")
    else:
        print("⚠️  Some tests failed. Please fix the issues above before proceeding.")
        print("\n🔧 Common fixes:")
        print("   - Install missing dependencies: pip install -r requirements.txt")
        print("   - Install Chrome: https://www.google.com/chrome/")
        print("   - Check file permissions in the directory")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 