#!/usr/bin/env python3
"""
Cloud-Optimized Instagram Bot for Oracle Cloud Free Tier
Headless automation with virtual display support
"""
import os
import sys
import time
import json
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import subprocess

class CloudInstagramBot:
    def __init__(self, username, password, target_accounts, users_per_account=50):
        self.username = username
        self.password = password
        self.target_accounts = target_accounts
        self.users_per_account = users_per_account
        self.driver = None
        self.is_running = True
        
        # Cloud-specific settings
        self.headless = os.environ.get('HEADLESS', 'true').lower() == 'true'
        self.display = os.environ.get('DISPLAY', ':99')
        
        # Setup data directory
        self.data_dir = Path('instagram_data')
        self.data_dir.mkdir(exist_ok=True)
        (self.data_dir / 'logs').mkdir(exist_ok=True)
        (self.data_dir / 'csv_exports').mkdir(exist_ok=True)
        
        # Load tracking data
        self.attempted_follows = self.load_attempted_follows()
        
        # Optimized delays for cloud (faster, more efficient)
        self.follow_min_delay = 15  # Faster for cloud
        self.follow_max_delay = 45
        self.unfollow_min_delay = 5
        self.unfollow_max_delay = 15
        
    def setup_virtual_display(self):
        """Setup virtual display for headless operation"""
        if self.headless and 'DISPLAY' not in os.environ:
            try:
                # Start Xvfb virtual display
                subprocess.Popen([
                    'Xvfb', ':99', 
                    '-screen', '0', '1024x768x24',
                    '-ac', '+extension', 'GLX', '+render', '-noreset'
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                os.environ['DISPLAY'] = ':99'
                time.sleep(2)  # Wait for display to start
                return True
            except Exception as e:
                print(f"Warning: Could not start virtual display: {e}")
                return False
        return True
        
    def init_driver(self):
        """Initialize Chrome driver optimized for Oracle Cloud"""
        try:
            # Setup virtual display first
            self.setup_virtual_display()
            
            options = Options()
            
            # Basic stability options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Cloud-specific optimizations
            if self.headless:
                options.add_argument('--headless')
                options.add_argument('--virtual-time-budget=1000')
                
            # Performance optimizations for 1GB RAM
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            options.add_argument('--disable-javascript')
            options.add_argument('--disable-css')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-gpu')
            options.add_argument('--memory-pressure-off')
            options.add_argument('--max_old_space_size=512')
            
            # Window settings
            options.add_argument('--window-size=1024,768')
            options.add_argument('--disable-notifications')
            
            # User agent for cloud
            options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Try different ChromeDriver locations
            driver_paths = [
                '/usr/bin/chromedriver',
                '/usr/local/bin/chromedriver',
                'chromedriver'
            ]
            
            driver_path = None
            for path in driver_paths:
                if os.path.exists(path) or path == 'chromedriver':
                    driver_path = path
                    break
                    
            if driver_path and driver_path != 'chromedriver':
                from selenium.webdriver.chrome.service import Service
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
                
            self.driver.implicitly_wait(10)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True
            
        except Exception as e:
            print(f"Error initializing driver: {str(e)}")
            return False

    def login(self, log_signal):
        """Log in to Instagram with cloud-optimized error handling"""
        try:
            self.driver.get('https://www.instagram.com/')
            time.sleep(3)
            
            log_signal.emit("🔐 Logging in to Instagram...")

            # Handle cookies popup
            try:
                cookies_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Allow')]"))
                )
                cookies_button.click()
                time.sleep(1)
            except:
                pass  # No cookies popup

            # Find and fill username field
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'username'))
            )
            username_field.clear()
            username_field.send_keys(self.username)

            # Find and fill password field
            password_field = self.driver.find_element(By.NAME, 'password')
            password_field.clear()
            password_field.send_keys(self.password)

            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Handle "Save login info" popup
            try:
                not_now_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                )
                not_now_button.click()
                time.sleep(2)
            except:
                pass

            # Handle "Turn on notifications" popup
            try:
                not_now_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                )
                not_now_button.click()
                time.sleep(2)
            except:
                pass

            # Check if login was successful
            if "instagram.com" in self.driver.current_url and "login" not in self.driver.current_url:
                log_signal.emit("✅ Successfully logged in!")
                return True
            else:
                log_signal.emit("❌ Login failed - check credentials")
                return False

        except Exception as e:
            log_signal.emit(f"❌ Login error: {str(e)}")
            return False

    def load_attempted_follows(self):
        """Load the list of previously attempted follows from JSON file"""
        try:
            attempted_follows_path = self.data_dir / 'attempted_follows.json'
            if attempted_follows_path.exists():
                with open(attempted_follows_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading attempted follows: {str(e)}")
            return {}

    def save_attempted_follows(self):
        """Save the list of attempted follows to JSON file"""
        try:
            attempted_follows_path = self.data_dir / 'attempted_follows.json'
            with open(attempted_follows_path, 'w') as f:
                json.dump(self.attempted_follows, f, indent=2)
        except Exception as e:
            print(f"Error saving attempted follows: {str(e)}")

    def should_skip_user(self, username, log_signal):
        """Check if we should skip attempting to follow this user"""
        if username in self.attempted_follows:
            attempt = self.attempted_follows[username]
            if attempt['instagram_username'] == self.username:  # Only skip if same account
                status = attempt['status']
                timestamp = attempt['timestamp']
                log_signal.emit(f"⏭️ Skipping {username} - Previously attempted ({status})")
                return True
        return False

    def add_to_attempted_follows(self, username, status):
        """Add a username to the attempted follows list with status and timestamp"""
        self.attempted_follows[username] = {
            'status': status,  # 'success', 'failed', 'private', 'already_following'
            'timestamp': datetime.now().isoformat(),
            'instagram_username': self.username
        }
        self.save_attempted_follows()

    def get_followers(self, account, log_signal, max_scroll_attempts=15):
        """Get followers optimized for cloud (faster, lighter)"""
        followers = []
        unique_followers_needed = self.users_per_account
        
        try:
            # Navigate to account page
            self.driver.get(f'https://www.instagram.com/{account}/')
            time.sleep(2)

            # Click followers button
            followers_link = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='followers']"))
            )
            followers_link.click()
            time.sleep(2)

            # Get followers dialog
            followers_dialog = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog']"))
            )

            # Collect followers with reduced scrolling (cloud optimized)
            processed_usernames = set()
            scroll_attempts = 0

            while len(followers) < unique_followers_needed and scroll_attempts < max_scroll_attempts:
                # Get follower elements
                follower_elements = followers_dialog.find_elements(By.CSS_SELECTOR, "a[role='link']")
                
                # Extract usernames
                for element in follower_elements:
                    try:
                        username = element.text
                        if username and username not in processed_usernames:
                            processed_usernames.add(username)
                            if not self.should_skip_user(username, log_signal):
                                followers.append(username)
                                log_signal.emit(f"📋 Found: {username} ({len(followers)}/{unique_followers_needed})")
                                if len(followers) >= unique_followers_needed:
                                    break
                    except:
                        continue

                # Scroll more efficiently for cloud
                if len(followers) < unique_followers_needed:
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollTop + 500;",
                        followers_dialog
                    )
                    time.sleep(1)
                    scroll_attempts += 1

            log_signal.emit(f"✅ Collected {len(followers)} followers from {account}")
            return followers

        except Exception as e:
            log_signal.emit(f"❌ Error collecting followers from {account}: {str(e)}")
            return followers

    def follow_user(self, username, log_signal):
        """Follow user with cloud-optimized performance"""
        try:
            if self.should_skip_user(username, log_signal):
                return False

            # Navigate to user's profile
            self.driver.get(f'https://www.instagram.com/{username}/')
            time.sleep(1.5)  # Faster for cloud

            # Find follow button
            follow_button = WebDriverWait(self.driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='button']"))
            )

            button_text = follow_button.text.lower()
            
            if button_text in ['follow', 'follow back']:
                follow_button.click()
                time.sleep(1.5)
                
                # Quick verification
                try:
                    new_button = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='button']"))
                    )
                    new_text = new_button.text.lower()
                    
                    if new_text in ['following', 'requested']:
                        log_signal.emit(f"✅ Successfully followed {username}")
                        self.add_to_attempted_follows(username, 'success')
                        return True
                except:
                    pass
                    
                log_signal.emit(f"⚠️ Follow attempt for {username} - status unclear")
                self.add_to_attempted_follows(username, 'unknown')
                return True
                
            else:
                status = 'already_following' if 'following' in button_text else 'private'
                log_signal.emit(f"⏭️ Skipping {username} - {button_text}")
                self.add_to_attempted_follows(username, status)
                return False

        except Exception as e:
            log_signal.emit(f"❌ Error following {username}: {str(e)}")
            self.add_to_attempted_follows(username, 'failed')
            return False

    def unfollow_user(self, username, log_signal):
        """Unfollow user with cloud optimization"""
        try:
            log_signal.emit(f"🔄 Unfollowing {username}")
            
            self.driver.get(f'https://www.instagram.com/{username}/')
            time.sleep(1.5)

            # Find following button
            following_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Following')]"))
            )
            following_button.click()
            time.sleep(1)

            # Click unfollow in popup
            unfollow_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Unfollow')]"))
            )
            unfollow_button.click()
            time.sleep(1)

            log_signal.emit(f"✅ Successfully unfollowed {username}")
            return True

        except Exception as e:
            log_signal.emit(f"❌ Error unfollowing {username}: {str(e)}")
            return False

    def run_follow_job(self, log_signal):
        """Execute follow job optimized for cloud"""
        try:
            log_signal.emit("🚀 Starting cloud follow job...")
            
            if not self.init_driver():
                log_signal.emit("❌ Failed to initialize driver")
                return []
                
            if not self.login(log_signal):
                log_signal.emit("❌ Failed to login")
                return []

            successfully_followed = []
            total_follows_needed = self.users_per_account * len(self.target_accounts)

            for target_account in self.target_accounts:
                if not self.is_running or len(successfully_followed) >= total_follows_needed:
                    break

                log_signal.emit(f"📋 Processing followers of {target_account}")
                
                followers = self.get_followers(target_account, log_signal)

                for follower in followers:
                    if not self.is_running or len(successfully_followed) >= total_follows_needed:
                        break

                    if self.follow_user(follower, log_signal):
                        successfully_followed.append(follower)
                        
                        # Cloud-optimized delay
                        delay = random.uniform(self.follow_min_delay, self.follow_max_delay)
                        log_signal.emit(f"⏳ Delay: {delay:.1f}s ({len(successfully_followed)}/{total_follows_needed})")
                        time.sleep(delay)

            log_signal.emit(f"🎉 Follow job completed: {len(successfully_followed)} new follows")
            return successfully_followed

        except Exception as e:
            log_signal.emit(f"❌ Error in follow job: {e}")
            return successfully_followed if 'successfully_followed' in locals() else []
        finally:
            if self.driver:
                self.driver.quit()

    def run_unfollow_job(self, usernames_to_unfollow, log_signal):
        """Execute unfollow job optimized for cloud"""
        try:
            log_signal.emit("🔄 Starting cloud unfollow job...")
            
            if not self.init_driver():
                log_signal.emit("❌ Failed to initialize driver")
                return []
                
            if not self.login(log_signal):
                log_signal.emit("❌ Failed to login")
                return []

            successfully_unfollowed = []

            for username in usernames_to_unfollow:
                if not self.is_running:
                    break

                if self.unfollow_user(username, log_signal):
                    successfully_unfollowed.append(username)
                    
                    # Cloud-optimized delay
                    delay = random.uniform(self.unfollow_min_delay, self.unfollow_max_delay)
                    log_signal.emit(f"⏳ Delay: {delay:.1f}s")
                    time.sleep(delay)

            log_signal.emit(f"🎉 Unfollow job completed: {len(successfully_unfollowed)} accounts")
            return successfully_unfollowed

        except Exception as e:
            log_signal.emit(f"❌ Error in unfollow job: {e}")
            return successfully_unfollowed if 'successfully_unfollowed' in locals() else []
        finally:
            if self.driver:
                self.driver.quit()

    def export_followed_users(self, usernames, log_signal):
        """Export followed users to CSV"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_path = self.data_dir / 'csv_exports' / f'followed_users_batch_{timestamp}.csv'
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Username', 'Followed At', 'Status', 'Instagram Account'])
                for username in usernames:
                    attempt_data = self.attempted_follows.get(username, {})
                    status = attempt_data.get('status', 'unknown')
                    followed_at = attempt_data.get('timestamp', datetime.now().isoformat())
                    writer.writerow([username, followed_at, status, self.username])
            
            log_signal.emit(f"📊 Exported {len(usernames)} users to {csv_path}")
            return str(csv_path)
            
        except Exception as e:
            log_signal.emit(f"Error exporting: {str(e)}")
            return None

# Logger class for use with scheduler
class CloudLogger:
    def __init__(self, logger):
        self.logger = logger
        
    def emit(self, message):
        self.logger.info(message)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

if __name__ == "__main__":
    # Test the cloud bot
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Example usage
    bot = CloudInstagramBot(
        username="your_username",
        password="your_password", 
        target_accounts=["example_account"],
        users_per_account=5
    )
    
    cloud_logger = CloudLogger(logger)
    result = bot.run_follow_job(cloud_logger)
    print(f"Test completed: {len(result)} follows") 