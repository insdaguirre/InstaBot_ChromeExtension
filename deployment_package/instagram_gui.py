#!/usr/bin/env python3
"""
Instagram Automation GUI Application
Simple interface where you input credentials and settings directly
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
import os

# Modified Instagram bot class for GUI use
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

class InstagramBotGUI:
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
        self.follow_delay_min = 3  # Changed from 10
        self.follow_delay_max = 3  # Changed from 15
        self.page_load_delay = 3
        
        # Initialize data files
        self.follows_data = self.load_follows_data()
        self.action_log = self.load_action_log()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def load_follows_data(self):
        if self.follows_file.exists():
            try:
                with open(self.follows_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
        
    def save_follows_data(self):
        with open(self.follows_file, 'w') as f:
            json.dump(self.follows_data, f, indent=2)
            
    def load_action_log(self):
        if self.action_log_file.exists():
            try:
                with open(self.action_log_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
        
    def save_action_log(self):
        with open(self.action_log_file, 'w') as f:
            json.dump(self.action_log, f, indent=2)
            
    def log_action(self, action_type, target_user, details=""):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action_type,
            "target": target_user,
            "details": details
        }
        self.action_log.append(log_entry)
        self.save_action_log()
        
    def init_driver(self, show_browser=False):
        try:
            options = Options()
            
            # Better anti-detection options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Add headless mode unless showing browser
            if not show_browser:
                options.add_argument('--headless')
            
            # Disable automation detection
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=options)
            
            # Remove automation indicators
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver.implicitly_wait(10)
            mode = "visible" if show_browser else "headless"
            self.logger.info(f"Chrome driver initialized successfully in {mode} mode")
            return True
        except Exception as e:
            self.logger.error(f"Error initializing driver: {str(e)}")
            return False

    def login(self):
        try:
            self.logger.info(f"Attempting to login as {self.username}")
            
            # Try direct login page first
            self.driver.get('https://www.instagram.com/accounts/login/')
            time.sleep(self.page_load_delay)
            
            # Check if we got redirected to main page
            if '/accounts/login' not in self.driver.current_url:
                self.logger.info("Redirected to main page, adjusting selectors...")
                main_page = True
            else:
                main_page = False
            
            # Wait for and fill username with appropriate selectors
            self.logger.info("Waiting for username field...")
            try:
                if main_page:
                    username_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Phone number, username, or email']"))
                    )
                else:
                    username_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.NAME, "username"))
                    )
            except TimeoutException:
                # If first attempt fails, try alternate selector
                username_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username'], input[aria-label='Phone number, username, or email']"))
                )
            
            username_input.clear()
            username_input.send_keys(self.username)
            time.sleep(1)
            
            # Fill password with appropriate selectors
            self.logger.info("Filling password...")
            try:
                if main_page:
                    password_input = self.driver.find_element(By.CSS_SELECTOR, "input[aria-label='Password']")
                else:
                    password_input = self.driver.find_element(By.NAME, "password")
            except:
                # Fallback to combined selector
                password_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='password'], input[aria-label='Password']")
            
            password_input.clear()
            password_input.send_keys(self.password)
            time.sleep(1)
            
            # Click login button with appropriate selector
            self.logger.info("Clicking login button...")
            try:
                if main_page:
                    login_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in')]"))
                    )
                else:
                    login_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
                    )
            except:
                # Fallback to any submit button
                login_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], form button"))
                )
            
            login_button.click()
            
            # Wait for login to process
            time.sleep(8)
            
            # Handle post-login dialogs
            try:
                not_now_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                )
                not_now_button.click()
                time.sleep(2)
            except:
                self.logger.debug("No 'Save Login Info' dialog found")
            
            # Check if we're still on login page (failed login)
            current_url = self.driver.current_url.lower()
            if "login" in current_url:
                self.logger.error("Still on login page - login failed")
                return False
            
            # Final verification - check if we're on Instagram home page
            if "instagram.com" in current_url and "login" not in current_url:
                self.logger.info("✅ Login completed successfully!")
                return True
            else:
                self.logger.error(f"Unexpected page after login: {current_url}")
                return False

        except TimeoutException:
            self.logger.error("Timeout waiting for login elements")
            return False
        except Exception as e:
            self.logger.error(f"Login failed with error: {str(e)}")
            return False
    


    def follow_users_from_account(self, account):
        try:
            self.logger.info(f"🎯 Navigating to account: {account}")
            self.driver.get(f"https://www.instagram.com/{account}/")
            
            # Check if account exists and is accessible
            page_source = self.driver.page_source.lower()
            if "sorry, this page isn't available" in page_source or "user not found" in page_source:
                self.logger.error(f"❌ Account {account} not found or not accessible")
                return []
            if "this account is private" in page_source:
                self.logger.error(f"❌ Account {account} is private")
                return []
            
            # Open followers modal
            try:
                followers_link = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/followers/') or contains(text(), 'followers') or contains(@title, 'followers')]"))
                        )
            self.driver.execute_script("arguments[0].click();", followers_link)
            except Exception as e:
                self.logger.error(f"❌ Could not open followers modal: {e}")
                return []
            
            # Wait for modal
            try:
                modal = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
                )
            except Exception as e:
                self.logger.error(f"❌ Followers modal failed to load: {e}")
                return []
            
            followed_count = 0
            followed_usernames = []
            processed_usernames = set()
            max_scrolls = 100
            scroll_attempts = 0
            
            while followed_count < self.users_per_account and scroll_attempts < max_scrolls:
                # Find all visible follow buttons and their usernames
                follow_buttons = self.driver.find_elements(By.XPATH, "//button[.//div[text()='Follow']]")
                if not follow_buttons:
                    break  # No more follow buttons, stop
                found_new = False
                        for button in follow_buttons:
                                try:
                                    parent = button.find_element(By.XPATH, "./ancestor::div[contains(@style, 'display: flex') or contains(@class, 'x1dm5mii')]")
                                    username_link = parent.find_element(By.XPATH, ".//a[contains(@href, '/') and not(contains(@href, '/followers/')) and not(contains(@href, '/following/'))]")
                        username = username_link.get_attribute('href').split('/')[-2]
                        if not username or username in processed_usernames or username in self.follows_data:
                                        continue
                        # Wait 1 second before each follow click
                                    time.sleep(1)
                        # Click follow
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                                    try:
                                        button.click()
                        except Exception:
                                        try:
                                            self.driver.execute_script("arguments[0].click();", button)
                            except Exception:
                                            actions = webdriver.ActionChains(self.driver)
                                            actions.move_to_element(button).click().perform()
                        # Assume follow is always successful
                        self.logger.info(f"✅ Followed @{username} ({followed_count + 1})")
                                            self.follows_data[username] = {
                                                'status': 'following',
                                                'followed_at': datetime.now().isoformat(),
                                                'source_account': account
                                            }
                                            self.log_action('follow', username, f'From {account}')
                        followed_usernames.append(username)
                        followed_count += 1
                        processed_usernames.add(username)
                        found_new = True
                        if followed_count >= self.users_per_account:
                            break
                    except Exception:
                                    continue
                if followed_count >= self.users_per_account:
                                break
                # Always scroll after each pass, then re-query for buttons
                modal_element = self.driver.find_element(By.XPATH, "//div[@role='dialog']")
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;", modal_element)
                    scroll_attempts += 1
            self.save_follows_data()
            self.logger.info(f"🎉 Completed following from @{account}: {followed_count} users followed.")
            return followed_usernames
        except Exception as e:
            self.logger.error(f"❌ Failed to follow users from {account}: {str(e)}")
            return []

    def unfollow_user(self, username):
        """Unfollow a specific user"""
        try:
            self.logger.info(f"🔄 Attempting to unfollow @{username}")
            
            # Navigate to user's profile
            self.driver.get(f"https://www.instagram.com/{username}/")
            time.sleep(self.page_load_delay)
            
            # Check if page exists
            if "Sorry, this page isn't available" in self.driver.page_source:
                self.logger.error(f"❌ Profile {username} doesn't exist")
                return False
            
            # Find the "Following" button using the HTML structure you provided
            try:
                # Look for button with "Following" text
                following_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[.//div[contains(text(), 'Following')]]"))
                )
                
                # Click the Following button to open dropdown
                self.logger.info(f"📋 Clicking Following button for @{username}")
                following_button.click()
                time.sleep(2)
                
                # Now find and click the "Unfollow" button in the dropdown
                unfollow_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Unfollow')]"))
                )
                
                self.logger.info(f"🎯 Clicking Unfollow button for @{username}")
                unfollow_button.click()
                time.sleep(2)
                
                # Update the follows data
                if username in self.follows_data:
                    self.follows_data[username]['status'] = 'unfollowed'
                    self.follows_data[username]['unfollowed_at'] = datetime.now().isoformat()
                    self.save_follows_data()
                
                self.log_action('unfollow', username, 'Unfollowed user successfully')
                self.logger.info(f"✅ Successfully unfollowed @{username}")
                return True
                
            except TimeoutException:
                # Maybe we're not following this user
                self.logger.warning(f"⚠️ Could not find Following button for @{username} - may not be following them")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error unfollowing {username}: {str(e)}")
            return False

    def unfollow_old_users(self, hours_threshold=48):
        """Unfollow users followed more than X hours ago"""
        try:
            current_time = datetime.now()
            users_to_unfollow = []
            
            # Find users eligible for unfollowing
            for username, data in self.follows_data.items():
                if data.get('status') != 'following':
                    continue
                    
                followed_time = datetime.fromisoformat(data['followed_at'])
                hours_passed = (current_time - followed_time).total_seconds() / 3600
                
                if hours_passed >= hours_threshold:
                    users_to_unfollow.append(username)
            
            self.logger.info(f"🕒 Found {len(users_to_unfollow)} users eligible for unfollowing (>{hours_threshold}h old)")
            
            # Unfollow eligible users
            unfollowed_count = 0
            for username in users_to_unfollow:
                if self.unfollow_user(username):
                    unfollowed_count += 1
                    # Small delay between unfollows
                    time.sleep(random.randint(3, 8))
                
            self.logger.info(f"🔄 Unfollowed {unfollowed_count} users")
            return unfollowed_count
            
        except Exception as e:
            self.logger.error(f"❌ Error in unfollow process: {str(e)}")
            return 0

    def test_unfollow_recent_user(self):
        """Test function: unfollow the most recently followed user (ignoring 48h rule)"""
        try:
            # Find the most recently followed user
            recent_follows = [
                (username, data) for username, data in self.follows_data.items()
                if data.get('status') == 'following'
            ]
            
            if not recent_follows:
                self.logger.info("❌ No users currently being followed")
                return False
            
            # Sort by followed_at timestamp to get most recent
            recent_follows.sort(key=lambda x: x[1]['followed_at'], reverse=True)
            most_recent_user = recent_follows[0][0]
            
            self.logger.info(f"🧪 TEST MODE: Unfollowing most recent user @{most_recent_user}")
            return self.unfollow_user(most_recent_user)
            
        except Exception as e:
            self.logger.error(f"❌ Error in test unfollow: {str(e)}")
            return False

class InstagramAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Automation Tool")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        self.bot = None
        self.automation_running = False
        self.automation_thread = None
        
        self.data_dir = Path('instagram_data')
        self.data_dir.mkdir(exist_ok=True)
        
        self.setup_logging()
        self.create_gui()
        self.update_stats()
        
    def setup_logging(self):
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        
        log_file = logs_dir / f'automation_{datetime.now().strftime("%Y%m%d")}.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def create_gui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Login Tab
        self.login_frame = ttk.Frame(notebook)
        notebook.add(self.login_frame, text="Login & Settings")
        self.create_login_tab()
        
        # Control Tab
        self.control_frame = ttk.Frame(notebook)
        notebook.add(self.control_frame, text="Control")
        self.create_control_tab()
        
        # Stats Tab
        self.stats_frame = ttk.Frame(notebook)
        notebook.add(self.stats_frame, text="Statistics")
        self.create_stats_tab()
        
    def create_login_tab(self):
        main_frame = ttk.Frame(self.login_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Credentials
        cred_frame = ttk.LabelFrame(main_frame, text="Instagram Credentials", padding=15)
        cred_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(cred_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(cred_frame, textvariable=self.username_var, width=30).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        ttk.Label(cred_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(cred_frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Show password checkbox
        self.show_password_var = tk.BooleanVar()
        show_password_cb = ttk.Checkbutton(cred_frame, text="Show Password", 
                                         variable=self.show_password_var, 
                                         command=self.toggle_password_visibility)
        show_password_cb.grid(row=1, column=2, sticky="w", padx=(10, 0), pady=5)
        
        # Settings
        settings_frame = ttk.LabelFrame(main_frame, text="Automation Settings", padding=15)
        settings_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(settings_frame, text="Target Accounts:").grid(row=0, column=0, sticky="w", pady=5)
        self.target_accounts_var = tk.StringVar(value="deadmau5,skrillex")
        ttk.Entry(settings_frame, textvariable=self.target_accounts_var, width=50).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        ttk.Label(settings_frame, text="Users per Account:").grid(row=1, column=0, sticky="w", pady=5)
        self.users_per_account_var = tk.StringVar(value="5")
        ttk.Entry(settings_frame, textvariable=self.users_per_account_var, width=10).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Test button
        test_frame = ttk.Frame(main_frame)
        test_frame.pack(fill="x", pady=10)
        
        ttk.Button(test_frame, text="Test Connection", command=self.test_connection).pack(side="left")
        
        # Show browser checkbox for testing
        self.show_browser_var = tk.BooleanVar(value=True)  # Default to checked for easier debugging
        ttk.Checkbutton(test_frame, text="Show Browser", 
                       variable=self.show_browser_var).pack(side="left", padx=(10, 0))
        
        self.connection_status_var = tk.StringVar(value="Not tested")
        ttk.Label(test_frame, textvariable=self.connection_status_var).pack(side="left", padx=(20, 0))
        
    def create_control_tab(self):
        main_frame = ttk.Frame(self.control_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Control buttons
        control_frame = ttk.LabelFrame(main_frame, text="Automation Control", padding=15)
        control_frame.pack(fill="x", pady=(0, 20))
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill="x")
        
        self.start_button = ttk.Button(button_frame, text="Start Automation", command=self.start_automation)
        self.start_button.pack(side="left", padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Automation", command=self.stop_automation, state="disabled")
        self.stop_button.pack(side="left", padx=(0, 10))
        
        # Test unfollow button
        self.test_unfollow_button = ttk.Button(button_frame, text="🧪 Test Unfollow", command=self.test_unfollow_functionality)
        self.test_unfollow_button.pack(side="left", padx=(0, 10))
        
        self.status_var = tk.StringVar(value="Stopped")
        ttk.Label(button_frame, textvariable=self.status_var, font=("Arial", 12, "bold")).pack(side="right")
        
        # Status display
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=15)
        status_frame.pack(fill="both", expand=True)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=15, wrap=tk.WORD)
        self.status_text.pack(fill="both", expand=True)
        
        self.add_status_message("Instagram Automation Ready")
        
    def test_unfollow_functionality(self):
        """Test the unfollow functionality on the most recently followed user"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        self.add_status_message("🧪 Starting unfollow test...")
        
        def test_unfollow_thread():
            try:
                # Create test bot instance
                test_bot = InstagramBotGUI(username, password, [], 1)
                
                show_browser = self.show_browser_var.get()
                self.root.after(0, lambda: self.add_status_message(f"🌐 Initializing Chrome for unfollow test..."))
                
                if test_bot.init_driver(show_browser=show_browser):
                    if test_bot.login():
                        self.root.after(0, lambda: self.add_status_message("✅ Logged in, testing unfollow functionality..."))
                        
                        # Test the unfollow on most recent user
                        if test_bot.test_unfollow_recent_user():
                            self.root.after(0, lambda: self.add_status_message("✅ Unfollow test successful!"))
                        else:
                            self.root.after(0, lambda: self.add_status_message("⚠️ Unfollow test failed - check logs for details"))
                    else:
                        self.root.after(0, lambda: self.add_status_message("❌ Login failed for unfollow test"))
                else:
                    self.root.after(0, lambda: self.add_status_message("❌ Chrome driver failed for unfollow test"))
                    
                # Clean up
                if test_bot.driver:
                    test_bot.driver.quit()
                    self.root.after(0, lambda: self.add_status_message("🧹 Unfollow test complete, browser closed"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.add_status_message(f"❌ Unfollow test error: {str(e)}"))
        
        threading.Thread(target=test_unfollow_thread, daemon=True).start()
        
    def create_stats_tab(self):
        main_frame = ttk.Frame(self.stats_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding=15)
        stats_frame.pack(fill="x", pady=(0, 20))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill="x")
        
        ttk.Label(stats_grid, text="Following:").grid(row=0, column=0, sticky="w", pady=2)
        self.following_var = tk.StringVar(value="0")
        ttk.Label(stats_grid, textvariable=self.following_var, font=("Arial", 10, "bold")).grid(row=0, column=1, sticky="w", padx=(20, 0), pady=2)
        
        ttk.Label(stats_grid, text="Today's Follows:").grid(row=1, column=0, sticky="w", pady=2)
        self.today_follows_var = tk.StringVar(value="0")
        ttk.Label(stats_grid, textvariable=self.today_follows_var, font=("Arial", 10, "bold")).grid(row=1, column=1, sticky="w", padx=(20, 0), pady=2)
        
        activity_frame = ttk.LabelFrame(main_frame, text="Recent Activity", padding=15)
        activity_frame.pack(fill="both", expand=True)
        
        self.activity_listbox = tk.Listbox(activity_frame)
        activity_scrollbar = ttk.Scrollbar(activity_frame, orient="vertical", command=self.activity_listbox.yview)
        self.activity_listbox.configure(yscrollcommand=activity_scrollbar.set)
        
        self.activity_listbox.pack(side="left", fill="both", expand=True)
        activity_scrollbar.pack(side="right", fill="y")
        
    def test_connection(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        self.connection_status_var.set("Testing...")
        
        def test_thread():
            try:
                self.root.after(0, lambda: self.add_status_message("🧪 Starting connection test..."))
                test_bot = InstagramBotGUI(username, password, [], 1)
                
                show_browser = self.show_browser_var.get()
                browser_mode = "visible" if show_browser else "headless"
                self.root.after(0, lambda: self.add_status_message(f"🌐 Initializing Chrome browser ({browser_mode})..."))
                if test_bot.init_driver(show_browser=show_browser):
                    self.root.after(0, lambda: self.add_status_message("🔑 Attempting to login to Instagram..."))
                    if test_bot.login():
                        self.root.after(0, lambda: self.connection_status_var.set("✅ Success!"))
                        self.root.after(0, lambda: self.add_status_message("✅ Connection test successful! Instagram login worked."))
                    else:
                        self.root.after(0, lambda: self.connection_status_var.set("❌ Login failed"))
                        self.root.after(0, lambda: self.add_status_message("❌ Login failed - check username/password"))
                else:
                    self.root.after(0, lambda: self.connection_status_var.set("❌ Driver failed"))
                    self.root.after(0, lambda: self.add_status_message("❌ Chrome driver failed to initialize"))
                    
                # Always clean up the driver
                if test_bot.driver:
                    test_bot.driver.quit()
                    self.root.after(0, lambda: self.add_status_message("🧹 Browser closed, test complete"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.connection_status_var.set(f"❌ Error"))
                self.root.after(0, lambda: self.add_status_message(f"❌ Test error: {str(e)}"))
        
        threading.Thread(target=test_thread, daemon=True).start()
        
    def toggle_password_visibility(self):
        """Toggle password visibility in the password entry field"""
        if self.show_password_var.get():
            self.password_entry.configure(show='')  # Show password
        else:
            self.password_entry.configure(show='*')  # Hide password
        
    def start_automation(self):
        if not self.validate_inputs():
            return
            
        self.automation_running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_var.set("Starting...")
        
        self.automation_thread = threading.Thread(target=self.run_automation, daemon=True)
        self.automation_thread.start()
        
        self.add_status_message("Automation started")
        
    def stop_automation(self):
        self.automation_running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_var.set("Stopping...")
        
        if self.bot and self.bot.driver:
            try:
                self.bot.driver.quit()
            except:
                pass
                
        self.status_var.set("Stopped")
        self.add_status_message("Automation stopped")
        
    def validate_inputs(self):
        if not self.username_var.get().strip():
            messagebox.showerror("Error", "Please enter Instagram username")
            return False
            
        if not self.password_var.get().strip():
            messagebox.showerror("Error", "Please enter Instagram password")
            return False
            
        if not self.target_accounts_var.get().strip():
            messagebox.showerror("Error", "Please enter target accounts")
            return False
            
        try:
            int(self.users_per_account_var.get())
        except ValueError:
            messagebox.showerror("Error", "Users per account must be a number")
            return False
            
        return True
        
    def run_automation(self):
        try:
            username = self.username_var.get().strip()
            password = self.password_var.get().strip()
            target_accounts = [acc.strip() for acc in self.target_accounts_var.get().split(',')]
            users_per_account = int(self.users_per_account_var.get())
            
            self.bot = InstagramBotGUI(username, password, target_accounts, users_per_account)
            
            self.root.after(0, lambda: self.status_var.set("Initializing..."))
            self.root.after(0, lambda: self.add_status_message("Initializing bot"))
            
            # Use show browser setting for automation too
            show_browser = self.show_browser_var.get()
            if not self.bot.init_driver(show_browser=show_browser):
                raise Exception("Failed to initialize Chrome driver")
                
            if not self.bot.login():
                raise Exception("Failed to login to Instagram")
                
            self.root.after(0, lambda: self.status_var.set("Running"))
            self.root.after(0, lambda: self.add_status_message("Bot logged in, starting automation"))
            
            # First, unfollow users that are 48+ hours old
            self.root.after(0, lambda: self.add_status_message("🕒 Checking for users to unfollow (48+ hours old)"))
            unfollowed_count = self.bot.unfollow_old_users(hours_threshold=48)
            if unfollowed_count > 0:
                self.root.after(0, lambda: self.add_status_message(f"🔄 Unfollowed {unfollowed_count} old users"))
            else:
                self.root.after(0, lambda: self.add_status_message("📋 No users ready for unfollowing yet"))
            
            # Follow users from each target account
            total_follows = 0
            successful_accounts = 0
            
            for i, account in enumerate(target_accounts):
                if not self.automation_running:
                    break
                    
                self.root.after(0, lambda a=account, idx=i+1, total=len(target_accounts): 
                    self.add_status_message(f"🎯 [{idx}/{total}] Starting to follow users from @{a}"))
                
                try:
                    follows = self.bot.follow_users_from_account(account)
                    total_follows += len(follows)
                    
                    if len(follows) > 0:
                        successful_accounts += 1
                        self.root.after(0, lambda f=len(follows), a=account: 
                            self.add_status_message(f"✅ Followed {f} users from @{a}"))
                    else:
                        self.root.after(0, lambda a=account: 
                            self.add_status_message(f"⚠️ No users followed from @{a} (account private, no followers, or error)"))
                
                except Exception as e:
                    self.root.after(0, lambda a=account, err=str(e): 
                        self.add_status_message(f"❌ Error with @{a}: {err}"))
                
                # Wait between accounts (except for the last one)
                if self.automation_running and i < len(target_accounts) - 1:
                    self.root.after(0, lambda: self.add_status_message(f"⏳ Waiting 60 seconds before next account..."))
                    for wait_time in range(60):
                        if not self.automation_running:
                            break
                        time.sleep(1)
                    
            # Final summary
            self.root.after(0, lambda: self.add_status_message(
                f"🎉 Automation completed! Total follows: {total_follows} from {successful_accounts}/{len(target_accounts)} accounts"))
                    
        except Exception as e:
            self.root.after(0, lambda: self.add_status_message(f"Automation error: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("Error"))
        finally:
            if self.bot and self.bot.driver:
                try:
                    self.bot.driver.quit()
                except:
                    pass
            self.automation_running = False
            self.root.after(0, lambda: self.start_button.configure(state="normal"))
            self.root.after(0, lambda: self.stop_button.configure(state="disabled"))
            if self.status_var.get() != "Error":
                self.root.after(0, lambda: self.status_var.set("Stopped"))
                
    def add_status_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.logger.info(message)
        
    def update_stats(self):
        try:
            follows_file = self.data_dir / 'follows.json'
            action_log_file = self.data_dir / 'action_log.json'
            
            follows_data = {}
            action_log = []
            
            if follows_file.exists():
                with open(follows_file, 'r') as f:
                    follows_data = json.load(f)
                    
            if action_log_file.exists():
                with open(action_log_file, 'r') as f:
                    action_log = json.load(f)
            
            now = datetime.now()
            today = now.date()
            
            following = [u for u, d in follows_data.items() if d.get('status') == 'following']
            
            today_follows = len([
                a for a in action_log 
                if a.get('action') == 'follow' 
                and datetime.fromisoformat(a['timestamp']).date() == today
            ])
            
            self.following_var.set(str(len(following)))
            self.today_follows_var.set(str(today_follows))
            
            # Update activity
            self.activity_listbox.delete(0, tk.END)
            for action in action_log[-15:]:
                timestamp = datetime.fromisoformat(action['timestamp']).strftime("%H:%M")
                text = f"[{timestamp}] {action['action'].title()}: {action['target']}"
                self.activity_listbox.insert(tk.END, text)
            
        except Exception as e:
            pass
            
        self.root.after(5000, self.update_stats)

def main():
    root = tk.Tk()
    
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except:
        pass
    
    app = InstagramAutomationGUI(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (800 // 2)
    y = (root.winfo_screenheight() // 2) - (600 // 2)
    root.geometry(f"800x600+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main() 