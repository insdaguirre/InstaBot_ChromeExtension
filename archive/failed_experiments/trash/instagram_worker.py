import time
import random
import os
from PyQt5.QtCore import QThread, pyqtSignal
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import logging

logger = logging.getLogger(__name__)

def setup_driver():
    try:
        logger.debug("Setting up Chrome options...")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--start-maximized')
        
        logger.debug("Setting up ChromeDriver using webdriver-manager...")
        driver_path = ChromeDriverManager().install()
        
        # Fix the path to point to the actual chromedriver executable
        if 'chromedriver-mac-x64' in driver_path:
            driver_path = os.path.join(os.path.dirname(driver_path), 'chromedriver')
        
        # Set proper permissions for the ChromeDriver executable
        logger.debug(f"Setting permissions for ChromeDriver at: {driver_path}")
        os.chmod(driver_path, 0o755)  # rwxr-xr-x permissions
        
        # Remove quarantine attribute if it exists
        try:
            os.system(f'xattr -d com.apple.quarantine "{driver_path}"')
        except:
            pass
            
        logger.debug(f"Using ChromeDriver at: {driver_path}")
        service = Service(driver_path)
        
        logger.debug("Creating Chrome WebDriver instance...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set window size
        driver.set_window_size(1920, 1080)
        
        logger.debug("Chrome WebDriver created successfully")
        return driver
    except Exception as e:
        logger.error(f"Error setting up Chrome driver: {str(e)}")
        if "unexpectedly exited" in str(e):
            logger.error("This might be due to macOS security settings. Please try:")
            logger.error("1. Open System Preferences > Security & Privacy")
            logger.error("2. Click 'Open Anyway' for ChromeDriver")
            logger.error("3. Run the script again")
        raise

class InstagramWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, username, password, accounts, action_type, min_delay, max_delay, max_per_hour, max_per_day):
        super().__init__()
        self.username = username
        self.password = password
        self.accounts = accounts
        self.action_type = action_type  # 'follow' or 'unfollow'
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_per_hour = max_per_hour
        self.max_per_day = max_per_day
        self.is_running = True

    def run(self):
        try:
            driver = setup_driver()
            
            # Login
            self.progress.emit("Logging in...")
            driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(5)
            
            try:
                driver.find_element(By.NAME, 'username').send_keys(self.username)
                driver.find_element(By.NAME, 'password').send_keys(self.password + Keys.RETURN)
                time.sleep(5)
                
                # Check for login errors
                error_messages = driver.find_elements(By.CLASS_NAME, 'error-container')
                if error_messages:
                    error_text = error_messages[0].text
                    self.progress.emit(f"❌ Login Error: {error_text}")
                    raise Exception(f"Login failed: {error_text}")
            except Exception as e:
                self.progress.emit(f"❌ Login Error: {str(e)}")
                raise
            
            actions_today = 0
            actions_this_hour = 0
            hour_start_time = time.time()
            
            for user in self.accounts:
                if not self.is_running:
                    break
                    
                current_time = time.time()
                
                # Reset hourly counter
                if current_time - hour_start_time > 3600:
                    actions_this_hour = 0
                    hour_start_time = current_time
                
                # Check limits
                if actions_today >= self.max_per_day:
                    self.progress.emit("Daily limit reached. Stopping.")
                    break
                if actions_this_hour >= self.max_per_hour:
                    wait = 3600 - (current_time - hour_start_time)
                    self.progress.emit(f"Hourly limit reached. Waiting {int(wait)} seconds.")
                    time.sleep(wait)
                    actions_this_hour = 0
                    hour_start_time = time.time()
                
                try:
                    # Visit profile
                    driver.get(f"https://www.instagram.com/{user}/")
                    time.sleep(random.uniform(4, 6))
                    
                    # Check if account exists
                    if "Sorry, this page isn't available." in driver.page_source:
                        self.progress.emit(f"❌ Error: Account {user} does not exist or is private")
                        continue
                    
                    # Check for rate limiting
                    if "Please wait a few minutes before you try again" in driver.page_source:
                        self.progress.emit("⚠️ Rate limit detected. Waiting 15 minutes...")
                        time.sleep(900)  # Wait 15 minutes
                        continue
                    
                    if self.action_type == 'follow':
                        try:
                            button = driver.find_element(By.XPATH, "//button[text()='Follow']")
                            action_text = "Followed"
                        except:
                            self.progress.emit(f"⚠️ Could not find Follow button for {user} (maybe already following)")
                            continue
                    else:
                        try:
                            button = driver.find_element(By.XPATH, "//button[text()='Following']")
                            button.click()
                            time.sleep(random.uniform(2, 3))
                            button = driver.find_element(By.XPATH, "//button[text()='Unfollow']")
                            action_text = "Unfollowed"
                        except:
                            self.progress.emit(f"⚠️ Could not find Following button for {user} (maybe not following)")
                            continue
                    
                    button.click()
                    self.progress.emit(f"✅ {action_text} {user}")
                    actions_today += 1
                    actions_this_hour += 1
                    
                except Exception as e:
                    self.progress.emit(f"❌ Error processing {user}: {str(e)}")
                    continue
                
                delay = random.uniform(self.min_delay, self.max_delay)
                self.progress.emit(f"⏳ Waiting {int(delay)} seconds before next attempt...")
                time.sleep(delay)
            
            driver.quit()
            self.finished.emit()
            
        except Exception as e:
            self.progress.emit(f"❌ Error: {str(e)}")
            self.finished.emit() 