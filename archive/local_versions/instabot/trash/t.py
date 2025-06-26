import sys
import time
import random
import platform
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QSpinBox, QTabWidget, QMessageBox,
                            QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from worker import InstagramWorker, setup_driver
import concurrent.futures
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Add user agent to appear more like a real browser
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        # Use local ChromeDriver
        service = Service("./chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"Error setting up ChromeDriver: {str(e)}")
        raise

def login_to_instagram(driver, username, password):
    try:
        # Navigate to Instagram login page
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(5)  # Wait for page to load
        
        # Find username and password fields
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_input = driver.find_element(By.NAME, "password")
        
        # Enter credentials
        username_input.clear()
        username_input.send_keys(username)
        password_input.clear()
        password_input.send_keys(password)
        
        # Click login button
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Wait for login to complete
        time.sleep(5)
        
        # Check if login was successful
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Search')]"))
            )
            logger.info("Successfully logged in")
            return True
        except:
            logger.error("Login verification failed")
            return False
            
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return False

def check_and_handle_login(driver, username, password):
    try:
        # Check if we're on a login page or if session expired
        if "login" in driver.current_url or "accounts/login" in driver.current_url:
            logger.info("Session expired, attempting to re-login")
            return login_to_instagram(driver, username, password)
        return True
    except Exception as e:
        logger.error(f"Error checking login status: {str(e)}")
        return False

def parse_follower_count(count_str):
    try:
        # Remove commas and convert to lowercase
        count_str = count_str.replace(',', '').lower()
        
        # Handle different formats (K, M, B)
        if 'k' in count_str:
            return int(float(count_str.replace('k', '')) * 1000)
        elif 'm' in count_str:
            return int(float(count_str.replace('m', '')) * 1000000)
        elif 'b' in count_str:
            return int(float(count_str.replace('b', '')) * 1000000000)
        else:
            return int(count_str)
    except:
        return 0

def get_followers(driver, username, target_username, max_followers):
    try:
        # Navigate to the target profile
        profile_url = f"https://www.instagram.com/{target_username}/"
        driver.get(profile_url)
        time.sleep(3)  # Wait for page to load
        
        # Check if we need to re-login
        if not check_and_handle_login(driver, username, "b@seb@ll"):
            logger.error("Failed to maintain login session")
            return []
        
        # Click on followers link
        followers_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/followers')]"))
        )
        followers_count = parse_follower_count(followers_link.text.split()[0])
        logger.info(f"Found {followers_count} followers for {target_username}")
        
        followers_link.click()
        time.sleep(2)  # Wait for followers modal to load
        
        # Scroll through followers
        followers_modal = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
        )
        
        followers = []
        last_height = driver.execute_script("return arguments[0].scrollHeight", followers_modal)
        
        while len(followers) < min(max_followers, followers_count):
            # Get follower usernames
            follower_elements = followers_modal.find_elements(By.XPATH, ".//a[@role='link']")
            for element in follower_elements:
                href = element.get_attribute('href')
                if href and '/p/' not in href and href not in followers:
                    username = href.split('/')[-2]
                    if username != target_username:
                        followers.append(username)
                        if len(followers) >= max_followers:
                            break
            
            # Scroll down
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_modal)
            time.sleep(2)  # Wait for content to load
            
            # Check if we've reached the bottom
            new_height = driver.execute_script("return arguments[0].scrollHeight", followers_modal)
            if new_height == last_height:
                break
            last_height = new_height
            
            # Check if we need to re-login
            if not check_and_handle_login(driver, username, "b@seb@ll"):
                logger.error("Failed to maintain login session during scrolling")
                break
        
        logger.info(f"Successfully scraped {len(followers)} followers from {target_username}")
        return followers
        
    except Exception as e:
        logger.error(f"Error getting followers: {str(e)}")
        return []

def scrape_followers_parallel(target_usernames, max_followers=100, max_workers=6):
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_username = {
            executor.submit(scrape_single_account, username, max_followers): username 
            for username in target_usernames
        }
        
        for future in concurrent.futures.as_completed(future_to_username):
            username = future_to_username[future]
            try:
                followers = future.result()
                results[username] = followers
            except Exception as e:
                logger.error(f"Error scraping {username}: {str(e)}")
                results[username] = []
    
    return results

def scrape_single_account(target_username, max_followers):
    driver = None
    try:
        driver = setup_driver()
        username = "deegz.mp3"  # Your Instagram username
        password = "b@seb@ll"   # Your Instagram password
        
        if not login_to_instagram(driver, username, password):
            raise Exception("Failed to login")
        
        followers = get_followers(driver, username, target_username, max_followers)
        return followers
        
    except Exception as e:
        logger.error(f"Error in scrape_single_account: {str(e)}")
        raise
    finally:
        if driver:
            driver.quit()

def verify_follow_status(driver, username_to_follow):
    try:
        # Navigate to the user's profile
        profile_url = f"https://www.instagram.com/{username_to_follow}/"
        driver.get(profile_url)
        time.sleep(random.uniform(3, 5))
        
        # Check if we need to re-login
        if not check_and_handle_login(driver, "deegz.mp3", "b@seb@ll"):
            return False
            
        # Find the follow button
        follow_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Following') or contains(text(), 'Follow')]"))
        )
        
        return follow_button.text == "Following"
    except Exception as e:
        logger.error(f"Error verifying follow status for {username_to_follow}: {str(e)}")
        return False

def check_rate_limit(driver):
    try:
        # Check for rate limit messages
        page_source = driver.page_source.lower()
        rate_limit_indicators = [
            "please wait a few minutes",
            "try again later",
            "too many requests",
            "rate limit",
            "temporary block"
        ]
        
        for indicator in rate_limit_indicators:
            if indicator in page_source:
                logger.warning(f"Rate limit detected: {indicator}")
                return True
        return False
    except:
        return False

def follow_user(driver, username_to_follow):
    try:
        # Navigate to the user's profile
        profile_url = f"https://www.instagram.com/{username_to_follow}/"
        driver.get(profile_url)
        time.sleep(5)  # Wait for page to load
        
        # Find and click the follow button
        follow_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[text()='Follow' or @type='button']"))
        )
        
        # Check if already following
        if "Following" in follow_button.text:
            logger.info(f"Already following {username_to_follow}")
            return True
            
        # Click follow button
        follow_button.click()
        time.sleep(3)
        
        logger.info(f"Successfully followed {username_to_follow}")
        return True
        
    except Exception as e:
        logger.error(f"Error following {username_to_follow}: {str(e)}")
        return False

def follow_users_parallel(usernames_to_follow, max_workers=6):
    driver = None
    try:
        driver = setup_driver()
        username = "deegz.mp3"  # Your Instagram username
        password = "b@seb@ll"   # Your Instagram password
        
        if not login_to_instagram(driver, username, password):
            raise Exception("Failed to login")
        
        results = []
        for username_to_follow in usernames_to_follow:
            success = follow_user(driver, username_to_follow)
            results.append((username_to_follow, success))
            time.sleep(random.uniform(2, 4))  # Random delay between follows
            
        return results
        
    except Exception as e:
        logger.error(f"Error in follow_users_parallel: {str(e)}")
        raise
    finally:
        if driver:
            driver.quit()

def print_progress(current, total, prefix=''):
    bar_length = 50
    filled_length = int(round(bar_length * current / float(total)))
    percents = round(100.0 * current / float(total), 1)
    bar = '=' * filled_length + '-' * (bar_length - filled_length)
    print(f'\r{prefix}[{bar}] {percents}% ({current}/{total})', end='')
    if current == total:
        print()

def main():
    driver = setup_driver()
    username = "deegz.mp3"
    password = "b@seb@ll"

    print("Starting Instagram automation...")
    print("1. Logging in...")
    
    if not login_to_instagram(driver, username, password):
        print("Failed to login. Exiting...")
        driver.quit()
        return

    print("2. Successfully logged in!")
    
    # Test with a single user first
    test_user = "zuck"
    print(f"\nTesting follow functionality with {test_user}...")
    
    if follow_user(driver, test_user):
        print(f"Successfully followed {test_user}")
    else:
        print(f"Failed to follow {test_user}")
    
    driver.quit()
    print("\nTest completed.")

if __name__ == "__main__":
    main()

class FollowerScraper(QThread):
    progress = pyqtSignal(str)
    followers_found = pyqtSignal(list)
    finished = pyqtSignal()
    progress_update = pyqtSignal(int)
    
    def __init__(self, username, password, target_account, max_followers):
        super().__init__()
        self.username = username
        self.password = password
        self.target_account = target_account
        self.max_followers = max_followers
        self.is_running = True
        self.executor = ThreadPoolExecutor(max_workers=6)  # Use 6 CPU cores
        logger.debug(f"FollowerScraper initialized for account: {target_account}")

    def wait_for_element(self, driver, by, value, timeout=10):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.error(f"Timeout waiting for element: {value}")
            return None

    def login(self, driver):
        try:
            logger.debug("Navigating to Instagram login page...")
            driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(5)
            
            # Wait for and fill username field
            username_field = self.wait_for_element(driver, By.NAME, 'username')
            if not username_field:
                raise Exception("Could not find username field")
            username_field.send_keys(self.username)
            
            # Wait for and fill password field
            password_field = self.wait_for_element(driver, By.NAME, 'password')
            if not password_field:
                raise Exception("Could not find password field")
            password_field.send_keys(self.password + Keys.RETURN)
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check for login errors
            error_messages = driver.find_elements(By.CLASS_NAME, 'error-container')
            if error_messages:
                error_text = error_messages[0].text
                logger.error(f"Login error detected: {error_text}")
                self.progress.emit(f"❌ Login Error: {error_text}")
                raise Exception(f"Login failed: {error_text}")
            
            logger.debug("Login successful")
            return True
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            self.progress.emit(f"❌ Login Error: {str(e)}")
            return False

    def get_followers_count(self, driver):
        try:
            # Try multiple selectors for followers count
            selectors = [
                "//a[contains(@href, '/followers')]//span",
                "//a[contains(@href, '/followers')]",
                "//li[contains(., 'followers')]//span",
                "//li[contains(., 'followers')]"
            ]
            
            for selector in selectors:
                try:
                    element = self.wait_for_element(driver, By.XPATH, selector)
                    if element:
                        text = element.text
                        # Extract numbers from text
                        count = ''.join(filter(str.isdigit, text))
                        if count:
                            return int(count)
                except:
                    continue
            
            raise Exception("Could not find followers count")
            
        except Exception as e:
            logger.error(f"Error getting followers count: {str(e)}")
            raise

    def scroll_followers_list(self, driver, dialog):
        try:
            # Scroll to bottom with a smoother scroll
            last_height = driver.execute_script("return arguments[0].scrollHeight", dialog)
            driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", dialog)
            time.sleep(2)  # Wait for content to load
            
            # Get new height
            new_height = driver.execute_script("return arguments[0].scrollHeight", dialog)
            return new_height
            
        except Exception as e:
            logger.error(f"Error scrolling followers list: {str(e)}")
            return None

    def process_follower_elements(self, elements):
        followers = []
        for element in elements:
            try:
                href = element.get_attribute('href')
                if href and '/p/' not in href:  # Exclude post links
                    username = href.split('/')[-2]
                    if username and username != self.target_account:
                        followers.append(username)
            except:
                continue
        return followers

    def run(self):
        driver = None
        try:
            logger.debug("Starting follower scraping process...")
            self.progress.emit("🔄 Initializing Chrome driver...")
            driver = setup_driver()
            
            # Login
            if not self.login(driver):
                raise Exception("Login failed")
            
            # Navigate to target account
            self.progress.emit(f"🔍 Navigating to {self.target_account}'s profile...")
            driver.get(f"https://www.instagram.com/{self.target_account}/")
            time.sleep(3)
            
            # Check if account exists
            if "Sorry, this page isn't available." in driver.page_source:
                error_msg = f"Account {self.target_account} does not exist or is private"
                logger.error(error_msg)
                self.progress.emit(f"❌ Error: {error_msg}")
                raise Exception(error_msg)
            
            # Get followers count
            followers_count = self.get_followers_count(driver)
            logger.debug(f"Found {followers_count} followers")
            self.progress.emit(f"📊 Found {followers_count} followers")
            
            # Click on followers link
            followers_link = self.wait_for_element(driver, By.XPATH, "//a[contains(@href, '/followers')]")
            if not followers_link:
                raise Exception("Could not find followers link")
            followers_link.click()
            time.sleep(3)
            
            # Wait for followers dialog
            dialog = self.wait_for_element(driver, By.XPATH, "//div[@role='dialog']")
            if not dialog:
                raise Exception("Could not find followers dialog")
            
            # Scroll and collect followers
            followers = []
            last_height = driver.execute_script("return arguments[0].scrollHeight", dialog)
            no_new_followers_count = 0
            scroll_attempts = 0
            max_scroll_attempts = 100  # Increased max scroll attempts
            
            while len(followers) < min(self.max_followers, followers_count) and self.is_running:
                try:
                    # Wait for follower elements with improved selector
                    follower_elements = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH, "//div[@role='dialog']//a[contains(@href, '/') and not(contains(@href, '/p/'))]"))
                    )
                    
                    # Process followers in parallel
                    new_followers = self.executor.submit(self.process_follower_elements, follower_elements).result()
                    
                    # Add new followers
                    for username in new_followers:
                        if username not in followers:
                            followers.append(username)
                            logger.debug(f"Found new follower: {username}")
                            self.progress.emit(f"✅ Found follower: {username}")
                            if len(followers) >= self.max_followers:
                                break
                    
                    # Update progress
                    progress_percent = int((len(followers) / min(self.max_followers, followers_count)) * 100)
                    self.progress_update.emit(progress_percent)
                    self.progress.emit(f"⏳ Progress: {len(followers)}/{min(self.max_followers, followers_count)} followers scraped ({progress_percent}%)")
                    
                    if len(new_followers) == 0:
                        no_new_followers_count += 1
                        logger.warning(f"No new followers found. Attempt {no_new_followers_count}/3")
                        if no_new_followers_count >= 3:
                            # Try one more scroll before giving up
                            new_height = self.scroll_followers_list(driver, dialog)
                            if new_height == last_height:
                                self.progress.emit("⚠️ No new followers found after multiple scrolls. Stopping...")
                                break
                            no_new_followers_count = 0
                    else:
                        no_new_followers_count = 0
                    
                    # Scroll with improved behavior
                    new_height = self.scroll_followers_list(driver, dialog)
                    if new_height == last_height:
                        scroll_attempts += 1
                        if scroll_attempts >= 3:  # Try 3 times before confirming end
                            logger.info("Reached end of followers list")
                            self.progress.emit("⚠️ Reached end of followers list")
                            break
                    else:
                        scroll_attempts = 0
                        last_height = new_height
                    
                    # Add a small delay between scrolls
                    time.sleep(2)  # Increased delay to allow more content to load
                    
                except Exception as e:
                    logger.error(f"Error during scrolling: {str(e)}")
                    self.progress.emit(f"❌ Error during scrolling: {str(e)}")
                    break
            
            if not followers:
                error_msg = "No followers were collected. This might be due to:\n1. The account is private\n2. Instagram is blocking the scraping\n3. The followers list is not accessible"
                logger.error(error_msg)
                self.progress.emit(f"❌ Error: {error_msg}")
                raise Exception("No followers were collected")
            
            logger.info(f"Successfully scraped {len(followers)} followers")
            self.progress.emit(f"✅ Successfully scraped {len(followers)} followers")
            self.followers_found.emit(followers)
            self.finished.emit()
            
        except Exception as e:
            logger.error(f"Fatal error in FollowerScraper: {str(e)}")
            self.progress.emit(f"❌ Error: {str(e)}")
            self.finished.emit()
        finally:
            if driver:
                logger.debug("Closing Chrome driver...")
                driver.quit()
            self.executor.shutdown(wait=False)

class InstagramManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Instagram Manager")
        self.setMinimumSize(800, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Create login tab
        login_tab = QWidget()
        login_layout = QVBoxLayout(login_tab)
        
        # Username
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        username_layout.addWidget(self.username_input)
        login_layout.addLayout(username_layout)
        
        # Password
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_input)
        login_layout.addLayout(password_layout)
        
        # Action selection
        action_layout = QHBoxLayout()
        action_layout.addWidget(QLabel("Action:"))
        self.follow_button = QPushButton("Follow")
        self.unfollow_button = QPushButton("Unfollow")
        action_layout.addWidget(self.follow_button)
        action_layout.addWidget(self.unfollow_button)
        login_layout.addLayout(action_layout)
        
        # Accounts to process
        login_layout.addWidget(QLabel("Accounts (one per line):"))
        self.accounts_input = QTextEdit()
        login_layout.addWidget(self.accounts_input)
        
        # Timing parameters
        timing_layout = QHBoxLayout()
        timing_layout.addWidget(QLabel("Min delay (seconds):"))
        self.min_delay = QSpinBox()
        self.min_delay.setRange(30, 300)
        self.min_delay.setValue(30)
        timing_layout.addWidget(self.min_delay)
        
        timing_layout.addWidget(QLabel("Max delay (seconds):"))
        self.max_delay = QSpinBox()
        self.max_delay.setRange(60, 600)
        self.max_delay.setValue(60)
        timing_layout.addWidget(self.max_delay)
        login_layout.addLayout(timing_layout)
        
        # Rate limiting
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(QLabel("Max per hour:"))
        self.max_per_hour = QSpinBox()
        self.max_per_hour.setRange(1, 100)
        self.max_per_hour.setValue(20)
        rate_layout.addWidget(self.max_per_hour)
        
        rate_layout.addWidget(QLabel("Max per day:"))
        self.max_per_day = QSpinBox()
        self.max_per_day.setRange(1, 500)
        self.max_per_day.setValue(100)
        rate_layout.addWidget(self.max_per_day)
        login_layout.addLayout(rate_layout)
        
        # Start button
        self.start_button = QPushButton("Start")
        login_layout.addWidget(self.start_button)
        
        # Progress log
        login_layout.addWidget(QLabel("Progress:"))
        self.progress_log = QTextEdit()
        self.progress_log.setReadOnly(True)
        login_layout.addWidget(self.progress_log)
        
        tabs.addTab(login_tab, "Follow/Unfollow")
        
        # Create follower scraper tab
        scraper_tab = QWidget()
        scraper_layout = QVBoxLayout(scraper_tab)
        
        # Target account
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target Account:"))
        self.target_account_input = QLineEdit()
        target_layout.addWidget(self.target_account_input)
        scraper_layout.addLayout(target_layout)
        
        # Number of followers to scrape
        followers_layout = QHBoxLayout()
        followers_layout.addWidget(QLabel("Number of followers to scrape:"))
        self.max_followers = QSpinBox()
        self.max_followers.setRange(1, 1000)
        self.max_followers.setValue(100)
        followers_layout.addWidget(self.max_followers)
        scraper_layout.addLayout(followers_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        scraper_layout.addWidget(self.progress_bar)
        
        # Scrape button
        self.scrape_button = QPushButton("Scrape Followers")
        scraper_layout.addWidget(self.scrape_button)
        
        # Scraped followers list
        scraper_layout.addWidget(QLabel("Scraped Followers:"))
        self.scraped_followers = QTextEdit()
        self.scraped_followers.setReadOnly(True)
        scraper_layout.addWidget(self.scraped_followers)
        
        # Use scraped followers button
        self.use_followers_button = QPushButton("Use These Followers")
        scraper_layout.addWidget(self.use_followers_button)
        
        # Scraper progress log
        scraper_layout.addWidget(QLabel("Scraper Progress:"))
        self.scraper_progress = QTextEdit()
        self.scraper_progress.setReadOnly(True)
        scraper_layout.addWidget(self.scraper_progress)
        
        tabs.addTab(scraper_tab, "Follower Scraper")
        
        # Connect signals
        self.follow_button.clicked.connect(lambda: self.start_action('follow'))
        self.unfollow_button.clicked.connect(lambda: self.start_action('unfollow'))
        self.scrape_button.clicked.connect(self.start_scraping)
        self.use_followers_button.clicked.connect(self.use_scraped_followers)
        
        self.worker = None
        self.scraper = None

    def start_action(self, action_type):
        if not self.username_input.text() or not self.password_input.text():
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return
            
        accounts = [acc.strip() for acc in self.accounts_input.toPlainText().split('\n') if acc.strip()]
        if not accounts:
            QMessageBox.warning(self, "Error", "Please enter at least one account")
            return
            
        self.worker = InstagramWorker(
            self.username_input.text(),
            self.password_input.text(),
            accounts,
            action_type,
            self.min_delay.value(),
            self.max_delay.value(),
            self.max_per_hour.value(),
            self.max_per_day.value()
        )
        
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.action_finished)
        self.worker.start()
        
        self.start_button.setEnabled(False)
        self.follow_button.setEnabled(False)
        self.unfollow_button.setEnabled(False)

    def start_scraping(self):
        if not self.username_input.text() or not self.password_input.text():
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return
            
        target_account = self.target_account_input.text().strip()
        if not target_account:
            QMessageBox.warning(self, "Error", "Please enter a target account")
            return
            
        # Reset progress
        self.progress_bar.setValue(0)
        self.scraped_followers.clear()
        self.scraper_progress.clear()
        
        self.scraper = FollowerScraper(
            self.username_input.text(),
            self.password_input.text(),
            target_account,
            self.max_followers.value()
        )
        
        self.scraper.progress.connect(self.update_scraper_progress)
        self.scraper.followers_found.connect(self.handle_scraped_followers)
        self.scraper.finished.connect(self.scraping_finished)
        self.scraper.progress_update.connect(self.update_progress_bar)
        self.scraper.start()
        
        self.scrape_button.setEnabled(False)

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def handle_scraped_followers(self, followers):
        self.scraped_followers.setPlainText('\n'.join(followers))
        self.progress_bar.setValue(100)  # Ensure progress bar shows completion

    def use_scraped_followers(self):
        followers = self.scraped_followers.toPlainText().strip()
        if followers:
            self.accounts_input.setPlainText(followers)
            follower_count = len(followers.splitlines())
            QMessageBox.information(self, "Success", f"Successfully copied {follower_count} followers to follow/unfollow list")
        else:
            QMessageBox.warning(self, "Warning", "No followers to copy. Please scrape followers first.")

    def update_progress(self, message):
        self.progress_log.append(message)

    def update_scraper_progress(self, message):
        self.scraper_progress.append(message)
        # Auto-scroll to bottom
        self.scraper_progress.verticalScrollBar().setValue(
            self.scraper_progress.verticalScrollBar().maximum()
        )

    def action_finished(self):
        self.start_button.setEnabled(True)
        self.follow_button.setEnabled(True)
        self.unfollow_button.setEnabled(True)
        if self.worker:
            self.worker.is_running = False

    def scraping_finished(self):
        self.scrape_button.setEnabled(True)
        if self.scraper:
            self.scraper.is_running = False
        # Show completion message
        QMessageBox.information(self, "Complete", "Follower scraping completed!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InstagramManager()
    window.show()
    sys.exit(app.exec_()) 