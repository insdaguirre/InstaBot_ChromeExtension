import sys
import time
import random
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
from webdriver_manager.chrome import ChromeDriverManager

class FollowerScraper(QThread):
    progress = pyqtSignal(str)
    followers_found = pyqtSignal(list)
    finished = pyqtSignal()
    progress_update = pyqtSignal(int)  # For progress bar
    
    def __init__(self, username, password, target_account, max_followers):
        super().__init__()
        self.username = username
        self.password = password
        self.target_account = target_account
        self.max_followers = max_followers
        self.is_running = True

    def run(self):
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            
            # Login
            self.progress.emit("🔄 Logging in to Instagram...")
            driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(5)
            
            driver.find_element(By.NAME, 'username').send_keys(self.username)
            driver.find_element(By.NAME, 'password').send_keys(self.password + Keys.RETURN)
            time.sleep(5)
            
            # Navigate to target account
            self.progress.emit(f"🔍 Navigating to {self.target_account}'s profile...")
            driver.get(f"https://www.instagram.com/{self.target_account}/")
            time.sleep(3)
            
            # Click on followers
            followers_link = driver.find_element(By.XPATH, "//a[contains(@href, '/followers')]")
            followers_count = int(followers_link.text.split()[0].replace(',', ''))
            self.progress.emit(f"📊 Found {followers_count} followers")
            
            followers_link.click()
            time.sleep(3)
            
            # Scroll and collect followers
            followers = []
            last_height = driver.execute_script("return document.querySelector('div[role=\"dialog\"]').scrollHeight")
            scroll_count = 0
            
            while len(followers) < min(self.max_followers, followers_count) and self.is_running:
                # Get follower usernames
                follower_elements = driver.find_elements(By.XPATH, "//div[@role='dialog']//a[contains(@href, '/')]")
                new_followers = 0
                
                for element in follower_elements:
                    username = element.get_attribute('href').split('/')[-2]
                    if username and username not in followers:
                        followers.append(username)
                        new_followers += 1
                        if len(followers) >= self.max_followers:
                            break
                
                # Update progress
                progress_percent = int((len(followers) / min(self.max_followers, followers_count)) * 100)
                self.progress_update.emit(progress_percent)
                self.progress.emit(f"⏳ Progress: {len(followers)}/{min(self.max_followers, followers_count)} followers scraped ({progress_percent}%)")
                
                if new_followers == 0:
                    scroll_count += 1
                    if scroll_count >= 3:  # If no new followers found after 3 scrolls, break
                        self.progress.emit("⚠️ No new followers found after multiple scrolls. Stopping...")
                        break
                else:
                    scroll_count = 0
                
                # Scroll
                dialog = driver.find_element(By.XPATH, "//div[@role='dialog']")
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog)
                time.sleep(2)
                
                new_height = driver.execute_script("return document.querySelector('div[role=\"dialog\"]').scrollHeight")
                if new_height == last_height:
                    self.progress.emit("⚠️ Reached end of followers list")
                    break
                last_height = new_height
            
            driver.quit()
            self.progress.emit(f"✅ Successfully scraped {len(followers)} followers")
            self.followers_found.emit(followers)
            self.finished.emit()
            
        except Exception as e:
            self.progress.emit(f"❌ Error: {str(e)}")
            self.finished.emit()

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
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            
            # Login
            self.progress.emit("Logging in...")
            driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(5)
            
            driver.find_element(By.NAME, 'username').send_keys(self.username)
            driver.find_element(By.NAME, 'password').send_keys(self.password + Keys.RETURN)
            time.sleep(5)
            
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
                
                # Visit profile
                driver.get(f"https://www.instagram.com/{user}/")
                time.sleep(random.uniform(4, 6))
                
                try:
                    if self.action_type == 'follow':
                        button = driver.find_element(By.XPATH, "//button[text()='Follow']")
                        action_text = "Followed"
                    else:
                        button = driver.find_element(By.XPATH, "//button[text()='Following']")
                        button.click()
                        time.sleep(random.uniform(2, 3))
                        button = driver.find_element(By.XPATH, "//button[text()='Unfollow']")
                        action_text = "Unfollowed"
                    
                    button.click()
                    self.progress.emit(f"{action_text} {user}")
                    actions_today += 1
                    actions_this_hour += 1
                except:
                    self.progress.emit(f"Could not {self.action_type} {user}")
                
                delay = random.uniform(self.min_delay, self.max_delay)
                self.progress.emit(f"Waiting {int(delay)} seconds before next attempt...")
                time.sleep(delay)
            
            driver.quit()
            self.finished.emit()
            
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")
            self.finished.emit()

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

    def update_scraper_progress(self, message):
        self.scraper_progress.append(message)
        # Auto-scroll to bottom
        self.scraper_progress.verticalScrollBar().setValue(
            self.scraper_progress.verticalScrollBar().maximum()
        )

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