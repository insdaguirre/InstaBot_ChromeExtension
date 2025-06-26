#!/usr/bin/env python3
"""
Fast Parallel Instagram Unfollow Bot
Optimized for 6-core parallel processing with minimal delays
"""

import threading
import concurrent.futures
import time
import random
import json
import csv
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import queue
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FastUnfollowBot:
    def __init__(self, username, password, max_workers=6):
        self.username = username
        self.password = password
        self.max_workers = max_workers
        
        # Fixed optimal delays for maximum speed while staying safe
        self.min_delay = 2  # Very fast for unfollowing
        self.max_delay = 4
        self.results_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        
    def create_optimized_driver(self):
        """Create a fast, optimized Chrome driver"""
        options = Options()
        
        # Performance optimizations
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')  # Speed up loading
        options.add_argument('--disable-javascript')  # Disable non-essential JS
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        
        # Memory optimizations
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=4096')
        
        # Network optimizations
        options.add_argument('--aggressive-cache-discard')
        options.add_argument('--disable-background-networking')
        
        # Window settings for speed
        options.add_argument('--window-size=1024,768')
        
        # User agent
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        # Disable automation detection
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(3)  # Shorter implicit wait
        
        # Remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def fast_login(self, driver):
        """Fast login with minimal waits"""
        try:
            driver.get('https://www.instagram.com/accounts/login/')
            
            # Wait for username field and enter credentials
            username_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.send_keys(self.username)
            
            password_input = driver.find_element(By.NAME, "password")
            password_input.send_keys(self.password)
            
            # Click login
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Quick verification
            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Home']"))
            )
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def fast_unfollow_user(self, driver, username):
        """Ultra-optimized unfollow with enhanced reliability"""
        try:
            start_time = time.time()
            
            # Navigate to profile
            driver.get(f'https://www.instagram.com/{username}/')
            
            # Quick page load check
            WebDriverWait(driver, 3).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            if "Sorry, this page isn't available" in driver.page_source:
                return False, f"Profile {username} doesn't exist"
            
            # Enhanced relationship button detection
            relationship_button = None
            button_text = None
            
            # Fast multi-attempt detection
            for attempt in range(2):
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    try:
                        if button.is_displayed() and button.is_enabled():
                            text = button.text.strip().lower()
                            if text in ['following', 'requested']:
                                relationship_button = button
                                button_text = text
                                break
                            elif text in ['follow', 'follow back']:
                                return False, f"Not following {username}"
                    except:
                        continue
                
                if relationship_button:
                    break
                elif attempt == 0:
                    time.sleep(0.3)  # Ultra-brief wait
            
            if not relationship_button:
                return False, f"No relationship button found for {username}"
            
            # Ultra-fast clicking with fallbacks
            try:
                # Ensure visibility
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", relationship_button)
                time.sleep(0.1)
                
                # Try click methods
                try:
                    relationship_button.click()
                except:
                    driver.execute_script("arguments[0].click();", relationship_button)
            except:
                return False, f"Failed to click relationship button for {username}"
            
            # Minimal menu wait with early detection
            menu_detected = False
            for wait_time in [0.2, 0.4]:
                time.sleep(wait_time)
                
                # Quick scan for menu items
                elements = (
                    driver.find_elements(By.TAG_NAME, "button") + 
                    driver.find_elements(By.CSS_SELECTOR, "div[role='button']")
                )
                
                for element in elements:
                    try:
                        if element.is_displayed():
                            text = element.text.strip().lower()
                            if any(term in text for term in ['unfollow', 'cancel']):
                                menu_detected = True
                                break
                    except:
                        continue
                
                if menu_detected:
                    break
            
            # Enhanced unfollow option detection
            action_button = None
            search_terms = ['cancel request', 'cancel', 'unfollow'] if 'request' in button_text else ['unfollow']
            
            # Get fresh element list
            clickable_elements = (
                driver.find_elements(By.TAG_NAME, "button") + 
                driver.find_elements(By.CSS_SELECTOR, "div[role='button']")
            )
            
            # Prioritized search: exact matches first
            for priority_search in [True, False]:
                for element in clickable_elements:
                    try:
                        if element.is_displayed() and element.is_enabled():
                            element_text = element.text.strip().lower()
                            
                            for term in search_terms:
                                if priority_search:
                                    # Exact match
                                    if term == element_text:
                                        action_button = element
                                        break
                                else:
                                    # Partial match with length constraint
                                    if term in element_text and len(element_text) < 25:
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
                
                # Ultra-fast action clicking
                try:
                    action_button.click()
                except:
                    try:
                        driver.execute_script("arguments[0].click();", action_button)
                    except:
                        return False, f"Failed to click unfollow option for {username}"
                
                time.sleep(0.15)  # Minimal confirmation wait
                
                # Fast confirmation handling
                if 'unfollow' in action_text.lower():
                    try:
                        confirm_elements = driver.find_elements(By.TAG_NAME, "button")
                        for elem in confirm_elements:
                            try:
                                if elem.is_displayed() and 'unfollow' in elem.text.lower():
                                    elem.click()
                                    break
                            except:
                                continue
                    except:
                        pass
                
                elapsed = time.time() - start_time
                action_word = "cancelled request" if 'request' in button_text else "unfollowed"
                return True, f"Successfully {action_word} {username} ({elapsed:.1f}s)"
            else:
                return False, f"Could not find unfollow option for {username}"
                
        except Exception as e:
            return False, f"Error processing {username}: {str(e)}"
    

    
    def worker_thread(self, usernames_chunk, worker_id):
        """Worker thread that processes a chunk of usernames"""
        driver = None
        results = []
        
        try:
            # Create driver and login
            driver = self.create_optimized_driver()
            
            if not self.fast_login(driver):
                self.progress_queue.put(f"❌ Worker {worker_id}: Login failed")
                return []
            
            self.progress_queue.put(f"✅ Worker {worker_id}: Logged in successfully")
            
            # Process each username in the chunk
            for i, username in enumerate(usernames_chunk, 1):
                try:
                    success, message = self.fast_unfollow_user(driver, username)
                    
                    if success:
                        results.append(username)
                        self.progress_queue.put(f"✅ Worker {worker_id} ({i}/{len(usernames_chunk)}): {message}")
                    else:
                        self.progress_queue.put(f"❌ Worker {worker_id} ({i}/{len(usernames_chunk)}): {message}")
                    
                    # Minimal delay between actions
                    if i < len(usernames_chunk):  # Don't delay after last item
                        delay = random.uniform(self.min_delay, self.max_delay)
                        time.sleep(delay)
                        
                except Exception as e:
                    self.progress_queue.put(f"❌ Worker {worker_id}: Error with {username}: {str(e)}")
            
            self.progress_queue.put(f"🎉 Worker {worker_id}: Completed {len(results)}/{len(usernames_chunk)} accounts")
            
        except Exception as e:
            self.progress_queue.put(f"❌ Worker {worker_id}: Critical error: {str(e)}")
            
        finally:
            if driver:
                driver.quit()
        
        return results
    
    def unfollow_accounts_parallel(self, usernames_list):
        """Main method to unfollow accounts in parallel"""
        if not usernames_list:
            return []
        
        # Split usernames into chunks for parallel processing
        chunk_size = max(1, len(usernames_list) // self.max_workers)
        chunks = [usernames_list[i:i + chunk_size] for i in range(0, len(usernames_list), chunk_size)]
        
        print(f"🚀 Starting parallel unfollow with {self.max_workers} workers")
        print(f"📊 Processing {len(usernames_list)} accounts in {len(chunks)} chunks")
        print(f"⚡ Estimated time: {len(usernames_list) * 4 / self.max_workers / 60:.1f} minutes")
        print("=" * 60)
        
        start_time = time.time()
        all_results = []
        
        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all worker tasks
            future_to_worker = {
                executor.submit(self.worker_thread, chunk, i+1): i+1 
                for i, chunk in enumerate(chunks)
            }
            
            # Monitor progress and collect results
            completed_workers = 0
            for future in concurrent.futures.as_completed(future_to_worker):
                worker_id = future_to_worker[future]
                try:
                    worker_results = future.result()
                    all_results.extend(worker_results)
                    completed_workers += 1
                    
                    # Print progress updates from queue
                    while not self.progress_queue.empty():
                        try:
                            message = self.progress_queue.get_nowait()
                            print(message)
                        except queue.Empty:
                            break
                    
                    print(f"🔄 Worker {worker_id} finished ({completed_workers}/{len(chunks)})")
                    
                except Exception as e:
                    print(f"❌ Worker {worker_id} failed: {str(e)}")
        
        # Print any remaining progress messages
        while not self.progress_queue.empty():
            try:
                message = self.progress_queue.get_nowait()
                print(message)
            except queue.Empty:
                break
        
        elapsed_time = time.time() - start_time
        success_rate = len(all_results) / len(usernames_list) * 100 if usernames_list else 0
        
        print("=" * 60)
        print(f"🎯 RESULTS SUMMARY:")
        print(f"   ✅ Successfully processed: {len(all_results)}/{len(usernames_list)} accounts")
        print(f"   📈 Success rate: {success_rate:.1f}%")
        print(f"   ⏱️  Total time: {elapsed_time:.1f} seconds")
        print(f"   🚀 Average per account: {elapsed_time/len(usernames_list):.1f}s")
        print(f"   ⚡ Speed improvement: ~{30//(elapsed_time/len(usernames_list)) if elapsed_time > 0 else 'N/A'}x faster")
        
        return all_results
    
    def load_usernames_from_csv(self, csv_file_path):
        """Load usernames from CSV file"""
        usernames = []
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row and row[0].strip():  # Skip empty rows
                        usernames.append(row[0].strip())
            
            print(f"📁 Loaded {len(usernames)} usernames from {csv_file_path}")
            return usernames
            
        except Exception as e:
            print(f"❌ Error loading CSV file: {str(e)}")
            return []
    
    def save_results_to_csv(self, successful_unfollows, output_file=None):
        """Save results to CSV file"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"unfollow_results_{timestamp}.csv"
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Username', 'Status', 'Timestamp'])
                for username in successful_unfollows:
                    writer.writerow([username, 'Unfollowed', datetime.now().isoformat()])
            
            print(f"💾 Results saved to {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Error saving results: {str(e)}")
            return None

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fast Parallel Instagram Unfollow Bot')
    parser.add_argument('--csv', required=True, help='CSV file with usernames to unfollow')
    parser.add_argument('--username', required=True, help='Your Instagram username')
    parser.add_argument('--password', required=True, help='Your Instagram password')
    parser.add_argument('--workers', type=int, default=6, help='Number of parallel workers (default: 6)')
    
    args = parser.parse_args()
    
    # Create bot instance (delays are now automatically optimized)
    bot = FastUnfollowBot(
        username=args.username,
        password=args.password,
        max_workers=args.workers
    )
    
    # Load usernames from CSV
    usernames = bot.load_usernames_from_csv(args.csv)
    if not usernames:
        print("❌ No valid usernames found in CSV file")
        return
    
    # Execute parallel unfollow
    successful_unfollows = bot.unfollow_accounts_parallel(usernames)
    
    # Save results
    if successful_unfollows:
        bot.save_results_to_csv(successful_unfollows)
    
    print(f"\n🎉 Process completed! Check the results CSV file for details.")

if __name__ == "__main__":
    main() 