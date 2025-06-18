from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import platform
import time
import random
import json
import os
from datetime import datetime, timedelta
import threading
import subprocess
from selenium.webdriver.common.keys import Keys
import csv
from pathlib import Path
from selenium.webdriver.common.action_chains import ActionChains
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt5.QtCore import QUrl

class InstagramBot:
    def __init__(self, username, password, target_accounts, users_per_account=50,
                 min_delay=30, max_delay=60, unfollow_delay=0):
        self.username = username
        self.password = password
        self.target_accounts = target_accounts
        self.users_per_account = users_per_account
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.unfollow_delay = unfollow_delay
        self.is_running = False
        self.driver = None
        self.followed_users = []
        self.attempted_follows = self.load_attempted_follows()
        self.data_dir = self.setup_data_directory()
        self.unfollow_thread = None

    def setup_data_directory(self):
        """Create and return the data directory path"""
        # Create a data directory in the same folder as the script
        data_dir = Path(os.path.dirname(os.path.abspath(__file__))) / 'instagram_data'
        data_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (data_dir / 'csv_exports').mkdir(exist_ok=True)
        (data_dir / 'logs').mkdir(exist_ok=True)
        
        return data_dir

    def get_log_path(self):
        """Get the path for the log file"""
        return self.data_dir / 'logs' / 'action_log.json'

    def get_attempted_follows_path(self):
        """Get the path for the attempted follows file"""
        return self.data_dir / 'logs' / 'attempted_follows.json'

    def get_chrome_version(self):
        system = platform.system()
        try:
            if system == "Darwin":  # macOS
                process = subprocess.Popen(
                    ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                version = process.communicate()[0].decode('UTF-8').replace('Google Chrome ', '').strip()
                return version
            else:
                # Add Windows and Linux support if needed
                return None
        except:
            return None

    def init_driver(self):
        """Initialize the web driver"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_window_size(1200, 800)

    def login(self, log_signal):
        """Log in to Instagram"""
        try:
            self.driver.get('https://www.instagram.com/')
            time.sleep(2)
            
            log_signal.emit("Logging in to Instagram...")

            # Find and fill username field
            username_field = self.driver.find_element(By.NAME, 'username')
            if username_field:
                username_field.clear()
                username_field.send_keys(self.username)
            else:
                log_signal.emit("❌ Could not find username field")
                return False

            # Find and fill password field
            password_field = self.driver.find_element(By.NAME, 'password')
            if password_field:
                password_field.clear()
                password_field.send_keys(self.password)
            else:
                log_signal.emit("❌ Could not find password field")
                return False

            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            if login_button:
                login_button.click()
                time.sleep(3)  # Wait for login
                log_signal.emit("Successfully logged in!")
                return True
            else:
                log_signal.emit("❌ Could not find login button")
                return False

        except Exception as e:
            log_signal.emit(f"❌ Login error: {str(e)}")
            return False

    def load_followed_users(self):
        try:
            if os.path.exists('followed_users.json'):
                with open('followed_users.json', 'r') as f:
                    data = json.load(f)
                # Validate and filter out any invalid entries
                valid_data = []
                for user in data:
                    if isinstance(user, dict) and 'username' in user and 'followed_at' in user:
                        if 'unfollowed' not in user:
                            user['unfollowed'] = False
                        valid_data.append(user)
                return valid_data
        except Exception as e:
            print(f"Error loading followed users: {str(e)}")
        return []

    def save_followed_users(self):
        try:
            # Create backup of current file if it exists
            if os.path.exists('followed_users.json'):
                backup_path = 'followed_users.backup.json'
                with open('followed_users.json', 'r') as f:
                    current_data = f.read()
                with open(backup_path, 'w') as f:
                    f.write(current_data)

            # Save new data
            with open('followed_users.json', 'w') as f:
                json.dump(self.followed_users, f, indent=2)
        except Exception as e:
            print(f"Error saving followed users: {str(e)}")

    def find_element(self, by, value):
        """Find element in either regular driver or embedded browser"""
        try:
            return self.driver.find_element(by, value)
        except:
            return None

    def find_elements(self, by, value):
        """Find elements in either regular driver or embedded browser"""
        try:
            return self.driver.find_elements(by, value)
        except:
            return []

    def click_element(self, element):
        """Click element in either regular driver or embedded browser"""
        try:
            self.driver.execute_script("arguments[0].click();", element)
            return True
        except:
            return False

    def navigate_to(self, url):
        """Navigate to URL in either regular driver or embedded browser"""
        try:
            self.driver.get(url)
            time.sleep(1.5)
            return True
        except:
            return False

    def load_attempted_follows(self):
        """Load the list of previously attempted follows from JSON file"""
        try:
            attempted_follows_path = self.get_attempted_follows_path()
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
            attempted_follows_path = self.get_attempted_follows_path()
            with open(attempted_follows_path, 'w') as f:
                json.dump(self.attempted_follows, f, indent=2)
        except Exception as e:
            print(f"Error saving attempted follows: {str(e)}")

    def add_to_attempted_follows(self, username, status):
        """Add a username to the attempted follows list with status and timestamp"""
        self.attempted_follows[username] = {
            'status': status,  # 'success', 'failed', 'private', 'already_following'
            'timestamp': datetime.now().isoformat(),
            'instagram_username': self.username  # Track which account attempted the follow
        }
        self.save_attempted_follows()

    def should_skip_user(self, username, log_signal):
        """Check if we should skip attempting to follow this user"""
        if username in self.attempted_follows:
            attempt = self.attempted_follows[username]
            if attempt['instagram_username'] == self.username:  # Only skip if same account
                status = attempt['status']
                timestamp = attempt['timestamp']
                log_signal.emit(f"Skipping {username} - Previously attempted ({status}) on {timestamp}")
                return True
        return False

    def get_followers(self, account, log_signal, max_scroll_attempts=30):
        """Get followers that haven't been followed before"""
        followers = []
        unique_followers_needed = self.users_per_account
        scroll_without_new = 0
        max_scroll_without_new = 10  # Maximum scrolls without finding new users before moving on
        
        try:
            # Navigate to account page
            self.driver.get(f'https://www.instagram.com/{account}/')
            time.sleep(3)

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

            # Scroll and collect followers
            prev_followers_count = 0
            scroll_attempts = 0
            processed_usernames = set()  # Keep track of usernames we've already processed

            while len(followers) < unique_followers_needed and scroll_attempts < max_scroll_attempts:
                # Get follower elements
                follower_elements = followers_dialog.find_elements(By.CSS_SELECTOR, "a[role='link']")
                
                # Extract usernames
                new_followers_found = False
                for element in follower_elements:
                    try:
                        username = element.text
                        if username and username not in processed_usernames:
                            processed_usernames.add(username)
                            # Only add if we haven't attempted to follow before
                            if not self.should_skip_user(username, log_signal):
                                followers.append(username)
                                new_followers_found = True
                                log_signal.emit(f"Found new potential follow: {username}")
                                if len(followers) >= unique_followers_needed:
                                    break
                    except:
                        continue

                if not new_followers_found:
                    scroll_without_new += 1
                else:
                    scroll_without_new = 0

                # If we haven't found new followers in several attempts, try scrolling further
                scroll_distance = 300 if scroll_without_new < 3 else 600

                # Scroll
                try:
                    self.driver.execute_script(
                        f"arguments[0].scrollTop = arguments[0].scrollTop + {scroll_distance};",
                        followers_dialog
                    )
                    time.sleep(1.5)  # Slightly longer wait for content to load
                    
                    # Check if we've reached the bottom
                    current_height = self.driver.execute_script("return arguments[0].scrollTop", followers_dialog)
                    scroll_height = self.driver.execute_script("return arguments[0].scrollHeight", followers_dialog)
                    
                    if current_height >= scroll_height - 600:  # Near bottom
                        scroll_attempts += 1
                        log_signal.emit(f"Reached bottom of followers list, attempt {scroll_attempts}/{max_scroll_attempts}")
                    
                except Exception as e:
                    scroll_attempts += 1
                    log_signal.emit(f"Scroll error: {str(e)}")

                # Update progress
                if len(followers) > prev_followers_count:
                    log_signal.emit(f"Found {len(followers)}/{unique_followers_needed} new potential follows")
                    prev_followers_count = len(followers)

                # If we've made too many attempts without finding new users, try to refresh the dialog
                if scroll_without_new >= max_scroll_without_new:
                    try:
                        log_signal.emit("Refreshing followers dialog...")
                        self.driver.refresh()
                        time.sleep(3)
                        followers_link = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='followers']"))
                        )
                        followers_link.click()
                        time.sleep(2)
                        followers_dialog = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog']"))
                        )
                        scroll_without_new = 0
                    except:
                        pass

            if len(followers) < unique_followers_needed:
                log_signal.emit(f"Found {len(followers)} new potential follows in this account")
            else:
                log_signal.emit(f"Successfully found {len(followers)} new potential follows")

            return followers

        except Exception as e:
            log_signal.emit(f"Error collecting followers from {account}: {str(e)}")
            return followers

    def follow_user(self, username, log_signal):
        try:
            if self.should_skip_user(username, log_signal):
                return False

            # Navigate to user's profile
            self.driver.get(f'https://www.instagram.com/{username}/')
            time.sleep(2)

            # Find follow button - multiple possible selectors
            follow_button = None
            button_selectors = [
                "button[type='button']",  # General button
                "button._acan._acap._acas",  # Follow button class
                "button._acan._acap._acas._aj1-"  # Alternative follow button class
            ]
            
            for selector in button_selectors:
                try:
                    follow_button = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue

            if not follow_button:
                log_signal.emit(f"Could not find follow button for {username}")
                return False

            button_text = follow_button.text.lower()
            
            if button_text in ['follow', 'follow back']:
                # Store the button's current state
                initial_state = follow_button.get_attribute('class')
                
                # Click the follow button
                follow_button.click()
                time.sleep(2)  # Wait for state change
                
                # Multiple verification methods
                follow_success = False
                
                # Method 1: Check button text change
                try:
                    new_button = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='button']"))
                    )
                    new_text = new_button.text.lower()
                    if new_text in ['following', 'requested']:
                        follow_success = True
                except:
                    pass

                # Method 2: Check button class change
                if not follow_success:
                    try:
                        new_state = follow_button.get_attribute('class')
                        if new_state != initial_state:
                            follow_success = True
                    except:
                        pass

                # Method 3: Check for following/requested button
                if not follow_success:
                    try:
                        following_selectors = [
                            "button._acan._acap._acat",  # Following button
                            "button._acan._acap._acas._aj1-",  # Requested button
                            "button[type='button']._acan._acap._acat"  # Alternative following button
                        ]
                        
                        for selector in following_selectors:
                            try:
                                WebDriverWait(self.driver, 3).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                                )
                                follow_success = True
                                break
                            except:
                                continue
                    except:
                        pass

                # Final verification
                if follow_success:
                    log_signal.emit(f"✅ Successfully followed {username}")
                    self.add_to_attempted_follows(username, 'success')
                    return True
                else:
                    log_signal.emit(f"❌ Could not verify follow for {username}")
                    self.add_to_attempted_follows(username, 'failed')
                    return False
            else:
                status = 'private' if 'private' in self.driver.page_source.lower() else 'already_following'
                log_signal.emit(f"⏭️ Skipping {username} - {status}")
                self.add_to_attempted_follows(username, status)
                return False

        except Exception as e:
            log_signal.emit(f"❌ Error following {username}: {str(e)}")
            self.add_to_attempted_follows(username, 'failed')
            return False

    def verify_follow_status(self, username):
        """Additional method to double-check follow status"""
        try:
            # Check for following/requested status
            following_selectors = [
                "button._acan._acap._acat",  # Following button
                "button._acan._acap._acas._aj1-",  # Requested button
                "button[type='button']._acan._acap._acat",  # Alternative following button
                "button[type='button'] div._ab8w._ab94._ab97._ab9h._ab9m._ab9p"  # Following text container
            ]
            
            for selector in following_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        button_text = element.text.lower()
                        return button_text in ['following', 'requested']
                except:
                    continue
            
            return False
        except:
            return False

    def unfollow_user(self, username, log_signal):
        try:
            # Navigate to user's profile
            self.driver.get(f'https://www.instagram.com/{username}/')
            time.sleep(1.5)  # Reduced wait time

            # Debug: Log the page title and URL
            log_signal.emit(f"📍 Navigating to: {username}")

            # Find the Following/Requested button (handle both cases)
            button = None
            try:
                # Try to find any button containing either "Following" or "Requested"
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for b in buttons:
                    if b.is_displayed() and b.text.strip().lower() in ['following', 'requested']:
                        button = b
                        break

                if not button:
                    log_signal.emit(f"❌ Could not find Following/Requested button for {username}")
                    return False

                # Click the button to open the menu
                log_signal.emit("🖱️ Opening menu...")
                self.driver.execute_script("arguments[0].click();", button)
                time.sleep(0.5)  # Short wait for menu

                # Find and click the Unfollow button in the menu
                menu_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                unfollow_button = None
                
                for btn in menu_buttons:
                    if btn.is_displayed() and btn.text.strip().lower() == "unfollow":
                        unfollow_button = btn
                        break

                if unfollow_button:
                    log_signal.emit("🖱️ Clicking Unfollow...")
                    self.driver.execute_script("arguments[0].click();", unfollow_button)
                    time.sleep(0.5)  # Short wait for unfollow to complete
                    
                    # Quick verification
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        if btn.is_displayed() and btn.text.strip().lower() in ['follow', 'follow back']:
                            log_signal.emit(f"✅ Successfully unfollowed {username}")
                            return True
                    
                    log_signal.emit(f"⚠️ Could not verify unfollow for {username}")
                    return False
                else:
                    log_signal.emit(f"❌ Could not find Unfollow button for {username}")
                    return False

            except Exception as e:
                log_signal.emit(f"❌ Error during unfollow process: {str(e)}")
                return False

        except Exception as e:
            log_signal.emit(f"❌ Error accessing profile {username}: {str(e)}")
            return False

    def find_following_button(self, log_signal):
        """Find the Following button using multiple methods"""
        # Method 1: Direct class selector
        try:
            buttons = self.driver.find_elements(By.CSS_SELECTOR, "button._acan._acap._acat")
            for button in buttons:
                if button.is_displayed() and button.text.strip().lower() in ['following', 'requested']:
                    log_signal.emit("📌 Found Following button by class")
                    return button
        except:
            pass

        # Method 2: XPath with text
        try:
            buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Following') or contains(text(), 'Requested')]")
            for button in buttons:
                if button.is_displayed():
                    log_signal.emit("📌 Found Following button by text")
                    return button
        except:
            pass

        # Method 3: Button with specific div structure
        try:
            buttons = self.driver.find_elements(By.XPATH, "//button[.//div[contains(text(), 'Following') or contains(text(), 'Requested')]]")
            for button in buttons:
                if button.is_displayed():
                    log_signal.emit("📌 Found Following button by div structure")
                    return button
        except:
            pass

        return None

    def verify_following_status(self, username, log_signal):
        """Verify that we are actually following the user"""
        try:
            # Method 1: Check for Following button
            buttons = self.driver.find_elements(By.CSS_SELECTOR, "button._acan._acap._acat")
            for button in buttons:
                if button.is_displayed() and button.text.strip().lower() in ['following', 'requested']:
                    log_signal.emit("✓ Verified following status by button")
                    return True

            # Method 2: Check page source
            page_source = self.driver.page_source.lower()
            if 'following' in page_source or 'requested' in page_source:
                log_signal.emit("✓ Verified following status by page source")
                return True

            # Method 3: Check button with specific div structure
            buttons = self.driver.find_elements(By.XPATH, "//button[.//div[contains(text(), 'Following') or contains(text(), 'Requested')]]")
            if any(b.is_displayed() for b in buttons):
                log_signal.emit("✓ Verified following status by div structure")
                return True

            log_signal.emit("⚠️ Could not verify following status")
            return False
        except Exception as e:
            log_signal.emit(f"❌ Error verifying following status: {str(e)}")
            return False

    def verify_unfollow_success(self, username, log_signal):
        """Verify that the unfollow was successful"""
        try:
            time.sleep(2)  # Wait for page to update
            
            # Method 1: Check for Follow button
            try:
                follow_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button._acan._acap._acas")
                for button in follow_buttons:
                    if button.is_displayed() and button.text.strip().lower() in ['follow', 'follow back']:
                        log_signal.emit("✓ Verified unfollow by Follow button presence")
                        return True
            except:
                pass

            # Method 2: Check that Following button is gone
            try:
                following_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button._acan._acap._acat")
                if not any(b.is_displayed() and b.text.strip().lower() in ['following', 'requested'] for b in following_buttons):
                    log_signal.emit("✓ Verified unfollow by Following button absence")
                    return True
            except:
                pass

            # Method 3: Refresh and check
            try:
                self.driver.refresh()
                time.sleep(2)
                follow_buttons = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button._acan._acap._acas"))
                )
                for button in follow_buttons:
                    if button.is_displayed() and button.text.strip().lower() in ['follow', 'follow back']:
                        log_signal.emit("✓ Verified unfollow after page refresh")
                        return True
            except:
                pass

            return False
        except Exception as e:
            log_signal.emit(f"❌ Error verifying unfollow: {str(e)}")
            return False

    def unfollow_scheduler(self, log_signal):
        log_signal.emit("Starting unfollow scheduler...")
        
        while self.is_running:
            try:
                current_time = datetime.now()
                unfollowed_count = 0
                
                # Load the latest followed_users data
                self.followed_users = self.load_followed_users()
                
                # Check each followed user
                for user in self.followed_users:
                    if not self.is_running:
                        break
                        
                    if not user['unfollowed']:
                        followed_time = datetime.fromisoformat(user['followed_at'])
                        time_diff = current_time - followed_time
                        
                        # Log time until unfollow
                        hours_left = (timedelta(seconds=self.unfollow_delay) - time_diff).total_seconds() / 3600
                        if hours_left > 0:
                            log_signal.emit(f"Will unfollow {user['username']} in {hours_left:.1f} hours")
                            continue
                            
                        if time_diff > timedelta(seconds=self.unfollow_delay):
                            # Try to unfollow
                            if self.unfollow_user(user['username'], log_signal):
                                user['unfollowed'] = True
                                user['unfollowed_at'] = current_time.isoformat()
                                self.save_followed_users()
                                unfollowed_count += 1
                                
                                # Add random delay between unfollows
                                delay = random.uniform(self.min_delay, self.max_delay)
                                log_signal.emit(f"Waiting {delay:.1f} seconds before next unfollow...")
                                time.sleep(delay)
                
                if unfollowed_count > 0:
                    log_signal.emit(f"Unfollowed {unfollowed_count} users in this cycle")
                
                # Sleep for a while before next check
                # Check every 15 minutes instead of every minute
                time.sleep(900)
                
            except Exception as e:
                log_signal.emit(f"Error in unfollow scheduler: {str(e)}")
                time.sleep(60)  # Wait a minute before retrying if there's an error

    def run(self, log_signal):
        """Run the follow operation"""
        try:
            self.init_driver()
            if not self.login(log_signal):
                return []

            successfully_followed = []
            total_follows_needed = self.users_per_account
            max_cycles = 5  # Maximum number of times to cycle through all accounts
            cycles_without_new_follows = 0

            while len(successfully_followed) < total_follows_needed and cycles_without_new_follows < max_cycles:
                if not self.is_running:
                    break

                follows_before_cycle = len(successfully_followed)
                log_signal.emit(f"\n=== Starting new cycle through target accounts (cycle {cycles_without_new_follows + 1}/{max_cycles}) ===")
                log_signal.emit(f"Currently have {len(successfully_followed)}/{total_follows_needed} follows")

                for target_account in self.target_accounts:
                    if not self.is_running or len(successfully_followed) >= total_follows_needed:
                        break

                    remaining_follows = total_follows_needed - len(successfully_followed)
                    log_signal.emit(f"\nProcessing followers of {target_account} - Need {remaining_follows} more follows")
                    
                    # Temporarily set users_per_account to remaining follows needed
                    original_users_per_account = self.users_per_account
                    self.users_per_account = remaining_follows
                    followers = self.get_followers(target_account, log_signal)
                    self.users_per_account = original_users_per_account

                    for follower in followers:
                        if not self.is_running or len(successfully_followed) >= total_follows_needed:
                            break

                        if self.follow_user(follower, log_signal):
                            successfully_followed.append(follower)
                            # Export CSV after each successful follow
                            self.export_followed_users(successfully_followed, log_signal)
                            # Random delay between follows
                            delay = random.uniform(self.min_delay, self.max_delay)
                            log_signal.emit(f"Waiting {delay:.1f} seconds... ({len(successfully_followed)}/{total_follows_needed} completed)")
                            time.sleep(delay)

                # Check if we found any new follows in this cycle
                if len(successfully_followed) == follows_before_cycle:
                    cycles_without_new_follows += 1
                    log_signal.emit(f"\nNo new follows found in this cycle. {max_cycles - cycles_without_new_follows} cycles remaining before stopping.")
                else:
                    cycles_without_new_follows = 0  # Reset counter if we found new follows
                    log_signal.emit(f"\nFound {len(successfully_followed) - follows_before_cycle} new follows in this cycle!")

                # If we haven't reached our goal, prepare for next cycle
                if len(successfully_followed) < total_follows_needed and cycles_without_new_follows < max_cycles:
                    log_signal.emit("\nStarting new cycle through target accounts to find more follows...")
                    time.sleep(5)  # Brief pause between cycles

            # Final status message
            if len(successfully_followed) >= total_follows_needed:
                log_signal.emit(f"\nSuccess! Found and followed all {total_follows_needed} requested accounts.")
            else:
                log_signal.emit(f"\nExhausted all possibilities. Could only find {len(successfully_followed)} accounts to follow after {max_cycles} cycles.")
                log_signal.emit("Consider adding more target accounts or waiting some time before trying again.")

            return successfully_followed

        except Exception as e:
            log_signal.emit(f"Error in automation: {str(e)}")
            return successfully_followed
        finally:
            if self.driver:
                self.driver.quit()

    def run_unfollow(self, log_signal):
        """Run the unfollow operation with optimized performance"""
        try:
            self.init_driver()
            if not self.login(log_signal):
                return []

            successfully_unfollowed = []
            failed_attempts = []

            for username in self.target_accounts:
                if not self.is_running:
                    break

                try:
                    if self.unfollow_user(username, log_signal):
                        successfully_unfollowed.append(username)
                    else:
                        failed_attempts.append(username)
                    
                    # Randomized shorter delay between unfollows
                    delay = random.uniform(self.min_delay / 2, self.max_delay / 2)
                    log_signal.emit(f"⏳ Short wait ({delay:.1f}s)...")
                    time.sleep(delay)

                except Exception as e:
                    log_signal.emit(f"❌ Error processing {username}: {str(e)}")
                    failed_attempts.append(username)

            # Log summary
            if failed_attempts:
                log_signal.emit("\n⚠️ Failed to unfollow these accounts:")
                for username in failed_attempts:
                    log_signal.emit(f"- {username}")

            return successfully_unfollowed

        except Exception as e:
            log_signal.emit(f"❌ Error in automation: {str(e)}")
            return successfully_unfollowed
        finally:
            if self.driver:
                self.driver.quit()

    def stop(self):
        self.is_running = False
        if self.driver:
            self.driver.quit()
            self.driver = None 

    def export_followed_users(self, usernames, log_signal):
        """Export followed users to CSV with explicit path"""
        try:
            # Create timestamp for filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Create the full path for the CSV file
            csv_dir = self.data_dir / 'csv_exports'
            csv_path = csv_dir / f'followed_users_{timestamp}.csv'
            
            # Write the CSV file
            with open(csv_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Username', 'Followed At', 'Status'])
                for username in usernames:
                    status = self.attempted_follows.get(username, {}).get('status', 'unknown')
                    writer.writerow([username, datetime.now().isoformat(), status])
            
            log_signal.emit(f"Exported {len(usernames)} followed users to {csv_path}")
            return str(csv_path)
            
        except Exception as e:
            log_signal.emit(f"Error exporting followed users: {str(e)}")
            return None

    def import_unfollow_list(self, file_path, log_signal=None):
        """Import list of accounts to unfollow from CSV"""
        try:
            usernames = []
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:  # Skip empty rows
                        usernames.append(row[0].strip())
            
            if log_signal:
                log_signal.emit(f"✅ Successfully imported {len(usernames)} usernames from CSV")
            
            # Update the GUI to show the imported file path
            self.unfollow_csv_file = file_path
            self.unfollow_csv_path_label.setText(f"Selected file: {file_path}")
            self.unfollow_csv_path_label.setStyleSheet("color: green")
            self.unfollow_start_button.setEnabled(True)
            
            return usernames
        except Exception as e:
            if log_signal:
                log_signal.emit(f"❌ Error importing unfollow list: {str(e)}")
            self.unfollow_csv_path_label.setText("Error importing file")
            self.unfollow_csv_path_label.setStyleSheet("color: red")
            self.unfollow_start_button.setEnabled(False)
            return []

    def create_unfollow_tab(self):
        unfollow_tab = QWidget()
        layout = QVBoxLayout()

        # Create widgets
        self.unfollow_csv_label = QLabel("Select CSV file with accounts to unfollow:")
        self.unfollow_csv_path_label = QLabel("")  # Add label to show selected file path
        self.unfollow_csv_path_label.setWordWrap(True)  # Enable word wrap for long paths
        self.unfollow_csv_button = QPushButton("Choose CSV File")
        self.unfollow_start_button = QPushButton("Start Unfollowing")
        self.unfollow_stop_button = QPushButton("Stop")
        self.unfollow_stop_button.setEnabled(False)

        # Add widgets to layout
        layout.addWidget(self.unfollow_csv_label)
        layout.addWidget(self.unfollow_csv_button)
        layout.addWidget(self.unfollow_csv_path_label)  # Add the path label to layout
        layout.addWidget(self.unfollow_start_button)
        layout.addWidget(self.unfollow_stop_button)
        layout.addStretch()

        # Connect buttons
        self.unfollow_csv_button.clicked.connect(self.select_unfollow_csv)
        self.unfollow_start_button.clicked.connect(self.start_unfollow)
        self.unfollow_stop_button.clicked.connect(self.stop_unfollow)

        unfollow_tab.setLayout(layout)
        return unfollow_tab

    def select_unfollow_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_name:
            self.unfollow_csv_file = file_name
            # Update the label to show the selected file path
            self.unfollow_csv_path_label.setText(f"Selected file: {file_name}")
            self.unfollow_csv_path_label.setStyleSheet("color: green")  # Make it green to indicate success
            self.unfollow_start_button.setEnabled(True)
        else:
            self.unfollow_csv_path_label.setText("No file selected")
            self.unfollow_csv_path_label.setStyleSheet("color: red")  # Make it red to indicate no selection
            self.unfollow_start_button.setEnabled(False) 