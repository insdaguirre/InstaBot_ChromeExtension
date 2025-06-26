#!/usr/bin/env python3
"""
Complete Instagram Automation Bot - AWS Compatible
Based on successful working test configuration
"""
import os
import time
import json
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

class InstagramBot:
    def __init__(self, username, password, target_accounts, users_per_account=25):
        self.username = username
        self.password = password
        self.target_accounts = target_accounts
        self.users_per_account = users_per_account
        self.driver = None
        
        # Setup directories
        self.data_dir = Path('instagram_data')
        self.data_dir.mkdir(exist_ok=True)
        
        # Files for tracking
        self.follows_file = self.data_dir / 'follows.json'
        self.action_log_file = self.data_dir / 'action_log.json'
        
        # Timing settings
        self.follow_delay_min = 20
        self.follow_delay_max = 40
        self.page_load_delay = 3
        
        # Initialize data files
        self.follows_data = self.load_follows_data()
        self.action_log = self.load_action_log()
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_follows_data(self):
        """Load follows data from file"""
        if self.follows_file.exists():
            try:
                with open(self.follows_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
        
    def save_follows_data(self):
        """Save follows data to file"""
        with open(self.follows_file, 'w') as f:
            json.dump(self.follows_data, f, indent=2)
            
    def load_action_log(self):
        """Load action log from file"""
        if self.action_log_file.exists():
            try:
                with open(self.action_log_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
        
    def save_action_log(self):
        """Save action log to file"""
        with open(self.action_log_file, 'w') as f:
            json.dump(self.action_log, f, indent=2)
            
    def log_action(self, action_type, target_user, details=""):
        """Log an action"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action_type,
            "target": target_user,
            "details": details
        }
        self.action_log.append(log_entry)
        self.save_action_log()
        
    def init_driver(self):
        """Initialize Chrome driver with working configuration"""
        try:
            options = Options()
            
            # Working configuration from successful test
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--remote-debugging-port=9222')
            
            # Additional stability options
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-notifications')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(10)
            
            self.logger.info("✅ Chrome started")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing driver: {str(e)}")
            return False

    def login(self):
        """Login to Instagram"""
        try:
            self.logger.info("🔑 Attempting to log in...")
            self.driver.get('https://www.instagram.com/accounts/login/')
            time.sleep(self.page_load_delay)

            # Enter username
            username_input = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.clear()
            username_input.send_keys(self.username)
            time.sleep(1)

            # Enter password
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.clear()
            password_input.send_keys(self.password)
            time.sleep(1)

            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            time.sleep(5)
            
            # Check if login was successful
            if "login" not in self.driver.current_url.lower():
                self.logger.info("✅ Login completed")
                return True
            else:
                self.logger.error("❌ Login failed - still on login page")
                return False

        except Exception as e:
            self.logger.error(f"❌ Login failed: {str(e)}")
            return False

    def navigate_to_account(self, account):
        """Navigate to a specific Instagram account"""
        try:
            url = f"https://www.instagram.com/{account}/"
            self.driver.get(url)
            time.sleep(self.page_load_delay)
            
            # Check if account exists
            if "Page Not Found" in self.driver.page_source or "Sorry, this page isn't available" in self.driver.page_source:
                self.logger.warning(f"⚠️ Account {account} not found")
                return False
                
            self.logger.info(f"✅ Navigated to {account}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error navigating to {account}: {str(e)}")
            return False

    def get_followers(self, account, max_followers=None):
        """Get followers from an account"""
        followers = []
        try:
            if max_followers is None:
                max_followers = self.users_per_account
                
            # Click followers link
            followers_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/followers/')]"))
            )
            followers_link.click()
            time.sleep(3)
            
            # Wait for followers dialog to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
            )
            
            # Scroll and collect followers
            collected = 0
            scroll_attempts = 0
            max_scroll_attempts = 10
            
            while collected < max_followers and scroll_attempts < max_scroll_attempts:
                # Get follower elements
                follower_elements = self.driver.find_elements(
                    By.XPATH, "//div[@role='dialog']//a[contains(@href, '/')]"
                )
                
                for element in follower_elements[collected:]:
                    try:
                        username = element.get_attribute('href').split('/')[-2]
                        if username and username not in followers and username != self.username:
                            followers.append(username)
                            collected += 1
                            if collected >= max_followers:
                                break
                    except:
                        continue
                
                # Scroll down in the dialog
                if collected < max_followers:
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollHeight",
                        self.driver.find_element(By.XPATH, "//div[@role='dialog']//div[contains(@style, 'overflow')]")
                    )
                    time.sleep(2)
                    scroll_attempts += 1
            
            self.logger.info(f"📋 Collected {len(followers)} followers from {account}")
            return followers
            
        except Exception as e:
            self.logger.error(f"❌ Error getting followers from {account}: {str(e)}")
            return []

    def follow_user(self, username):
        """Follow a specific user"""
        try:
            # Navigate to user profile
            self.driver.get(f"https://www.instagram.com/{username}/")
            time.sleep(self.page_load_delay)
            
            # Check if already following
            follow_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Follow')]")
            if not follow_buttons:
                # Already following or private account
                return False
            
            # Click follow button
            follow_button = follow_buttons[0]
            follow_button.click()
            time.sleep(2)
            
            # Record the follow
            follow_time = datetime.now().isoformat()
            self.follows_data[username] = {
                'followed_at': follow_time,
                'status': 'following'
            }
            self.save_follows_data()
            
            self.log_action('follow', username, f"Followed user successfully")
            self.logger.info(f"✅ Followed {username}")
            
            # Random delay between follows
            delay = random.randint(self.follow_delay_min, self.follow_delay_max)
            self.logger.info(f"⏳ Waiting {delay} seconds before next action...")
            time.sleep(delay)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error following {username}: {str(e)}")
            return False

    def unfollow_old_users(self, hours_threshold=48):
        """Unfollow users followed more than X hours ago"""
        try:
            unfollowed_count = 0
            current_time = datetime.now()
            
            for username, data in list(self.follows_data.items()):
                if data['status'] != 'following':
                    continue
                    
                followed_time = datetime.fromisoformat(data['followed_at'])
                hours_passed = (current_time - followed_time).total_seconds() / 3600
                
                if hours_passed >= hours_threshold:
                    if self.unfollow_user(username):
                        unfollowed_count += 1
                        
            self.logger.info(f"🔄 Unfollowed {unfollowed_count} users")
            return unfollowed_count
            
        except Exception as e:
            self.logger.error(f"❌ Error in unfollow process: {str(e)}")
            return 0

    def unfollow_user(self, username):
        """Unfollow a specific user"""
        try:
            self.driver.get(f"https://www.instagram.com/{username}/")
            time.sleep(self.page_load_delay)
            
            # Look for Following button
            following_buttons = self.driver.find_elements(
                By.XPATH, "//button[contains(text(), 'Following') or contains(@aria-label, 'Following')]"
            )
            
            if following_buttons:
                following_buttons[0].click()
                time.sleep(1)
                
                # Confirm unfollow
                unfollow_confirm = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Unfollow')]")
                if unfollow_confirm:
                    unfollow_confirm[0].click()
                    time.sleep(2)
                    
                    # Update status
                    if username in self.follows_data:
                        self.follows_data[username]['status'] = 'unfollowed'
                        self.follows_data[username]['unfollowed_at'] = datetime.now().isoformat()
                        self.save_follows_data()
                    
                    self.log_action('unfollow', username, "Unfollowed user")
                    self.logger.info(f"↩️ Unfollowed {username}")
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error unfollowing {username}: {str(e)}")
            return False

    def run_automation_cycle(self):
        """Run one complete automation cycle"""
        try:
            self.logger.info("🚀 Starting automation cycle...")
            
            # Initialize driver and login
            if not self.init_driver():
                return False
                
            if not self.login():
                return False
            
            # Unfollow old users first
            self.unfollow_old_users()
            
            # Follow new users from target accounts
            total_follows = 0
            for account in self.target_accounts:
                if self.navigate_to_account(account):
                    followers = self.get_followers(account)
                    
                    followed_this_account = 0
                    for follower in followers:
                        if follower not in self.follows_data or self.follows_data[follower]['status'] != 'following':
                            if self.follow_user(follower):
                                followed_this_account += 1
                                total_follows += 1
                                
                                if followed_this_account >= self.users_per_account:
                                    break
                    
                    self.logger.info(f"📊 Followed {followed_this_account} users from {account}")
            
            self.logger.info(f"✅ Automation cycle completed. Total new follows: {total_follows}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error in automation cycle: {str(e)}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("🔒 Browser closed")

    def get_stats(self):
        """Get automation statistics"""
        stats = {
            'total_follows': len([u for u, d in self.follows_data.items() if d['status'] == 'following']),
            'total_unfollows': len([u for u, d in self.follows_data.items() if d['status'] == 'unfollowed']),
            'recent_actions': len([a for a in self.action_log if 
                datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(days=1)])
        }
        return stats

def main():
    """Main function"""
    # Configuration
    USERNAME = "deegz.mp3"
    PASSWORD = "b@seb@ll"  # Replace with your actual password
    TARGET_ACCOUNTS = ["1001tracklists", "housemusic.us", "housemusicnerds", "edm"]
    USERS_PER_ACCOUNT = 25
    
    # Create bot instance
    bot = InstagramBot(USERNAME, PASSWORD, TARGET_ACCOUNTS, USERS_PER_ACCOUNT)
    
    # Run automation cycle
    success = bot.run_automation_cycle()
    
    if success:
        stats = bot.get_stats()
        print(f"📊 Current stats: {stats}")
    
    return success

if __name__ == "__main__":
    main() 