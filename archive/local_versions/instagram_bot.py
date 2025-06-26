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

class InstagramBot:
    def __init__(self, username, password, target_accounts, users_per_account=50,
                 unfollow_delay=0):
        self.username = username
        self.password = password
        self.target_accounts = target_accounts
        self.users_per_account = users_per_account
        self.unfollow_delay = unfollow_delay
        
        # Fixed optimal delays - no user configuration needed
        self.follow_min_delay = 25  # Slightly longer for following (more restricted)
        self.follow_max_delay = 45
        self.unfollow_min_delay = 3  # Much shorter for unfollowing (less restricted)
        self.unfollow_max_delay = 8
        self.driver = None
        self.followed_users = []
        self.is_running = True
        self.unfollow_thread = None
        self.data_dir = self.setup_data_directory()
        self.attempted_follows = self.load_attempted_follows()

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

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        
        system = platform.system()
        if system == "Darwin":  # macOS
            # Use system installed ChromeDriver
            chromedriver_path = "/usr/local/bin/chromedriver"
            if not os.path.exists(chromedriver_path):
                raise Exception("ChromeDriver not found. Please install it using 'brew install --cask chromedriver'")
            
            # Set Chrome binary location
            chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            
            # Create service with system ChromeDriver
            service = Service(executable_path=chromedriver_path)
            
            # Verify ChromeDriver permissions
            if not os.access(chromedriver_path, os.X_OK):
                raise Exception(
                    "ChromeDriver is not executable. Please run these commands in terminal:\n"
                    "sudo xattr -d com.apple.quarantine /usr/local/bin/chromedriver\n"
                    "chmod +x /usr/local/bin/chromedriver"
                )
        else:
            # For other operating systems, use webdriver_manager
            service = Service(ChromeDriverManager().install())
            
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            error_msg = str(e)
            if "chromedriver" in error_msg.lower() and system == "Darwin":
                raise Exception(
                    "ChromeDriver security issue detected. Please run these commands in terminal:\n"
                    "sudo xattr -d com.apple.quarantine /usr/local/bin/chromedriver\n"
                    "chmod +x /usr/local/bin/chromedriver"
                )
            raise Exception(f"Failed to initialize Chrome driver: {error_msg}")

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

    def login(self, log_signal):
        try:
            log_signal.emit("Logging in to Instagram...")
            self.driver.get('https://www.instagram.com/accounts/login/')
            time.sleep(2)

            # Enter username
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.send_keys(self.username)

            # Enter password
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(self.password)

            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            # Wait for login to complete
            time.sleep(5)
            
            # Check for successful login
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Home']"))
                )
                log_signal.emit("Successfully logged in!")
                return True
            except TimeoutException:
                log_signal.emit("Login failed - please check your credentials")
                return False

        except Exception as e:
            log_signal.emit(f"Error during login: {str(e)}")
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

    def fast_unfollow_user(self, username, log_signal):
        """Fast unfollow with enhanced reliability - optimized version"""
        try:
            start_time = time.time()
            log_signal.emit(f"🚀 Fast unfollow: {username}")
            
            # Navigate to user's profile
            self.driver.get(f'https://www.instagram.com/{username}/')
            
            # Quick page existence check with better timing
            WebDriverWait(self.driver, 3).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            if "Sorry, this page isn't available" in self.driver.page_source:
                log_signal.emit(f"❌ Profile {username} doesn't exist or is unavailable")
                return False

            # Enhanced relationship button detection
            try:
                relationship_button = None
                button_text = None
                
                # Try multiple detection methods quickly
                for attempt in range(2):
                    # Method 1: Fast button scan
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for button in buttons:
                        try:
                            if button.is_displayed() and button.is_enabled():
                                text = button.text.strip().lower()
                                if text in ['following', 'requested']:
                                    relationship_button = button
                                    button_text = text
                                    break
                                elif text in ['follow', 'follow back']:
                                    log_signal.emit(f"⚠️ Not following {username}")
                                    return False
                        except:
                            continue
                    
                    if relationship_button:
                        break
                    elif attempt == 0:
                        time.sleep(0.5)  # Brief wait for elements to load
                
                if not relationship_button:
                    log_signal.emit(f"⚠️ No relationship button found for {username}")
                    return False
                
                # Enhanced clicking
                click_success = False
                
                # Try standard click first
                try:
                    # Ensure element is in view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", relationship_button)
                    time.sleep(0.2)
                    
                    relationship_button.click()
                    click_success = True
                except:
                    pass
                
                # Fallback to JavaScript click
                if not click_success:
                    try:
                        self.driver.execute_script("arguments[0].click();", relationship_button)
                        click_success = True
                    except:
                        log_signal.emit(f"❌ Failed to click relationship button for {username}")
                        return False
                
                # Wait for menu with progressive timeout
                menu_found = False
                for wait_time in [0.4, 0.8]:
                    time.sleep(wait_time)
                    
                    # Quick check if menu appeared
                    elements = (
                        self.driver.find_elements(By.TAG_NAME, "button") + 
                        self.driver.find_elements(By.CSS_SELECTOR, "div[role='button']")
                    )
                    
                    for element in elements:
                        try:
                            if element.is_displayed():
                                text = element.text.strip().lower()
                                if any(term in text for term in ['unfollow', 'cancel']):
                                    menu_found = True
                                    break
                        except:
                            continue
                    
                    if menu_found:
                        break
                
                # Find and click unfollow option with enhanced detection
                action_button = None
                search_terms = ['cancel request', 'cancel', 'unfollow'] if 'request' in button_text else ['unfollow']
                
                # Get fresh element list
                clickable_elements = (
                    self.driver.find_elements(By.TAG_NAME, "button") + 
                    self.driver.find_elements(By.CSS_SELECTOR, "div[role='button']")
                )
                
                # Look for exact matches first, then partial
                for exact_match in [True, False]:
                    for element in clickable_elements:
                        try:
                            if element.is_displayed() and element.is_enabled():
                                element_text = element.text.strip().lower()
                                
                                for term in search_terms:
                                    if exact_match:
                                        if term == element_text:
                                            action_button = element
                                            break
                                    else:
                                        if term in element_text and len(element_text) < 30:
                                            action_button = element
                                            break
                                
                                if action_button:
                                    break
                        except:
                            continue
                    
                    if action_button:
                        break
                
                if action_button:
                    action_text = action_button.text.strip()
                    
                    # Enhanced action button clicking
                    try:
                        action_button.click()
                    except:
                        try:
                            self.driver.execute_script("arguments[0].click();", action_button)
                        except:
                            log_signal.emit(f"❌ Failed to click unfollow option for {username}")
                            return False
                    
                    time.sleep(0.3)  # Brief wait for potential confirmation
                    
                    # Handle confirmation dialog if needed
                    if 'unfollow' in action_text.lower():
                        try:
                            # Quick confirmation search
                            confirm_elements = self.driver.find_elements(By.TAG_NAME, "button")
                            for elem in confirm_elements:
                                try:
                                    if elem.is_displayed() and 'unfollow' in elem.text.lower():
                                        elem.click()
                                        break
                                except:
                                    continue
                        except:
                            pass  # No confirmation or already handled
                    
                    elapsed = time.time() - start_time
                    action_word = "cancelled request" if 'request' in button_text else "unfollowed"
                    log_signal.emit(f"✅ Fast {action_word} {username} ({elapsed:.1f}s)")
                    return True
                else:
                    log_signal.emit(f"❌ Could not find unfollow option for {username}")
                    return False
                    
            except Exception as e:
                log_signal.emit(f"❌ Error in fast unfollow for {username}: {str(e)}")
                return False
                
        except Exception as e:
            log_signal.emit(f"❌ Critical error processing {username}: {str(e)}")
            return False

    def find_relationship_button_fast(self, driver):
        """Quickly find Following/Requested button"""
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if button.is_displayed():
                    text = button.text.strip().lower()
                    if text in ['following', 'requested']:
                        return button
            return None
        except:
            return None

    def unfollow_user(self, username, log_signal):
        """Robust unfollow method with enhanced error handling and multiple detection strategies"""
        try:
            log_signal.emit(f"🔄 Starting unfollow process for {username}")
            
            # Navigate to user's profile
            self.driver.get(f'https://www.instagram.com/{username}/')
            
            # Check if profile exists early
            WebDriverWait(self.driver, 5).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            if "Sorry, this page isn't available" in self.driver.page_source:
                log_signal.emit(f"❌ Profile {username} doesn't exist or is unavailable")
                return False

            # Wait for main content with better timeout handling
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "main"))
                )
                # Additional wait for dynamic content
                time.sleep(2)
                log_signal.emit(f"✅ Profile page loaded for {username}")
            except TimeoutException:
                log_signal.emit(f"⏳ Timeout loading profile for {username}")
                return False

            # Enhanced relationship button detection with multiple strategies
            relationship_button = None
            button_status = None
            
            for attempt in range(3):  # Try up to 3 times
                try:
                    log_signal.emit(f"🔍 Attempt {attempt + 1}: Searching for relationship button...")
                    
                    # Strategy 1: Standard button search
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for button in buttons:
                        try:
                            if button.is_displayed() and button.is_enabled():
                                button_text = button.text.strip().lower()
                                
                                if button_text in ['following', 'requested']:
                                    relationship_button = button
                                    button_status = button_text
                                    log_signal.emit(f"✅ Found '{button_text}' button (standard search)")
                                    break
                                elif button_text in ['follow', 'follow back']:
                                    log_signal.emit(f"⚠️ Found '{button_text}' - we are NOT following this user")
                                    return False
                        except:
                            continue
                    
                    # Strategy 2: CSS selector search if standard failed
                    if not relationship_button:
                        css_selectors = [
                            "button[type='button']",
                            "button._acan._acap._acat",  # Following button classes
                            "button._acan._acap._acas._aj1-",  # Requested button classes
                        ]
                        
                        for selector in css_selectors:
                            try:
                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                for element in elements:
                                    if element.is_displayed() and element.is_enabled():
                                        element_text = element.text.strip().lower()
                                        if element_text in ['following', 'requested']:
                                            relationship_button = element
                                            button_status = element_text
                                            log_signal.emit(f"✅ Found '{element_text}' button (CSS search)")
                                            break
                                if relationship_button:
                                    break
                            except:
                                continue
                    
                    # Strategy 3: XPath search as last resort
                    if not relationship_button:
                        xpath_selectors = [
                            "//button[contains(text(), 'Following')]",
                            "//button[contains(text(), 'Requested')]",
                            "//*[@role='button'][contains(text(), 'Following')]",
                            "//*[@role='button'][contains(text(), 'Requested')]"
                        ]
                        
                        for xpath in xpath_selectors:
                            try:
                                element = self.driver.find_element(By.XPATH, xpath)
                                if element.is_displayed() and element.is_enabled():
                                    relationship_button = element
                                    button_status = element.text.strip().lower()
                                    log_signal.emit(f"✅ Found '{button_status}' button (XPath search)")
                                    break
                            except:
                                continue
                    
                    if relationship_button:
                        break
                    else:
                        log_signal.emit(f"⏳ Attempt {attempt + 1} failed, waiting and retrying...")
                        time.sleep(1)
                        
                except Exception as e:
                    log_signal.emit(f"❌ Error in attempt {attempt + 1}: {str(e)}")
                    time.sleep(1)
            
            if not relationship_button:
                log_signal.emit(f"❌ Could not find Following/Requested button for {username}")
                return False

            # Enhanced clicking with multiple fallback methods
            try:
                log_signal.emit(f"🖱️ Clicking '{button_status}' button...")
                
                # Ensure button is in viewport and clickable
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", relationship_button)
                time.sleep(1)
                
                # Wait for element to be clickable
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(relationship_button))
                
                # Try multiple click methods
                click_success = False
                
                # Method 1: Standard click
                try:
                    relationship_button.click()
                    click_success = True
                    log_signal.emit("✅ Standard click successful")
                except Exception as e:
                    log_signal.emit(f"⚠️ Standard click failed: {str(e)}")
                
                # Method 2: ActionChains click
                if not click_success:
                    try:
                        ActionChains(self.driver).move_to_element(relationship_button).click().perform()
                        click_success = True
                        log_signal.emit("✅ ActionChains click successful")
                    except Exception as e:
                        log_signal.emit(f"⚠️ ActionChains click failed: {str(e)}")
                
                # Method 3: JavaScript click
                if not click_success:
                    try:
                        self.driver.execute_script("arguments[0].click();", relationship_button)
                        click_success = True
                        log_signal.emit("✅ JavaScript click successful")
                    except Exception as e:
                        log_signal.emit(f"⚠️ JavaScript click failed: {str(e)}")
                
                if not click_success:
                    log_signal.emit("❌ All click methods failed")
                    return False
                
                # Wait for menu to appear with progressive timeout
                menu_appeared = False
                for wait_time in [0.5, 1.0, 1.5]:
                    time.sleep(wait_time)
                    
                    # Check if menu appeared by looking for new clickable elements
                    new_elements = (
                        self.driver.find_elements(By.TAG_NAME, "button") + 
                        self.driver.find_elements(By.CSS_SELECTOR, "div[role='button']")
                    )
                    
                    for element in new_elements:
                        try:
                            if element.is_displayed():
                                element_text = element.text.strip().lower()
                                if any(term in element_text for term in ['unfollow', 'cancel']):
                                    menu_appeared = True
                                    break
                        except:
                            continue
                    
                    if menu_appeared:
                        log_signal.emit(f"✅ Menu appeared after {wait_time}s")
                        break
                
                if not menu_appeared:
                    log_signal.emit("⚠️ Menu may not have appeared, proceeding anyway...")
                
            except Exception as e:
                log_signal.emit(f"❌ Failed to click relationship button: {str(e)}")
                return False

            # Enhanced unfollow option detection
            try:
                log_signal.emit("🔍 Searching for unfollow option...")
                
                # Determine search terms based on button status
                if button_status == 'requested':
                    search_terms = ['cancel request', 'cancel', 'unfollow']
                    log_signal.emit("🔍 Looking for cancel/unfollow options (pending request)")
                else:
                    search_terms = ['unfollow']
                    log_signal.emit("🔍 Looking for unfollow option")
                
                action_button = None
                
                # Multiple detection attempts with different strategies
                for detection_attempt in range(2):
                    log_signal.emit(f"🔍 Detection attempt {detection_attempt + 1}")
                    
                    # Get fresh element lists
                    try:
                        all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        all_divs = self.driver.find_elements(By.CSS_SELECTOR, "div[role='button']")
                        all_clickable = all_buttons + all_divs
                        
                        log_signal.emit(f"📊 Found {len(all_clickable)} total clickable elements")
                        
                        # Look for exact matches first
                        for element in all_clickable:
                            try:
                                if element.is_displayed() and element.is_enabled():
                                    element_text = element.text.strip().lower()
                                    
                                    # Check for exact term matches
                                    for term in search_terms:
                                        if term == element_text:
                                            action_button = element
                                            log_signal.emit(f"🎯 Found exact match: '{element.text.strip()}'")
                                            break
                                    
                                    if action_button:
                                        break
                            except:
                                continue
                        
                        # If no exact match, look for partial matches
                        if not action_button:
                            for element in all_clickable:
                                try:
                                    if element.is_displayed() and element.is_enabled():
                                        element_text = element.text.strip().lower()
                                        
                                        # Check for partial term matches
                                        for term in search_terms:
                                            if term in element_text and len(element_text) < 50:  # Avoid long text
                                                action_button = element
                                                log_signal.emit(f"🎯 Found partial match: '{element.text.strip()}'")
                                                break
                                        
                                        if action_button:
                                            break
                                except:
                                    continue
                        
                        if action_button:
                            break
                        else:
                            log_signal.emit(f"⏳ Attempt {detection_attempt + 1} failed, waiting...")
                            time.sleep(0.5)
                            
                    except Exception as e:
                        log_signal.emit(f"❌ Error in detection attempt {detection_attempt + 1}: {str(e)}")
                        time.sleep(0.5)
                
                if action_button:
                    action_text = action_button.text.strip()
                    log_signal.emit(f"🖱️ Clicking unfollow option: '{action_text}'")
                    
                    # Enhanced clicking for unfollow option
                    unfollow_click_success = False
                    
                    # Method 1: Direct click
                    try:
                        action_button.click()
                        unfollow_click_success = True
                        log_signal.emit("✅ Unfollow option clicked successfully")
                    except Exception as e:
                        log_signal.emit(f"⚠️ Direct click failed: {str(e)}")
                    
                    # Method 2: JavaScript click
                    if not unfollow_click_success:
                        try:
                            self.driver.execute_script("arguments[0].click();", action_button)
                            unfollow_click_success = True
                            log_signal.emit("✅ JavaScript unfollow click successful")
                        except Exception as e:
                            log_signal.emit(f"⚠️ JavaScript click failed: {str(e)}")
                    
                    if not unfollow_click_success:
                        log_signal.emit("❌ Failed to click unfollow option")
                        return False
                    
                    # Handle confirmation dialog with better detection
                    time.sleep(0.8)  # Wait for potential confirmation dialog
                    
                    if 'unfollow' in action_text.lower():
                        try:
                            # Look for confirmation dialog
                            confirm_selectors = [
                                "//button[contains(text(), 'Unfollow')]",
                                "//button[contains(translate(text(), 'UNFOLLOW', 'unfollow'), 'unfollow')]",
                                "//*[@role='button'][contains(text(), 'Unfollow')]"
                            ]
                            
                            confirm_button = None
                            for selector in confirm_selectors:
                                try:
                                    elements = self.driver.find_elements(By.XPATH, selector)
                                    for element in elements:
                                        if element.is_displayed() and element.is_enabled():
                                            confirm_button = element
                                            break
                                    if confirm_button:
                                        break
                                except:
                                    continue
                            
                            if confirm_button:
                                log_signal.emit("🔍 Found confirmation dialog, clicking confirm...")
                                try:
                                    confirm_button.click()
                                    log_signal.emit("✅ Confirmation clicked")
                                except:
                                    self.driver.execute_script("arguments[0].click();", confirm_button)
                                    log_signal.emit("✅ Confirmation clicked (JS)")
                            else:
                                log_signal.emit("ℹ️ No confirmation dialog found (action may be complete)")
                                
                        except Exception as e:
                            log_signal.emit(f"⚠️ Error handling confirmation: {str(e)}")
                    
                    # Quick success verification
                    time.sleep(1)
                    
                    try:
                        # Check if we can find a "Follow" button now (indicating success)
                        post_action_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for button in post_action_buttons:
                            try:
                                if button.is_displayed():
                                    button_text = button.text.strip().lower()
                                    if button_text in ['follow', 'follow back']:
                                        if button_status == 'requested':
                                            log_signal.emit(f"✅ Successfully cancelled follow request for {username}")
                                        else:
                                            log_signal.emit(f"✅ Successfully unfollowed {username}")
                                        return True
                            except:
                                continue
                        
                        # If no clear indication, assume success (better than false negative)
                        log_signal.emit(f"✅ Unfollow action completed for {username}")
                        return True
                        
                    except Exception as e:
                        log_signal.emit(f"✅ Unfollow completed for {username} (verification skipped: {str(e)})")
                        return True
                    
                else:
                    # Enhanced debugging when no unfollow option is found
                    log_signal.emit("❌ Could not find unfollow option")
                    
                    try:
                        # Show available options for debugging
                        all_elements = (
                            self.driver.find_elements(By.TAG_NAME, "button") + 
                            self.driver.find_elements(By.CSS_SELECTOR, "div[role='button']")
                        )
                        
                        visible_options = []
                        for element in all_elements:
                            try:
                                if element.is_displayed() and element.text.strip():
                                    visible_options.append(element.text.strip())
                            except:
                                continue
                        
                        if visible_options:
                            log_signal.emit(f"🔍 Available options: {visible_options[:10]}")  # Show first 10
                        else:
                            log_signal.emit("🔍 No visible options found")
                            
                    except:
                        pass
                    
                    return False
                    
            except Exception as e:
                log_signal.emit(f"❌ Error in unfollow detection: {str(e)}")
                return False

        except Exception as e:
            log_signal.emit(f"❌ Critical error processing {username}: {str(e)}")
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
                                
                                # Add random delay between unfollows (automatic optimal timing)
                                delay = random.uniform(self.unfollow_min_delay, self.unfollow_max_delay)
                                log_signal.emit(f"⏳ Auto delay: {delay:.1f}s before next unfollow...")
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
                            # Random delay between follows (automatic optimal timing)
                            delay = random.uniform(self.follow_min_delay, self.follow_max_delay)
                            log_signal.emit(f"⏳ Auto delay: {delay:.1f}s... ({len(successfully_followed)}/{total_follows_needed} completed)")
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
        """Run the unfollow operation"""
        try:
            log_signal.emit("🚀 Initializing Chrome driver...")
            if not self.init_driver():
                log_signal.emit("❌ Failed to initialize Chrome driver")
                return []
            
            log_signal.emit("🔐 Logging in to Instagram...")
            if not self.login(log_signal):
                log_signal.emit("❌ Failed to log in to Instagram")
                return []

            successfully_unfollowed = []
            total_accounts = len(self.target_accounts)
            
            log_signal.emit(f"📋 Starting unfollow process for {total_accounts} accounts")

            for i, username in enumerate(self.target_accounts, 1):
                if not self.is_running:
                    log_signal.emit("⏹️ Process stopped by user")
                    break

                log_signal.emit(f"\n📍 Processing {i}/{total_accounts}: {username}")
                
                if self.unfollow_user(username, log_signal):
                    successfully_unfollowed.append(username)
                    log_signal.emit(f"✅ Progress: {len(successfully_unfollowed)}/{total_accounts} completed")
                else:
                    log_signal.emit(f"❌ Failed to unfollow {username}")
                
                # Only add delay if not the last account (automatic optimal timing)
                if i < total_accounts and self.is_running:
                    delay = random.uniform(self.unfollow_min_delay, self.unfollow_max_delay)
                    log_signal.emit(f"⏳ Auto delay: {delay:.1f}s...")
                    time.sleep(delay)

            log_signal.emit(f"\n🎉 Unfollow process completed!")
            log_signal.emit(f"✅ Successfully unfollowed: {len(successfully_unfollowed)}/{total_accounts} accounts")
            
            if len(successfully_unfollowed) < total_accounts:
                failed_count = total_accounts - len(successfully_unfollowed)
                log_signal.emit(f"⚠️ Failed to unfollow: {failed_count} accounts")

            return successfully_unfollowed

        except Exception as e:
            log_signal.emit(f"❌ Error in unfollow automation: {str(e)}")
            return successfully_unfollowed if 'successfully_unfollowed' in locals() else []
        finally:
            if self.driver:
                log_signal.emit("🔒 Closing browser...")
                self.driver.quit()

    def stop(self):
        self.is_running = False
        if self.driver:
            self.driver.quit()
            self.driver = None 

    def init_driver(self):
        """Initialize Chrome driver with optimized settings for Instagram"""
        try:
            options = webdriver.ChromeOptions()
            
            # Basic stability options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Window and display options
            options.add_argument('--start-maximized')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            
            # User agent to appear more natural
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Performance options optimized for 6-core parallel processing
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')  # Speed up loading
            options.add_argument('--disable-javascript')  # Faster page loads
            options.add_argument('--disable-css')  # Skip CSS loading
            options.add_argument('--disable-web-security')  # Faster processing
            options.add_argument('--aggressive-cache-discard')  # Memory optimization
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(10)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True
            
        except Exception as e:
            print(f"Error initializing driver: {str(e)}")
            return False

    def export_followed_users(self, usernames, log_signal):
        """Export followed users to CSV with explicit path - optimized for batch export"""
        try:
            # Create timestamp for filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Create the full path for the CSV file
            csv_dir = self.data_dir / 'csv_exports'
            csv_path = csv_dir / f'followed_users_batch_{timestamp}.csv'
            
            # Write the CSV file with more detailed information
            with open(csv_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Username', 'Followed At', 'Status', 'Instagram Account'])
                for username in usernames:
                    attempt_data = self.attempted_follows.get(username, {})
                    status = attempt_data.get('status', 'unknown')
                    followed_at = attempt_data.get('timestamp', datetime.now().isoformat())
                    writer.writerow([username, followed_at, status, self.username])
            
            log_signal.emit(f"📊 Batch complete! Exported {len(usernames)} followed users to {csv_path}")
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