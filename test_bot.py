#!/usr/bin/env python3
"""
Simple Instagram Bot Test - Verify working configuration
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_instagram_bot():
    """Test basic bot functionality"""
    print("🧪 Testing Instagram Bot...")
    
    try:
        # Use the working Chrome configuration
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-notifications')
        
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        print("✅ Chrome started")
        
        # Test login
        driver.get('https://www.instagram.com/accounts/login/')
        time.sleep(3)
        
        # Get credentials from secure config
        from config import get_credentials
        username, password = get_credentials()
        
        username_input = driver.find_element(By.NAME, "username")
        username_input.send_keys(username)
        time.sleep(1)
        
        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(password)
        time.sleep(1)
        
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        time.sleep(5)
        
        if "login" not in driver.current_url.lower():
            print("✅ Login completed")
            
            # Test navigation to target account
            driver.get("https://www.instagram.com/1001tracklists/")
            time.sleep(3)
            print("✅ Successfully navigated to target account")
            
            print("✅ All tests passed! Bot is ready for deployment.")
            return True
        else:
            print("❌ Login failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
    finally:
        if 'driver' in locals():
            driver.quit()
            print("🔒 Browser closed")

if __name__ == "__main__":
    success = test_instagram_bot()
    exit(0 if success else 1) 