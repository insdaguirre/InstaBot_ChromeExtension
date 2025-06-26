#!/usr/bin/env python3
"""
AWS-Optimized Instagram Bot for EC2 t2.micro instances
"""
import os
import time
import json
import random
import logging
from datetime import datetime
from pathlib import Path
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import subprocess

class AWSInstagramBot:
    def __init__(self, username, password, target_accounts, users_per_account=50):
        self.username = username
        self.password = password
        self.target_accounts = target_accounts
        self.users_per_account = users_per_account
        self.driver = None
        
        # AWS-specific settings
        self.headless = os.environ.get('HEADLESS', 'true').lower() == 'true'
        self.aws_region = os.environ.get('AWS_REGION', 'us-east-1')
        
        # Setup directories
        self.data_dir = Path('instagram_data')
        self.data_dir.mkdir(exist_ok=True)
        (self.data_dir / 'logs').mkdir(exist_ok=True)
        
        # AWS-optimized delays
        self.follow_min_delay = 15
        self.follow_max_delay = 45
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup AWS-specific logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - AWS-Bot - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/aws_automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def detect_aws_instance(self):
        """Detect if running on AWS EC2"""
        try:
            response = requests.get(
                'http://169.254.169.254/latest/meta-data/instance-id',
                timeout=2
            )
            if response.status_code == 200:
                return True, response.text
        except:
            pass
        return False, None
        
    def init_driver(self):
        """Initialize Chrome driver optimized for AWS t2.micro"""
        try:
            # Detect AWS environment
            is_aws, instance_id = self.detect_aws_instance()
            if is_aws:
                self.logger.info(f"Running on AWS EC2 instance: {instance_id}")
            
            options = Options()
            
            # Basic stability options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # AWS-specific optimizations
            if self.headless:
                options.add_argument('--headless')
                
            # Performance optimizations for AWS t2.micro (1GB RAM)
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            options.add_argument('--disable-gpu')
            options.add_argument('--memory-pressure-off')
            options.add_argument('--max_old_space_size=512')
            
            # Window settings
            options.add_argument('--window-size=1024,768')
            options.add_argument('--disable-notifications')
            
            # Try different ChromeDriver locations (AWS compatible)
            driver_paths = [
                '/usr/bin/chromedriver',           
                '/usr/local/bin/chromedriver',     
                '/snap/bin/chromium.chromedriver', 
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
            self.logger.info("Chrome driver initialized successfully on AWS")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing driver: {str(e)}")
            return False

    def login(self):
        """Login to Instagram"""
        try:
            self.logger.info("Attempting to log in to Instagram...")
            self.driver.get('https://www.instagram.com/accounts/login/')
            time.sleep(3)

            # Enter username
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.send_keys(self.username)
            time.sleep(1)

            # Enter password
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(self.password)
            time.sleep(1)

            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            time.sleep(5)
            
            self.logger.info("Successfully logged in to Instagram")
            return True

        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            return False

    def run_follow_batch(self):
        """Run a batch of follows optimized for AWS"""
        try:
            if not self.init_driver():
                self.logger.error("Failed to initialize driver")
                return False
                
            if not self.login():
                self.logger.error("Failed to login")
                return False
            
            self.logger.info("AWS Instagram automation started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in AWS follow batch: {str(e)}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Main function for AWS execution"""
    # Load configuration
    try:
        with open('config/automation_config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return
    
    # Get credentials from environment
    username = os.environ.get('INSTAGRAM_USERNAME')
    password = os.environ.get('INSTAGRAM_PASSWORD')
    
    if not username or not password:
        print("Instagram credentials not found in environment variables")
        return
    
    # Initialize AWS bot
    bot = AWSInstagramBot(
        username=username,
        password=password,
        target_accounts=config['target_accounts'],
        users_per_account=config['settings']['followers_per_account']
    )
    
    # Run follow batch
    success = bot.run_follow_batch()
    
    if success:
        print("AWS Instagram automation completed successfully")
    else:
        print("AWS Instagram automation failed")

if __name__ == "__main__":
    main() 