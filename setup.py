#!/usr/bin/env python3
"""
Instagram Automation Setup Script
Helps users configure the bot securely
"""
import os
import json
import shutil
import getpass

def setup_config():
    """Interactive setup for configuration"""
    print("🤖 Instagram Automation Setup")
    print("=" * 40)
    
    # Check if config already exists
    if os.path.exists('config.json'):
        overwrite = input("⚠️ config.json already exists. Overwrite? (y/N): ").lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return False
    
    print("\n📝 Please provide your Instagram credentials:")
    username = input("Instagram username: ").strip()
    
    if not username:
        print("❌ Username cannot be empty")
        return False
    
    password = getpass.getpass("Instagram password (hidden): ").strip()
    
    if not password:
        print("❌ Password cannot be empty")
        return False
    
    print("\n🎯 Target accounts configuration:")
    print("Current default accounts: 1001tracklists, housemusic.us, housemusicnerds, edm")
    use_defaults = input("Use default accounts? (Y/n): ").lower()
    
    if use_defaults == 'n':
        accounts_input = input("Enter target accounts (comma-separated): ").strip()
        target_accounts = [acc.strip() for acc in accounts_input.split(',') if acc.strip()]
    else:
        target_accounts = ["1001tracklists", "housemusic.us", "housemusicnerds", "edm"]
    
    print("\n⚙️ Automation settings:")
    users_per_account = input("Users to follow per account (default: 25): ").strip()
    users_per_account = int(users_per_account) if users_per_account.isdigit() else 25
    
    unfollow_delay = input("Unfollow delay in hours (default: 48): ").strip()
    unfollow_delay = int(unfollow_delay) if unfollow_delay.isdigit() else 48
    
    # Create config
    config = {
        "instagram": {
            "username": username,
            "password": password
        },
        "automation": {
            "target_accounts": target_accounts,
            "users_per_account": users_per_account,
            "total_daily_follows": users_per_account * len(target_accounts),
            "unfollow_delay_hours": unfollow_delay,
            "schedule_times": ["10:00", "18:00"]
        },
        "aws": {
            "instance_type": "t3.small",
            "region": "us-east-2"
        }
    }
    
    # Save config
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n✅ Configuration saved to config.json")
    print("🔒 This file is excluded from git for security")
    
    return True

def setup_env_file():
    """Create .env file as alternative to config.json"""
    print("\n🌍 Environment Variables Setup")
    print("=" * 40)
    
    if os.path.exists('.env'):
        overwrite = input("⚠️ .env already exists. Overwrite? (y/N): ").lower()
        if overwrite != 'y':
            return
    
    # Copy template
    if os.path.exists('.env.template'):
        shutil.copy('.env.template', '.env')
        print("✅ Created .env from template")
        print("📝 Please edit .env file and fill in your credentials")
    else:
        print("❌ .env.template not found")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    try:
        import selenium
        print("✅ Selenium installed")
    except ImportError:
        print("❌ Selenium not installed. Run: pip install selenium")
        return False
    
    try:
        import flask
        print("✅ Flask installed")
    except ImportError:
        print("❌ Flask not installed. Run: pip install flask")
        return False
    
    try:
        import schedule
        print("✅ Schedule installed")
    except ImportError:
        print("❌ Schedule not installed. Run: pip install schedule")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Instagram Automation System Setup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first:")
        print("pip install -r requirements.txt")
        return
    
    print("\n🔧 Choose configuration method:")
    print("1. Interactive setup (creates config.json)")
    print("2. Environment variables (creates .env)")
    print("3. Manual setup (copy templates)")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == '1':
        if setup_config():
            print("\n🎉 Setup complete! You can now run:")
            print("  python complete_instagram_bot.py")
            print("  python dashboard.py")
    elif choice == '2':
        setup_env_file()
        print("\n📝 Please edit .env file with your credentials")
    elif choice == '3':
        print("\n📋 Manual setup:")
        print("1. Copy config.template.json to config.json")
        print("2. Copy .env.template to .env")
        print("3. Fill in your credentials")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 